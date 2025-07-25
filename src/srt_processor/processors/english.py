"""English subtitle processing with intelligent word-based line breaking."""

import re
from typing import List

from ..models.subtitle import ProcessingConfig, SubtitleBlock


class EnglishProcessor:
    """Processor for English subtitles with v2.0 word-based intelligent features."""

    def __init__(self, config: ProcessingConfig) -> None:
        """Initialize English processor.

        Args:
            config: Processing configuration
        """
        self.config = config

        # Connective words and conjunctions for optimal breaking
        self.conjunctions = {
            "and",
            "but",
            "or",
            "nor",
            "for",
            "so",
            "yet",
            "because",
            "since",
            "although",
            "though",
            "while",
            "whereas",
            "however",
            "therefore",
            "moreover",
            "furthermore",
            "nevertheless",
            "nonetheless",
        }

        # Prepositions - prefer breaking before these
        self.prepositions = {
            "in",
            "on",
            "at",
            "by",
            "for",
            "with",
            "from",
            "to",
            "of",
            "about",
            "under",
            "over",
            "through",
            "between",
            "among",
            "during",
            "before",
            "after",
            "above",
            "below",
            "across",
            "around",
            "behind",
            "beside",
        }

        # Sentence ending punctuation
        self.sentence_endings = ".!?"

        # All punctuation marks
        self.punctuation = ".,!?;:\"\\'()[]{}—–-"

        # Dialogue marker pattern
        self.dialogue_pattern = re.compile(r"^-\s*(.*)$")

    def process_block(self, block: SubtitleBlock) -> SubtitleBlock:
        """Process an English subtitle block.

        Args:
            block: Input subtitle block

        Returns:
            Processed subtitle block
        """
        if not block.lines:
            return block

        # Process dialogue formatting first
        processed_lines = self._process_dialogue_format(block.lines)

        # Smart merge if multiple lines (aggressive merging for over-broken content)
        if len(processed_lines) > 1:
            processed_lines = self._smart_merge_lines(processed_lines)

        # Apply intelligent line breaking
        processed_lines = self._apply_line_breaking(processed_lines)

        # Final check: merge overly short lines
        processed_lines = self._merge_short_lines(processed_lines)

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
        """Smart merge multiple lines based on English grammar rules.

        Aggressively merges short lines to fix over-broken content.

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
                    # For dialogue lines, handle dash markers properly
                    if current_line.startswith("- ") and line.startswith("- "):
                        # Both are dialogue - unlikely, keep separate
                        merged_lines.append(current_line)
                        current_line = line
                    elif current_line.startswith("- ") and not line.startswith("- "):
                        # Merge dialogue with continuation
                        current_line += " " + line
                    elif not current_line.startswith("- ") and line.startswith("- "):
                        # Start new dialogue
                        merged_lines.append(current_line)
                        current_line = line
                    else:
                        # Regular merge
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

        More aggressive merging for fixing over-broken English content.

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

        # Don't merge two dialogue lines together
        current_is_dialogue = current.startswith("- ")
        next_is_dialogue = next_line.startswith("- ")
        if current_is_dialogue and next_is_dialogue:
            return False

        # Be more aggressive about merging short lines
        current_length = len(current.strip())
        next_length = len(next_line.strip())

        # Always merge if either line is very short (< 25 chars)
        if current_length < 25 or next_length < 25:
            merged_length = len(current) + 1 + len(next_line)  # +1 for space
            char_limit = self.config.get_character_limit(self.config.language)
            return merged_length <= char_limit

        # Special case: merge if current ends with sentence and next is very short
        if current.rstrip().endswith(".") and next_length < 20:
            merged_length = len(current) + 1 + len(next_line)  # +1 for space
            char_limit = self.config.get_character_limit(self.config.language)
            return merged_length <= char_limit

        # Merge if current line ends with connecting words
        current_words = current.strip().split()
        if current_words and current_words[-1].lower() in {
            "a",
            "an",
            "the",
            "of",
            "in",
            "on",
            "at",
            "to",
            "for",
            "with",
            "by",
            "and",
            "or",
            "but",
        }:
            merged_length = len(current) + 1 + len(next_line)  # +1 for space
            char_limit = self.config.get_character_limit(self.config.language)
            return merged_length <= char_limit

        # Check character count after merging
        merged_length = len(current) + 1 + len(next_line)  # +1 for space
        char_limit = self.config.get_character_limit(self.config.language)

        # Merge if it would fit within limits
        return merged_length <= char_limit

    def _apply_line_breaking(self, lines: List[str]) -> List[str]:
        """Apply intelligent line breaking to English text.

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
        """Break a single line intelligently based on English rules.

        Args:
            line: Line to break

        Returns:
            List of broken lines
        """
        char_limit = self.config.get_character_limit(self.config.language)

        # If line fits within limit, return as-is
        if len(line) <= char_limit:
            return [line]

        # Apply v2.0 word threshold rule: don't break if remaining < 2 complete words
        if not self._should_break_line(line, char_limit):
            return [line]  # Don't break

        # Find best break position
        break_pos = self._find_best_break_position(line, char_limit)

        if break_pos == -1:
            # No good break position found, try word boundary breaking
            break_pos = self._find_word_boundary_break(line, char_limit)

        if break_pos == -1:
            # Still no good position, force break at limit
            break_pos = char_limit

        # Split the line
        first_part = line[:break_pos].rstrip()
        second_part = line[break_pos:].lstrip()

        # Recursively break the second part if needed (with safety check)
        result = [first_part]
        if second_part and len(second_part) < len(line):  # Prevent infinite recursion
            result.extend(self._break_line_intelligently(second_part))

        return result

    def _should_break_line(self, line: str, char_limit: int) -> bool:
        """Determine if line should be broken based on v2.0 word threshold rule.

        Args:
            line: Line to check
            char_limit: Character limit

        Returns:
            True if line should be broken
        """
        if len(line) <= char_limit:
            return False

        # Find where the char limit falls in the text
        remaining_text = line[char_limit:].strip()
        if not remaining_text:
            return False

        # Count complete words in remaining text
        remaining_words = remaining_text.split()

        # Don't break if less than 4 complete words remaining (more conservative)
        if len(remaining_words) < 4:
            return False

        # Also check if breaking would create a very short second line
        # Find the best break position
        break_pos = self._find_best_break_position(line, char_limit)
        if break_pos > 0:
            second_part = line[break_pos:].strip()
            # Don't break if second part would be too short (< 20 chars)
            # This prevents issues like "Do that, then." being on its own line
            if len(second_part) < 20:
                return False

            # Also check word count in second part
            second_part_words = second_part.split()
            if len(second_part_words) < 3:
                return False
        else:
            # If no good break position found, be more conservative
            return False

        return True

    def _find_best_break_position(self, line: str, limit: int) -> int:
        """Find the best position to break an English line.

        Args:
            line: Line to analyze
            limit: Character limit

        Returns:
            Best break position, or -1 if no good position found
        """
        # Look for break positions in order of preference
        search_start = max(0, limit - 20)  # Look within 20 chars of limit
        search_end = min(len(line), limit)

        # 1. Look for punctuation marks (highest priority)
        for i in range(search_end - 1, search_start - 1, -1):
            if i < len(line) and line[i] in ".,!?;:":
                # Break after punctuation
                return i + 1

        # 2. Look for conjunctions (break before them)
        words_before_limit = line[:limit].split()
        for i, word in enumerate(words_before_limit):
            clean_word = word.lower().strip(self.punctuation)
            if clean_word in self.conjunctions:
                # Find position of this word in the original line
                word_pos = line.lower().find(clean_word)
                if search_start <= word_pos <= search_end:
                    return word_pos

        # 3. Look for prepositions (break before them)
        for i, word in enumerate(words_before_limit):
            clean_word = word.lower().strip(self.punctuation)
            if clean_word in self.prepositions:
                # Find position of this word in the original line
                word_pos = line.lower().find(clean_word)
                if search_start <= word_pos <= search_end:
                    return word_pos

        return -1

    def _find_word_boundary_break(self, line: str, limit: int) -> int:
        """Find word boundary break position near the limit.

        Args:
            line: Line to analyze
            limit: Character limit

        Returns:
            Word boundary break position, or -1 if not found
        """
        # Look for spaces near the limit
        search_start = max(0, limit - 15)
        search_end = min(len(line), limit + 5)

        # Find the last space before or near the limit
        for i in range(search_end - 1, search_start - 1, -1):
            if i < len(line) and line[i] == " ":
                return i

        return -1

    def validate_reading_speed(self, block: SubtitleBlock) -> bool:
        """Validate reading speed for English subtitles.

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
        """Get character count for English text.

        Args:
            text: Text to count

        Returns:
            Character count including spaces
        """
        # For English, count all characters including spaces
        return len(text)

    def get_word_count(self, text: str) -> int:
        """Get word count for English text.

        Args:
            text: Text to count

        Returns:
            Number of words
        """
        if not text.strip():
            return 0
        return len(text.split())

    def optimize_line_breaks_for_grammar(self, lines: List[str]) -> List[str]:
        """Optimize line breaks for English grammar rules.

        Args:
            lines: Input lines

        Returns:
            Lines optimized for grammar
        """
        if len(lines) <= 1:
            return lines

        optimized = []

        for line in lines:
            # Check for poor break patterns and fix them
            optimized_line = self._fix_poor_breaks(line)
            optimized.append(optimized_line)

        return optimized

    def _fix_poor_breaks(self, line: str) -> str:
        """Fix poor line breaking patterns in English.

        Args:
            line: Line to fix

        Returns:
            Fixed line
        """
        # This is a placeholder for more sophisticated grammar-based
        # line break optimization that could be added in future versions

        # For now, just return the line as-is
        # Future enhancements could include:
        # - Avoiding breaks between articles and nouns ("a car" -> don't break)
        # - Avoiding breaks between first and last names
        # - Keeping phrasal verbs together

        return line

    def _merge_short_lines(self, lines: List[str]) -> List[str]:
        """Merge overly short lines to improve readability.

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
                result.append(lines[i])
                i += 1
                continue

            # Check if we can merge with next line
            if i + 1 < len(lines) and lines[i + 1].strip():
                next_line = lines[i + 1].strip()

                # Check if dialogue markers match
                current_is_dialogue = current_line.startswith("- ")
                next_is_dialogue = next_line.startswith("- ")

                # More aggressive merging conditions:
                should_merge = False

                # 1. If second line is very short (< 20 chars)
                if len(next_line) < 20:
                    should_merge = True

                # 2. If current line is short (< 25 chars)
                elif len(current_line) < 25:
                    should_merge = True

                # 3. Don't merge two dialogue lines together
                if current_is_dialogue and next_is_dialogue:
                    should_merge = False

                if should_merge:
                    # Try merging
                    merged = None
                    if current_is_dialogue and not next_is_dialogue:
                        # Dialogue line with continuation
                        current_content = current_line[2:].strip()
                        merged = f"- {current_content} {next_line}"
                    elif not current_is_dialogue and next_is_dialogue:
                        # Don't merge non-dialogue with dialogue
                        merged = None
                    else:
                        # Regular merge
                        merged = f"{current_line} {next_line}"

                    char_limit = self.config.get_character_limit(self.config.language)
                    if merged and len(merged) <= char_limit:
                        result.append(merged)
                        i += 2  # Skip next line as it's been merged
                        continue

            result.append(lines[i])
            i += 1

        return result
