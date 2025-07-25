"""Language detection for subtitle content."""

import re
from collections import Counter
from typing import Dict, List

from ..models.subtitle import Language, SRTDocument, SubtitleBlock


class LanguageDetector:
    """Automatic language detection for subtitle content."""

    def __init__(self) -> None:
        """Initialize the language detector."""
        # Unicode ranges for different scripts
        self.chinese_pattern = re.compile(r"[\u4e00-\u9fff]")
        self.korean_pattern = re.compile(r"[\uac00-\ud7af]")
        self.hiragana_pattern = re.compile(r"[\u3040-\u309f]")
        self.katakana_pattern = re.compile(r"[\u30a0-\u30ff]")
        self.ascii_pattern = re.compile(r"[a-zA-Z]")

        # Common punctuation patterns
        self.chinese_punct = re.compile(r"[。！？，：" "（）【】《》]")
        self.korean_punct = re.compile(r"[。！？，：" "（）【】《》]")
        self.japanese_punct = re.compile(r"[。！？、：" "（）【】《》〈〉]")

    def detect_language(self, document: SRTDocument) -> Language:
        """Detect the primary language of a document.

        Args:
            document: SRT document to analyze

        Returns:
            Detected language
        """
        if not document.blocks:
            return Language.ENGLISH  # Default fallback

        # Analyze character distribution across all blocks
        char_counts = self._analyze_character_distribution(document.blocks)

        # Calculate confidence scores for each language
        scores = self._calculate_language_scores(char_counts)

        # Return language with highest confidence
        best_language = max(scores.keys(), key=lambda lang: scores[lang])
        return best_language

    def detect_block_languages(self, document: SRTDocument) -> None:
        """Detect and assign languages to individual blocks.

        Args:
            document: SRT document to analyze (modified in place)
        """
        for block in document.blocks:
            block.language = self._detect_block_language(block)

    def _detect_block_language(self, block: SubtitleBlock) -> Language:
        """Detect language for a single subtitle block.

        Args:
            block: Subtitle block to analyze

        Returns:
            Detected language for this block
        """
        text = block.text
        if not text.strip():
            return Language.ENGLISH

        char_counts = self._count_characters(text)
        scores = self._calculate_language_scores(char_counts)

        return max(scores.keys(), key=lambda lang: scores[lang])

    def detect_line_language(self, line: str) -> Language:
        """Detect language for a single line of text.

        Args:
            line: Text line to analyze

        Returns:
            Detected language for this line
        """
        if not line.strip():
            return Language.ENGLISH

        char_counts = self._count_characters(line)
        scores = self._calculate_language_scores(char_counts)

        return max(scores.keys(), key=lambda lang: scores[lang])

    def _analyze_character_distribution(
        self, blocks: List[SubtitleBlock]
    ) -> Dict[str, int]:
        """Analyze character distribution across all blocks.

        Args:
            blocks: List of subtitle blocks

        Returns:
            Dictionary with character type counts
        """
        combined_text = " ".join(block.text for block in blocks)
        return self._count_characters(combined_text)

    def _count_characters(self, text: str) -> Dict[str, int]:
        """Count different types of characters in text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with character type counts
        """
        return {
            "chinese": len(self.chinese_pattern.findall(text)),
            "korean": len(self.korean_pattern.findall(text)),
            "hiragana": len(self.hiragana_pattern.findall(text)),
            "katakana": len(self.katakana_pattern.findall(text)),
            "ascii": len(self.ascii_pattern.findall(text)),
            "chinese_punct": len(self.chinese_punct.findall(text)),
            "korean_punct": len(self.korean_punct.findall(text)),
            "japanese_punct": len(self.japanese_punct.findall(text)),
            "total_chars": len(text.replace(" ", "")),
        }

    def _calculate_language_scores(
        self, char_counts: Dict[str, int]
    ) -> Dict[Language, float]:
        """Calculate confidence scores for each language.

        Args:
            char_counts: Character type counts

        Returns:
            Dictionary mapping languages to confidence scores
        """
        total_chars = max(char_counts["total_chars"], 1)  # Avoid division by zero

        scores = {
            Language.CHINESE: 0.0,
            Language.ENGLISH: 0.0,
            Language.KOREAN: 0.0,
            Language.JAPANESE: 0.0,
        }

        # Chinese scoring
        chinese_ratio = char_counts["chinese"] / total_chars
        chinese_punct_ratio = char_counts["chinese_punct"] / total_chars
        scores[Language.CHINESE] = chinese_ratio * 10 + chinese_punct_ratio * 2

        # English scoring
        ascii_ratio = char_counts["ascii"] / total_chars
        # Boost score if mostly ASCII with minimal CJK characters
        cjk_total = (
            char_counts["chinese"]
            + char_counts["korean"]
            + char_counts["hiragana"]
            + char_counts["katakana"]
        )
        cjk_ratio = cjk_total / total_chars

        if cjk_ratio < 0.1:  # Less than 10% CJK characters
            scores[Language.ENGLISH] = ascii_ratio * 10
        else:
            scores[Language.ENGLISH] = ascii_ratio * 2

        # Korean scoring
        korean_ratio = char_counts["korean"] / total_chars
        korean_punct_ratio = char_counts["korean_punct"] / total_chars
        scores[Language.KOREAN] = korean_ratio * 10 + korean_punct_ratio * 2

        # Japanese scoring
        hiragana_ratio = char_counts["hiragana"] / total_chars
        katakana_ratio = char_counts["katakana"] / total_chars
        japanese_punct_ratio = char_counts["japanese_punct"] / total_chars

        # Japanese often mixes hiragana, katakana, and kanji (Chinese characters)
        japanese_script_ratio = hiragana_ratio + katakana_ratio
        japanese_with_kanji_ratio = japanese_script_ratio + (chinese_ratio * 0.5)

        scores[Language.JAPANESE] = (
            japanese_with_kanji_ratio * 10 + japanese_punct_ratio * 2
        )

        # Apply minimum thresholds
        min_threshold = 0.01
        for lang in scores:
            if scores[lang] < min_threshold:
                scores[lang] = 0.0

        return scores

    def get_language_statistics(self, document: SRTDocument) -> Dict[str, any]:
        """Get detailed language statistics for a document.

        Args:
            document: SRT document to analyze

        Returns:
            Dictionary with language analysis details
        """
        char_counts = self._analyze_character_distribution(document.blocks)
        scores = self._calculate_language_scores(char_counts)
        detected_language = max(scores.keys(), key=lambda lang: scores[lang])

        # Block-level analysis
        block_languages = []
        for block in document.blocks:
            block_lang = self._detect_block_language(block)
            block_languages.append(block_lang)

        language_distribution = Counter(block_languages)

        return {
            "detected_language": detected_language,
            "confidence_scores": {lang.value: score for lang, score in scores.items()},
            "character_counts": char_counts,
            "block_count": len(document.blocks),
            "language_distribution": {
                lang.value: count for lang, count in language_distribution.items()
            },
            "mixed_language": len(set(block_languages)) > 1,
        }

    def is_mixed_language_document(self, document: SRTDocument) -> bool:
        """Check if document contains multiple languages.

        Args:
            document: SRT document to check

        Returns:
            True if document contains multiple languages
        """
        if len(document.blocks) < 2:
            return False

        languages = set()
        for block in document.blocks:
            lang = self._detect_block_language(block)
            languages.add(lang)

            if len(languages) > 1:
                return True

        return False
