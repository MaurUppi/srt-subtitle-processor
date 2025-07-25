"""Main SRT processing engine that coordinates all components."""

from typing import Dict, Type

from ..models.subtitle import Language, ProcessingConfig, SRTDocument, SubtitleBlock
from ..processors.chinese import ChineseProcessor
from ..processors.english import EnglishProcessor
from ..processors.korean import KoreanProcessor
from .language_detector import LanguageDetector
from .parser import SRTParser


class SRTProcessor:
    """Main SRT processing engine."""

    def __init__(self, config: ProcessingConfig) -> None:
        """Initialize the SRT processor.

        Args:
            config: Processing configuration
        """
        self.config = config
        self.parser = SRTParser()
        self.language_detector = LanguageDetector()

        # Initialize language processors
        self.processors: Dict[Language, Type] = {
            Language.CHINESE: ChineseProcessor,
            Language.ENGLISH: EnglishProcessor,
            Language.KOREAN: KoreanProcessor,
            # Japanese processor would go here
        }

    def process_file(self, input_path: str, output_path: str) -> SRTDocument:
        """Process an SRT file from input to output.

        Args:
            input_path: Path to input SRT file
            output_path: Path to output SRT file

        Returns:
            Processed SRT document
        """
        # Parse the input file
        document = self.parser.parse_file(
            input_path, encoding=self.config.force_encoding
        )

        # Detect language if auto mode
        if self.config.language == Language.AUTO:
            detected_language = self.language_detector.detect_language(document)
            document.detected_language = detected_language
            # Update config language for processing
            self.config.language = detected_language
        else:
            document.detected_language = self.config.language

        # Detect individual block languages for mixed content
        self.language_detector.detect_block_languages(document)

        # Remove SDH blocks and clean content if requested
        if self.config.remove_sdh:
            document = document.remove_sdh_blocks_and_clean_content()

        # Process all subtitle blocks
        processed_document = self._process_document(document)

        # Write output file
        self.parser.write_file(
            processed_document, output_path, encoding=self.config.force_encoding
        )

        return processed_document

    def check_file_only(self, input_path: str) -> dict:
        """Check subtitle file for compliance without processing.

        Args:
            input_path: Path to input SRT file

        Returns:
            Detailed validation results dictionary with violation blocks
        """
        # Parse the input file
        document = self.parser.parse_file(
            input_path, encoding=self.config.force_encoding
        )

        # Detect language if auto mode
        if self.config.language == Language.AUTO:
            detected_language = self.language_detector.detect_language(document)
            document.detected_language = detected_language
            # Update config language for validation
            self.config.language = detected_language
        else:
            document.detected_language = self.config.language

        # Detect individual block languages for mixed content
        self.language_detector.detect_block_languages(document)

        # Remove SDH blocks and clean content if requested (for validation on final result)
        if self.config.remove_sdh:
            document = document.remove_sdh_blocks_and_clean_content()

        # Perform validation without processing
        validation_results = self.validate_document(document)

        # Add additional information for check-only mode
        validation_results["input_file"] = input_path
        validation_results["detected_language"] = (
            document.detected_language.value
            if document.detected_language
            else "unknown"
        )
        validation_results["original_document"] = document

        # Extract violation blocks with detailed information
        violation_blocks = self._extract_violation_blocks(
            document, validation_results["warnings"]
        )
        validation_results["violation_blocks"] = violation_blocks

        # Categorize warnings by type
        char_warnings = []
        speed_warnings = []

        for warning in validation_results["warnings"]:
            if "character limit" in warning:
                char_warnings.append(warning)
            elif "Reading speed" in warning:
                speed_warnings.append(warning)

        validation_results["character_warnings"] = char_warnings
        validation_results["speed_warnings"] = speed_warnings

        # Calculate compliance rate
        total_blocks = validation_results["statistics"]["total_blocks"]
        warning_blocks = len(
            set(
                warning.split(":")[0]
                for warning in validation_results["warnings"]
                if "Block" in warning
            )
        )
        compliant_blocks = total_blocks - warning_blocks
        compliance_rate = (
            (compliant_blocks / total_blocks * 100) if total_blocks > 0 else 0
        )

        validation_results["compliance_rate"] = compliance_rate
        validation_results["compliant_blocks"] = compliant_blocks

        return validation_results

    def _extract_violation_blocks(self, document: SRTDocument, warnings: list) -> list:
        """Extract original subtitle blocks that have violations.

        Args:
            document: Original parsed document
            warnings: List of validation warning strings

        Returns:
            List of dictionaries with block data and associated violations
        """
        import re

        # Group warnings by block index
        block_violations = {}

        for warning in warnings:
            # Extract block index from warning: "Block 10: Exceeds character limit..."
            match = re.match(r"Block (\d+):", warning)
            if match:
                block_idx = int(match.group(1))
                if block_idx not in block_violations:
                    block_violations[block_idx] = []
                block_violations[block_idx].append(warning)

        # Build violation blocks list
        violation_blocks = []
        for block_idx, block_warnings in block_violations.items():
            # Find the corresponding block (SRT indices are 1-based)
            block = None
            for doc_block in document.blocks:
                if doc_block.index == block_idx:
                    block = doc_block
                    break

            if block:
                violation_blocks.append(
                    {
                        "block": block,
                        "violations": block_warnings,
                        "violation_types": self._categorize_violation_types(
                            block_warnings
                        ),
                    }
                )

        # Sort by block index for consistent output
        violation_blocks.sort(key=lambda x: x["block"].index)

        return violation_blocks

    def _categorize_violation_types(self, warnings: list) -> list:
        """Categorize violation types from warning messages.

        Args:
            warnings: List of warning strings for a block

        Returns:
            List of violation type strings
        """
        violation_types = []
        for warning in warnings:
            if "character limit" in warning:
                violation_types.append("character_limit")
            elif "Reading speed" in warning:
                violation_types.append("reading_speed")
        return list(set(violation_types))  # Remove duplicates

    def _process_document(self, document: SRTDocument) -> SRTDocument:
        """Process all blocks in a document.

        Args:
            document: Input SRT document

        Returns:
            Processed SRT document with updated blocks
        """
        processed_blocks = []

        for block in document.blocks:
            # Check if this is a bilingual block
            if self._is_bilingual_block(block):
                processed_block = self._process_bilingual_block(block)
            else:
                # Determine which processor to use for this block
                block_language = (
                    block.language or document.detected_language or Language.ENGLISH
                )

                # Get appropriate processor
                processor_class = self.processors.get(block_language)
                if processor_class:
                    processor = processor_class(self.config)
                    processed_block = processor.process_block(block)
                else:
                    # No specific processor available, use as-is
                    processed_block = block

            processed_blocks.append(processed_block)

        # Create new document with processed blocks
        processed_document = SRTDocument(
            blocks=processed_blocks,
            source_file=document.source_file,
            detected_language=document.detected_language,
            encoding=document.encoding,
        )

        return processed_document

    def _is_bilingual_block(self, block: SubtitleBlock) -> bool:
        """Check if a block contains multiple languages.

        Args:
            block: Subtitle block to check

        Returns:
            True if block contains multiple languages
        """
        if len(block.lines) < 2:
            return False

        languages = set()
        for line in block.lines:
            if line.strip():
                line_language = self.language_detector.detect_line_language(line)
                languages.add(line_language)

                # If we find more than one language, it's bilingual
                if len(languages) > 1:
                    return True

        return False

    def _process_bilingual_block(self, block: SubtitleBlock) -> SubtitleBlock:
        """Process a bilingual block by handling each line with appropriate processor.

        Args:
            block: Bilingual subtitle block

        Returns:
            Processed subtitle block
        """
        processed_lines = []

        # Group consecutive lines by language for better processing
        i = 0
        while i < len(block.lines):
            line = block.lines[i]
            if not line.strip():
                processed_lines.append(line)
                i += 1
                continue

            # Detect language for this line
            line_language = self.language_detector.detect_line_language(line)

            # Collect consecutive lines of the same language
            consecutive_lines = [line]
            j = i + 1
            while j < len(block.lines):
                next_line = block.lines[j]
                if not next_line.strip():
                    j += 1
                    continue
                next_language = self.language_detector.detect_line_language(next_line)
                if next_language == line_language:
                    consecutive_lines.append(next_line)
                    j += 1
                else:
                    break

            # Process the group of consecutive lines
            processor_class = self.processors.get(line_language)
            if processor_class:
                # Create a temporary block for processing the consecutive lines
                temp_block = SubtitleBlock(
                    index=block.index,
                    time_code=block.time_code,
                    lines=consecutive_lines,
                    language=line_language,
                    is_sdh=block.is_sdh,
                )

                # Create temporary config with the line's language
                from dataclasses import replace

                temp_config = replace(self.config, language=line_language)

                processor = processor_class(temp_config)
                processed_temp_block = processor.process_block(temp_block)
                processed_lines.extend(processed_temp_block.lines)
            else:
                # No processor available, use lines as-is
                processed_lines.extend(consecutive_lines)

            # Move to the next unprocessed line
            i = j

        # Create new block with processed lines
        return SubtitleBlock(
            index=block.index,
            time_code=block.time_code,
            lines=processed_lines,
            language=block.language,
            is_sdh=block.is_sdh,
        )

    def validate_document(self, document: SRTDocument) -> Dict[str, any]:
        """Validate a processed document for compliance.

        Args:
            document: Document to validate

        Returns:
            Validation results
        """
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "statistics": {},
        }

        # Validate each block
        for i, block in enumerate(document.blocks):
            block_language = (
                block.language or document.detected_language or Language.ENGLISH
            )

            # Get appropriate processor for validation
            processor_class = self.processors.get(block_language)
            if processor_class:
                processor = processor_class(self.config)

                # Character limit validation (per line with individual language detection)
                for line_idx, line in enumerate(block.lines):
                    # Skip empty lines or lines with only whitespace
                    if not line.strip():
                        continue

                    # Detect language for each line individually for bilingual support
                    line_language = self.language_detector.detect_line_language(line)
                    char_limit = self.config.get_character_limit(line_language)
                    line_char_count = len(line)

                    if line_char_count > char_limit:
                        validation_results["warnings"].append(
                            f"Block {block.index}: Line {line_idx + 1} exceeds character limit "
                            f"({line_char_count} > {char_limit} {line_language.value})"
                        )

                # Reading speed validation
                if not self.config.no_speed_check:
                    if not processor.validate_reading_speed(block):
                        speed_limit = self.config.get_reading_speed_limit(
                            block_language
                        )
                        actual_speed = block.get_reading_speed()
                        validation_results["warnings"].append(
                            f"Block {block.index}: Reading speed too fast "
                            f"({actual_speed:.1f} > {speed_limit} chars/sec)"
                        )

        # Calculate statistics
        validation_results["statistics"] = {
            "total_blocks": len(document.blocks),
            "warning_count": len(validation_results["warnings"]),
            "error_count": len(validation_results["errors"]),
            "detected_language": (
                document.detected_language.value
                if document.detected_language
                else "unknown"
            ),
        }

        # Determine overall validity
        validation_results["valid"] = len(validation_results["errors"]) == 0

        return validation_results
