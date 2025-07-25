"""SRT subtitle data models."""

import re
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from typing import List, Optional


class Language(Enum):
    """Supported languages for subtitle processing."""

    AUTO = "auto"
    CHINESE = "zh"
    ENGLISH = "en"
    KOREAN = "ko"
    JAPANESE = "ja"


class ContentType(Enum):
    """Content type for reading speed calculations."""

    ADULT = "adult"
    CHILDREN = "children"


@dataclass
class TimeCode:
    """SRT time code representation."""

    start: timedelta
    end: timedelta

    @classmethod
    def from_srt_time(cls, time_str: str) -> "TimeCode":
        """Parse SRT time format: 00:01:13,933 --> 00:01:18,233"""
        start_str, end_str = time_str.split(" --> ")
        start = cls._parse_time(start_str)
        end = cls._parse_time(end_str)
        return cls(start=start, end=end)

    @staticmethod
    def _parse_time(time_str: str) -> timedelta:
        """Parse individual time: 00:01:13,933"""
        hours, minutes, seconds_ms = time_str.split(":")
        seconds, milliseconds = seconds_ms.split(",")

        return timedelta(
            hours=int(hours),
            minutes=int(minutes),
            seconds=int(seconds),
            milliseconds=int(milliseconds),
        )

    def to_srt_format(self) -> str:
        """Convert back to SRT time format."""
        return f"{self._format_time(self.start)} --> {self._format_time(self.end)}"

    def _format_time(self, td: timedelta) -> str:
        """Format timedelta to SRT time format."""
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        milliseconds = td.microseconds // 1000

        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    @property
    def duration(self) -> timedelta:
        """Get duration of subtitle."""
        return self.end - self.start


@dataclass
class SubtitleBlock:
    """Single subtitle block with timing and text."""

    index: int
    time_code: TimeCode
    lines: List[str]
    language: Optional[Language] = None
    is_sdh: bool = False

    @property
    def text(self) -> str:
        """Get combined text of all lines."""
        return "\n".join(self.lines)

    @property
    def character_count(self) -> int:
        """Get total character count across all lines."""
        return sum(len(line) for line in self.lines)

    def is_dialogue(self) -> bool:
        """Check if this is a dialogue subtitle (starts with -)."""
        return any(line.strip().startswith("-") for line in self.lines)

    def is_sdh_marker(self) -> bool:
        """Check if this contains SDH markers like ♪ or [sound]."""
        sdh_patterns = [r"♪", r"\[.*?\]", r"\(.*?\)", r"【.*?】", r"《.*?》"]
        text = self.text
        return any(re.search(pattern, text) for pattern in sdh_patterns)

    def is_sdh_only_block(self) -> bool:
        """Check if this block contains ONLY SDH markers without dialogue content.

        Returns True for blocks that contain only:
        - Music markers (♪♪, ♪♪♪)
        - Pure audio descriptions [Music plays], [Chuckles]
        - Sound effects [Mobile vibrates], [Knock on door]

        Returns False for blocks that contain dialogue mixed with SDH:
        - "-[ Sobbing ] It's Cal." (dialogue with SDH)
        - "Hello? [Mobile vibrates]" (mixed content)
        - Regular dialogue without SDH markers
        """
        if not self.lines:
            return False

        # Join all lines to analyze the complete text
        full_text = self.text.strip()

        if not full_text:
            return False

        # Enhanced SDH patterns
        music_patterns = [r"^♪+$", r"^🎵+$", r"^🎶+$"]
        audio_description_patterns = [
            r"^\[\s*.*?\s*\]$",  # Pure audio descriptions like [Music plays]
            r"^\(\s*.*?\s*\)$",  # Sound effects in ASCII parentheses
            r"^（\s*.*?\s*）$",  # Sound effects in full-width parentheses
            r"^【\s*.*?\s*】$",  # Chinese-style audio descriptions
            r"^《\s*.*?\s*》$",  # Chinese-style audio descriptions
            r"^［\s*.*?\s*］$",  # Full-width square brackets
            r"^〔\s*.*?\s*〕$",  # Japanese/Chinese square brackets
            r"^〈\s*.*?\s*〉$",  # Angle brackets
        ]

        # Check if entire block is just music markers
        for pattern in music_patterns:
            if re.match(pattern, full_text):
                return True

        # Check if entire block is just audio descriptions
        for pattern in audio_description_patterns:
            if re.match(pattern, full_text):
                return True

        # Check each line individually for pure SDH content
        for line in self.lines:
            line = line.strip()
            if not line:
                continue

            # Skip empty or whitespace-only lines
            if not line:
                continue

            # Check if line contains any actual dialogue content
            # Remove SDH markers and see if meaningful content remains
            temp_line = line

            # Remove music markers
            temp_line = re.sub(r"♪+|🎵+|🎶+", "", temp_line)

            # Remove audio descriptions
            temp_line = re.sub(r"\[.*?\]|\(.*?\)|【.*?】|《.*?》", "", temp_line)

            # Remove dialogue markers and whitespace
            temp_line = re.sub(r"^-\s*", "", temp_line).strip()

            # If anything meaningful remains after removing SDH markers,
            # this is not an SDH-only block
            if temp_line and len(temp_line) > 0:
                return False

        # If we get here, all lines were pure SDH content
        return True

    def clean_sdh_markers(self) -> "SubtitleBlock":
        """Create a new SubtitleBlock with SDH markers removed from dialogue lines.

        This method removes SDH markers like [Chuckles], [Sighs], etc. from lines
        while preserving the actual dialogue content.

        Examples:
        - "[ Sighs ] Hold on." → "Hold on."
        - "-[ Sobbing ] Ruth?" → "- Ruth?"
        - "Whoo! Whoo!\n-[ Chuckles ]" → "Whoo! Whoo!"

        Returns:
            New SubtitleBlock with cleaned lines
        """
        cleaned_lines = []

        for line in self.lines:
            original_line = line.strip()
            if not original_line:
                continue

            # Clean the line by removing SDH markers
            cleaned_line = self._remove_sdh_from_line(original_line)

            # Only add non-empty lines
            if cleaned_line.strip():
                cleaned_lines.append(cleaned_line)

        # Create new block with cleaned lines
        return SubtitleBlock(
            index=self.index,
            time_code=self.time_code,
            lines=cleaned_lines,
            language=self.language,
            is_sdh=self.is_sdh,
        )

    def _remove_sdh_from_line(self, line: str) -> str:
        """Remove SDH markers from a single line while preserving dialogue.

        Args:
            line: Original line text

        Returns:
            Cleaned line with SDH markers removed
        """
        # Enhanced SDH marker patterns with Unicode support
        sdh_patterns = [
            # Audio descriptions in square brackets (ASCII)
            r"\[\s*[^\]]*\s*\]",
            # Audio descriptions in parentheses (ASCII)
            r"\(\s*[^)]*\s*\)",
            # Audio descriptions in full-width parentheses (Unicode/Chinese)
            r"（\s*[^）]*\s*）",
            # Chinese-style audio descriptions
            r"【\s*[^】]*\s*】",
            r"《\s*[^》]*\s*》",
            # Music markers (Unicode and ASCII)
            r"♪+",
            r"🎵+",
            r"🎶+",
            # Additional Unicode brackets/parentheses variants
            r"［\s*[^］]*\s*］",  # Full-width square brackets
            r"〔\s*[^〕]*\s*〕",  # Japanese/Chinese square brackets
            r"〈\s*[^〉]*\s*〉",  # Angle brackets
            r"「\s*[^」]*\s*」",  # Japanese quotation marks (sometimes used for SDH)
        ]

        cleaned = line

        # Remove all SDH patterns iteratively
        for pattern in sdh_patterns:
            cleaned = re.sub(pattern, "", cleaned)

        # Clean up whitespace and formatting
        cleaned = self._clean_whitespace(cleaned)

        return cleaned

    def _clean_whitespace(self, text: str) -> str:
        """Clean up whitespace after SDH removal.

        Args:
            text: Text to clean

        Returns:
            Text with normalized whitespace
        """
        # Remove extra spaces
        cleaned = re.sub(r"\s+", " ", text)

        # Fix dialogue marker spacing: "- text" or "-text" → "- text"
        cleaned = re.sub(r"^-\s*", "- ", cleaned)

        # Fix multiple dashes that can occur after SDH removal: "- -text" → "- text"
        cleaned = re.sub(r"^-\s*-\s*", "- ", cleaned)

        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()

        # Handle case where only dialogue marker remains
        if cleaned == "-":
            return ""

        return cleaned

    def get_reading_speed(self) -> float:
        """Calculate reading speed in characters per second."""
        duration_seconds = self.time_code.duration.total_seconds()
        if duration_seconds <= 0:
            return 0.0
        return self.character_count / duration_seconds


@dataclass
class SRTDocument:
    """Complete SRT document with all subtitle blocks."""

    blocks: List[SubtitleBlock]
    source_file: Optional[str] = None
    detected_language: Optional[Language] = None
    encoding: str = "utf-8"

    @property
    def total_blocks(self) -> int:
        """Get total number of subtitle blocks."""
        return len(self.blocks)

    def get_blocks_by_language(self, language: Language) -> List[SubtitleBlock]:
        """Get all blocks for a specific language."""
        return [block for block in self.blocks if block.language == language]

    def get_dialogue_blocks(self) -> List[SubtitleBlock]:
        """Get all dialogue blocks."""
        return [block for block in self.blocks if block.is_dialogue()]

    def get_sdh_blocks(self) -> List[SubtitleBlock]:
        """Get all SDH marker blocks."""
        return [block for block in self.blocks if block.is_sdh_marker()]

    def get_sdh_only_blocks(self) -> List[SubtitleBlock]:
        """Get all blocks that contain only SDH markers (no dialogue)."""
        return [block for block in self.blocks if block.is_sdh_only_block()]

    def remove_sdh_only_blocks(self) -> "SRTDocument":
        """Create a new document with SDH-only blocks removed and indices resorted.

        This removes blocks that contain ONLY SDH markers (music, sound effects, etc.)
        while preserving dialogue blocks that may contain embedded SDH markers.

        Returns:
            New SRTDocument with filtered blocks and resorted indices
        """
        # Filter out SDH-only blocks
        filtered_blocks = [
            block for block in self.blocks if not block.is_sdh_only_block()
        ]

        # Resort indices sequentially
        for i, block in enumerate(filtered_blocks):
            block.index = i + 1

        # Create new document with filtered blocks
        return SRTDocument(
            blocks=filtered_blocks,
            source_file=self.source_file,
            detected_language=self.detected_language,
            encoding=self.encoding,
        )

    def remove_sdh_blocks_and_clean_content(self) -> "SRTDocument":
        """Create a new document with SDH-only blocks removed and SDH markers cleaned from remaining blocks.

        This performs comprehensive SDH removal:
        1. Removes blocks that contain ONLY SDH markers
        2. Removes SDH markers from mixed content blocks (dialogue + SDH)
        3. Resorts indices sequentially

        Returns:
            New SRTDocument with filtered and cleaned blocks
        """
        processed_blocks = []

        for block in self.blocks:
            # Skip SDH-only blocks entirely
            if block.is_sdh_only_block():
                continue

            # For mixed content blocks, clean SDH markers but preserve dialogue
            cleaned_block = block.clean_sdh_markers()
            if (
                cleaned_block
                and cleaned_block.lines
                and any(line.strip() for line in cleaned_block.lines)
            ):
                processed_blocks.append(cleaned_block)

        # Resort indices sequentially
        for i, block in enumerate(processed_blocks):
            block.index = i + 1

        # Create new document with processed blocks
        return SRTDocument(
            blocks=processed_blocks,
            source_file=self.source_file,
            detected_language=self.detected_language,
            encoding=self.encoding,
        )

    def to_srt_format(self) -> str:
        """Convert document back to SRT format."""
        result = []
        for block in self.blocks:
            result.append(str(block.index))
            result.append(block.time_code.to_srt_format())
            result.extend(block.lines)
            result.append("")  # Empty line between blocks

        return "\n".join(result)


@dataclass
class ProcessingConfig:
    """Configuration for subtitle processing."""

    language: Language = Language.AUTO
    content_type: ContentType = ContentType.ADULT
    sdh_mode: bool = False
    force_encoding: Optional[str] = None
    no_speed_check: bool = False
    no_punct_fix: bool = False
    batch_mode: bool = False
    batch_directory: Optional[str] = None
    check_only: bool = False
    output_violation: Optional[str] = None
    remove_sdh: bool = True

    def get_character_limit(self, language: Language) -> int:
        """Get character limit for specified language."""
        limits = {
            Language.CHINESE: 18 if self.sdh_mode else 16,
            Language.ENGLISH: 42,
            Language.KOREAN: 16,
            Language.JAPANESE: 16 if self.sdh_mode else 13,
        }
        return limits.get(language, 42)

    def get_reading_speed_limit(self, language: Language) -> float:
        """Get reading speed limit in chars/second for language and content type."""
        adult_speeds = {
            Language.CHINESE: 9.0,
            Language.ENGLISH: 20.0,
            Language.KOREAN: 12.0,
            Language.JAPANESE: 7.0 if self.sdh_mode else 4.0,
        }

        children_speeds = {
            Language.CHINESE: 7.0,
            Language.ENGLISH: 17.0,
            Language.KOREAN: 9.0,
            Language.JAPANESE: 7.0 if self.sdh_mode else 4.0,
        }

        speeds = (
            adult_speeds if self.content_type == ContentType.ADULT else children_speeds
        )
        return speeds.get(language, 20.0)
