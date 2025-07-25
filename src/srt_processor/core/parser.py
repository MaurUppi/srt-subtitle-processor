"""SRT file parser for reading and writing subtitle files."""

import re
from pathlib import Path
from typing import List, Optional

try:
    import chardet
except ImportError:
    chardet = None

from ..models.subtitle import SRTDocument, SubtitleBlock, TimeCode


class SRTParseError(Exception):
    """Exception raised when SRT parsing fails."""

    def __init__(self, message: str, line_number: Optional[int] = None) -> None:
        self.line_number = line_number
        super().__init__(f"Line {line_number}: {message}" if line_number else message)


class SRTParser:
    """Parser for SRT subtitle files."""

    def __init__(self) -> None:
        """Initialize the SRT parser."""
        self.time_pattern = re.compile(
            r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})"
        )

    def parse_file(self, file_path: str, encoding: Optional[str] = None) -> SRTDocument:
        """Parse an SRT file and return a SRTDocument.

        Args:
            file_path: Path to the SRT file
            encoding: Optional encoding override

        Returns:
            Parsed SRT document

        Raises:
            SRTParseError: If parsing fails
        """
        path = Path(file_path)
        if not path.exists():
            raise SRTParseError(f"File not found: {file_path}")

        # Detect encoding if not provided
        if encoding is None:
            encoding = self._detect_encoding(path)

        try:
            with open(path, "r", encoding=encoding) as f:
                content = f.read()
        except UnicodeDecodeError as e:
            raise SRTParseError(f"Encoding error with {encoding}: {e}")

        blocks = self._parse_content(content)
        return SRTDocument(blocks=blocks, source_file=str(path), encoding=encoding)

    def parse_content(self, content: str) -> SRTDocument:
        """Parse SRT content from a string.

        Args:
            content: SRT content as string

        Returns:
            Parsed SRT document
        """
        blocks = self._parse_content(content)
        return SRTDocument(blocks=blocks)

    def _detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding using chardet.

        Args:
            file_path: Path to the file

        Returns:
            Detected encoding name
        """
        if chardet is None:
            # Fallback to utf-8 if chardet not available
            return "utf-8"

        with open(file_path, "rb") as f:
            raw_data = f.read()

        result = chardet.detect(raw_data)
        encoding = result.get("encoding", "utf-8")

        # Common encoding fallbacks
        if encoding is None or encoding.lower() in ["ascii"]:
            encoding = "utf-8"

        return encoding

    def _parse_content(self, content: str) -> List[SubtitleBlock]:
        """Parse SRT content into subtitle blocks.

        Args:
            content: Raw SRT content

        Returns:
            List of parsed subtitle blocks

        Raises:
            SRTParseError: If parsing fails
        """
        blocks = []
        lines = content.strip().split("\n")
        current_line = 0

        while current_line < len(lines):
            try:
                block, next_line = self._parse_block(lines, current_line)
                if block:
                    blocks.append(block)
                current_line = next_line
            except Exception as e:
                raise SRTParseError(str(e), current_line + 1)

        return blocks

    def _parse_block(
        self, lines: List[str], start_line: int
    ) -> tuple[Optional[SubtitleBlock], int]:
        """Parse a single subtitle block.

        Args:
            lines: All lines from the file
            start_line: Line index to start parsing from

        Returns:
            Tuple of (parsed block or None, next line index)
        """
        current_line = start_line

        # Skip empty lines
        while current_line < len(lines) and not lines[current_line].strip():
            current_line += 1

        if current_line >= len(lines):
            return None, current_line

        # Parse subtitle index
        index_line = lines[current_line].strip()
        if not index_line.isdigit():
            raise SRTParseError(f"Expected subtitle index, got: {index_line}")

        index = int(index_line)
        current_line += 1

        if current_line >= len(lines):
            raise SRTParseError("Unexpected end of file after index")

        # Parse time code
        time_line = lines[current_line].strip()
        time_match = self.time_pattern.match(time_line)
        if not time_match:
            raise SRTParseError(f"Invalid time format: {time_line}")

        time_code = TimeCode.from_srt_time(time_line)
        current_line += 1

        # Parse subtitle text lines - collect until we find next subtitle block
        text_lines = []

        while current_line < len(lines):
            line = lines[current_line]
            stripped_line = line.strip()

            # Stop if we hit what looks like the next subtitle index (a standalone digit)
            if stripped_line.isdigit() and (current_line + 1 < len(lines)):
                # Check if the next line looks like a timestamp to confirm this is a subtitle index
                next_line = lines[current_line + 1].strip()
                if self.time_pattern.match(next_line):
                    break

            # Add the line to subtitle text
            text_lines.append(line.rstrip())
            current_line += 1

        # Remove trailing empty lines
        while text_lines and not text_lines[-1].strip():
            text_lines.pop()

        if not text_lines:
            raise SRTParseError("No subtitle text found")

        block = SubtitleBlock(index=index, time_code=time_code, lines=text_lines)

        return block, current_line

    def write_file(
        self, document: SRTDocument, output_path: str, encoding: Optional[str] = None
    ) -> None:
        """Write SRT document to file.

        Args:
            document: SRT document to write
            output_path: Output file path
            encoding: Optional encoding override (defaults to document encoding)
        """
        if encoding is None:
            encoding = document.encoding

        content = document.to_srt_format()

        with open(output_path, "w", encoding=encoding) as f:
            f.write(content)

    def validate_srt_format(self, content: str) -> List[str]:
        """Validate SRT format and return list of issues.

        Args:
            content: SRT content to validate

        Returns:
            List of validation errors (empty if valid)
        """
        issues = []
        lines = content.strip().split("\n")
        current_line = 0
        expected_index = 1

        while current_line < len(lines):
            # Skip empty lines
            while current_line < len(lines) and not lines[current_line].strip():
                current_line += 1

            if current_line >= len(lines):
                break

            # Check index
            index_line = lines[current_line].strip()
            if not index_line.isdigit():
                issues.append(
                    f"Line {current_line + 1}: Expected index, got '{index_line}'"
                )
                current_line += 1
                continue

            index = int(index_line)
            if index != expected_index:
                issues.append(
                    f"Line {current_line + 1}: Expected index {expected_index}, got {index}"
                )

            current_line += 1
            expected_index += 1

            if current_line >= len(lines):
                issues.append(f"Line {current_line}: Missing time code after index")
                break

            # Check time code
            time_line = lines[current_line].strip()
            if not self.time_pattern.match(time_line):
                issues.append(
                    f"Line {current_line + 1}: Invalid time format '{time_line}'"
                )

            current_line += 1

            # Check text lines exist
            text_line_count = 0
            while (
                current_line < len(lines)
                and lines[current_line].strip()
                and not lines[current_line].strip().isdigit()
            ):
                text_line_count += 1
                current_line += 1

            if text_line_count == 0:
                issues.append(f"Line {current_line}: No subtitle text found")

        return issues
