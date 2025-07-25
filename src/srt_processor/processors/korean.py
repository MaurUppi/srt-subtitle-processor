"""Korean subtitle processing with intelligent line breaking."""

import re
from typing import List

from ..models.subtitle import ProcessingConfig, SubtitleBlock


class KoreanProcessor:
    """Processor for Korean subtitles with v2.2 intelligent features."""

    def __init__(self, config: ProcessingConfig) -> None:
        """Initialize Korean processor.

        Args:
            config: Processing configuration
        """
        self.config = config

        # Korean punctuation marks
        self.punctuation = "。！？，：；" "''（）【】《》"

        # Korean helper particles and endings for intelligent line breaking
        self.helper_particles = {
            "은",
            "는",
            "이",
            "가",
            "을",
            "를",
            "에",
            "에서",
            "로",
            "으로",
            "와",
            "과",
            "의",
            "도",
            "만",
            "까지",
            "부터",
            "보다",
            "처럼",
            "다",
            "요",
            "죠",
            "네",
            "지",
            "니",
            "까",
            "야",
            "아",
            "어",
            "고",
            "서",
            "면",
            "려고",
            "하고",
            "때문에",
            "가지고",
        }

        # Sentence ending punctuation
        self.sentence_endings = "。！？"

        # Dialogue marker pattern
        self.dialogue_pattern = re.compile(r"^-\s*(.*)$")

    def process_block(self, block: SubtitleBlock) -> SubtitleBlock:
        """Process a Korean subtitle block.

        Args:
            block: Input subtitle block

        Returns:
            Processed subtitle block
        """
        if not block.lines:
            return block

        # Process dialogue formatting first
        processed_lines = self._process_dialogue_format(block.lines)

        # Smart merge if multiple lines
        if len(processed_lines) > 1:
            processed_lines = self._smart_merge_lines(processed_lines)

        # Apply intelligent line breaking
        processed_lines = self._apply_line_breaking(processed_lines)

        # Add missing punctuation if enabled
        if not self.config.no_punct_fix:
            processed_lines = self._add_missing_punctuation(processed_lines)

        # Create new block with processed lines
        new_block = SubtitleBlock(
            index=block.index,
            time_code=block.time_code,
            lines=processed_lines,
            language=block.language,
            is_sdh=block.is_sdh,
        )

        return new_block

    def _process_dialogue_format(self, lines: List[str]) -> List[str]:
        """Process dialogue format by adding spaces after dashes.

        Args:
            lines: Original lines

        Returns:
            Lines with proper dialogue formatting
        """
        processed_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line starts with dash
            match = self.dialogue_pattern.match(line)
            if match:
                content = match.group(1).strip()
                processed_lines.append(f"- {content}")
            else:
                processed_lines.append(line)

        return processed_lines

    def _smart_merge_lines(self, lines: List[str]) -> List[str]:
        """Smart merge multiple lines based on Korean rules.

        Args:
            lines: Input lines

        Returns:
            Merged lines
        """
        if len(lines) <= 1:
            return lines

        merged_lines = []
        current_line = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if we should merge with current line
            if self._should_merge_with_current(current_line, line):
                if current_line:
                    # For Korean, merge with space
                    current_line += " " + line
                else:
                    current_line = line
            else:
                # Start new line
                if current_line:
                    merged_lines.append(current_line)
                current_line = line

        # Add the last line
        if current_line:
            merged_lines.append(current_line)

        return merged_lines

    def _should_merge_with_current(self, current: str, next_line: str) -> bool:
        """Determine if next line should be merged with current.

        Args:
            current: Current line content
            next_line: Next line to consider

        Returns:
            True if lines should be merged
        """
        if not current:
            return False

        # Don't merge if current line ends with sentence punctuation
        if current and current[-1] in self.sentence_endings:
            return False

        # Don't merge dialogue lines with non-dialogue lines
        current_is_dialogue = current.startswith("- ")
        next_is_dialogue = next_line.startswith("- ")
        if current_is_dialogue != next_is_dialogue:
            return False

        # Check character count after merging (include space)
        merged_length = len(current) + 1 + len(next_line)
        char_limit = self.config.get_character_limit(self.config.language)

        # Merge if it would fit within limits
        return merged_length <= char_limit

    def _apply_line_breaking(self, lines: List[str]) -> List[str]:
        """Apply intelligent line breaking to Korean text.

        Args:
            lines: Input lines

        Returns:
            Lines with intelligent breaking applied
        """
        result_lines = []

        for line in lines:
            if not line.strip():
                continue

            broken_lines = self._break_line_intelligently(line)
            result_lines.extend(broken_lines)

        return result_lines

    def _break_line_intelligently(self, line: str) -> List[str]:
        """Break a single line intelligently based on Korean rules.

        Args:
            line: Line to break

        Returns:
            List of broken lines
        """
        char_limit = self.config.get_character_limit(self.config.language)

        # If line fits within limit, return as-is
        if len(line) <= char_limit:
            return [line]

        # Apply threshold rule: don't break if remaining < 3 chars (similar to Chinese)
        remaining_chars = len(line) - char_limit
        if remaining_chars < 3:
            return [line]  # Don't break

        # Find best break position
        break_pos = self._find_best_break_position(line, char_limit)

        if break_pos == -1:
            # No good break position found, force break at limit
            break_pos = char_limit

        # Split the line
        first_part = line[:break_pos].rstrip()
        second_part = line[break_pos:].lstrip()

        # Ensure second part meets minimum length requirement (≥4 chars for Korean)
        if len(second_part) < 4:
            # If second part too short, don't break
            return [line]

        # Recursively break the second part if needed (with safety check)
        result = [first_part]
        if second_part and len(second_part) < len(line):  # Prevent infinite recursion
            result.extend(self._break_line_intelligently(second_part))

        return result

    def _find_best_break_position(self, line: str, limit: int) -> int:
        """Find the best position to break a Korean line.

        Args:
            line: Line to analyze
            limit: Character limit

        Returns:
            Best break position, or -1 if no good position found
        """
        # Look for break positions in order of preference
        search_start = max(0, limit - 8)  # Look within 8 chars of limit
        search_end = min(len(line), limit + 3)  # Don't go too far past limit

        # 1. Look for spaces (word boundaries are important in Korean)
        for i in range(search_end - 1, search_start - 1, -1):
            if i < len(line) and line[i] == " ":
                if i <= limit:
                    return i

        # 2. Look for Korean particles and endings near the limit
        for i in range(search_end - 2, search_start - 1, -1):
            if i >= 0 and i + 2 <= len(line):
                two_char = line[i : i + 2]
                if two_char in self.helper_particles:
                    # Break after the particle
                    if i + 2 <= limit:
                        return i + 2

        # 3. Look for single character particles
        for i in range(search_end - 1, search_start - 1, -1):
            if i < len(line) and line[i] in self.helper_particles:
                # Break after the particle
                if i + 1 <= limit:
                    return i + 1

        # 4. Look for punctuation marks
        for i in range(search_end - 1, search_start - 1, -1):
            if i < len(line) and line[i] in self.punctuation:
                # Break after punctuation
                if i + 1 <= limit:
                    return i + 1

        # 5. No good position found
        return -1

    def _add_missing_punctuation(self, lines: List[str]) -> List[str]:
        """Add missing sentence-ending punctuation only to complete sentences.

        Args:
            lines: Input lines

        Returns:
            Lines with punctuation added where needed
        """
        if not lines:
            return lines

        result_lines = lines.copy()
        last_line = result_lines[-1].strip()

        # Only add punctuation if this appears to be a complete sentence
        # Check if last line needs punctuation and isn't a continuation
        if (
            last_line
            and last_line[-1] not in self.punctuation
            and not last_line.endswith("...")
            and not last_line.startswith("♪")  # Don't add to SDH markers
            and not last_line.endswith(
                ("고", "서", "면", "며", "는데", "지만", "하고")
            )  # Don't add if ends with Korean connectors (continuation)
            and not self._is_line_continuation(
                last_line
            )  # Check if it's a continuation
        ):
            # Add period to last line (Korean often uses 。)
            result_lines[-1] = last_line + "."

        return result_lines

    def _is_line_continuation(self, line: str) -> bool:
        """Check if a line appears to be a continuation of a sentence.

        Args:
            line: Line to check

        Returns:
            True if line appears to be a continuation
        """
        line = line.strip()
        if not line:
            return False

        # Common Korean patterns that suggest continuation:
        continuation_endings = {
            "고",
            "서",
            "면",
            "며",
            "는데",
            "지만",
            "하고",
            "가지고",
            "때문에",
            "하면서",
            "다가",
            "으면서",
            "으니까",
            "니까",
            "하여",
            "해서",
            "에서",
            "으로",
            "로",
            "와",
            "과",
        }

        # Check if line ends with continuation patterns
        for ending in continuation_endings:
            if line.endswith(ending):
                return True

        # Very short lines are likely continuations
        if len(line) < 6:
            return True

        return False

    def validate_reading_speed(self, block: SubtitleBlock) -> bool:
        """Validate reading speed for Korean subtitles.

        Args:
            block: Subtitle block to validate

        Returns:
            True if reading speed is acceptable
        """
        if self.config.no_speed_check:
            return True

        speed_limit = self.config.get_reading_speed_limit(self.config.language)
        actual_speed = block.get_reading_speed()

        return actual_speed <= speed_limit

    def get_character_count(self, text: str) -> int:
        """Get character count for Korean text.

        Args:
            text: Text to count

        Returns:
            Character count
        """
        # For Korean, count characters including spaces as they're important for readability
        return len(text)

    def merge_short_lines(self, lines: List[str]) -> List[str]:
        """Merge lines that are too short (< 5 characters).

        Args:
            lines: Input lines

        Returns:
            Lines with short lines merged
        """
        if len(lines) <= 1:
            return lines

        result = []
        i = 0

        while i < len(lines):
            current_line = lines[i].strip()

            if not current_line:
                i += 1
                continue

            # Check if current line is short and can be merged
            if (
                len(current_line) < 5
                and i + 1 < len(lines)
                and not current_line.endswith(tuple(self.sentence_endings))
            ):
                next_line = lines[i + 1].strip()
                merged = current_line + " " + next_line

                char_limit = self.config.get_character_limit(self.config.language)
                if len(merged) <= char_limit:
                    result.append(merged)
                    i += 2  # Skip next line as it's been merged
                    continue

            result.append(current_line)
            i += 1

        return result
