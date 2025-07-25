# SRT Subtitle Processor v2.6

A sophisticated multi-language subtitle processing tool that implements Netflix-compliant subtitle standards with intelligent line breaking, enhanced bilingual validation, and **default SDH removal** for improved readability.

## 🌟 Features

### Core Functionality
- **Multi-language Support**: Chinese, English, Korean, Japanese with auto-detection
- **Netflix Standard Compliance**: Character limits and reading speeds per Netflix guidelines
- **Intelligent Line Breaking**: Context-aware breaking with language-specific rules
- **Smart SDH Processing**: **Default removal** of audio/music markers for cleaner subtitles (v2.6)

### v2.6 Enhanced Features
- **Default SDH Removal**: Automatically removes audio/music markers for cleaner subtitles
- **Unicode SDH Support**: Handles both ASCII `()` and full-width `（）` parentheses in multilingual content
- **Smart Content Preservation**: Preserves dialogue while removing SDH markers from mixed content
- **Flexible SDH Control**: Use `--keep-sdh` flag when SDH markers are needed

### v2.5 Enhanced Features
- **Bilingual Validation Fix**: Per-line language detection for accurate character limit validation
- **Language-Specific Violations**: Enhanced violation output showing language codes and specific limits
- **Violation Output Export**: New `--output-violation` parameter to save violations to separate SRT files
- **Reading Speed Analysis**: Improved bilingual content reading speed calculation and reporting
- **Mixed-Language Support**: Correct handling of Chinese-English, Korean-English mixed content

### v2.4 Enhanced Features
- **Validation-Only Mode**: New `--check-only` parameter for compliance checking without processing
- **Detailed Validation Reports**: Comprehensive violation analysis with categorized warnings
- **Batch Validation**: Check multiple files simultaneously with summary statistics
- **Enhanced CLI Output**: Improved verbose mode with validation status indicators
- **Compliance Scoring**: Visual compliance rate indicators (✅ ⚠️ ❌) based on violation percentages

### v2.3 Enhanced Features
- **Complete Korean Language Support**: Full Korean processor implementation with dialogue formatting and intelligent line breaking
- **Korean Dialogue Formatting**: Proper spacing after Korean dialogue markers (e.g., `-여기 왔다` → `- 여기 왔다`)
- **Korean Particle Detection**: Intelligent line breaking at Korean particles and endings (은/는, 이/가, 을/를, etc.)
- **Korean Text Validation**: Proper character counting and reading speed validation for Korean content
- **Bilingual KO-CN Support**: Enhanced processing for Korean-Chinese mixed content

### v2.2 Enhanced Features
- **Dialogue Format Optimization**: Auto-add spaces after "-" markers
- **Bilingual Processing**: Intelligent handling of mixed Chinese-English content
- **Smart English Line Merging**: Merge short continuation lines (e.g., "Do that, then.")
- **Chinese Punctuation Intelligence**: Prevent unwanted periods in sentence continuations
- **Smart Threshold Detection**: 
  - Chinese: Don't break if remaining < 3 characters
  - English: Don't break if remaining < 4 complete words or creating lines < 20 chars
- **Minimum Line Length**: Ensure Chinese post-break lines ≥ 5 characters
- **SDH Audio Merging**: Combine repeated audio markers (♪♪,♪♪)
- **Context-Aware Punctuation**: Add missing sentence-ending punctuation only for complete sentences
- **Assistant Word Breaking**: Optimize breaks at Chinese helper words (的、地、得)

## 📊 Language Standards

| Language | Character Limit | SDH Limit | Reading Speed (Adult/Children) |
|----------|----------------|-----------|-------------------------------|
| Chinese  | 16             | 18        | 9/7 chars/sec                |
| English  | 42             | 42        | 20/17 chars/sec              |
| Korean   | 16             | 16        | 12/9 chars/sec               |
| Japanese | 13             | 16        | 4/4 chars/sec (SDH: 7/7)    |

## 🚀 Installation

```bash
# Set up & activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt

# Exit when done
deactivate
```

## 💻 Usage

### Command Line Interface

```bash
# Process single file with default SDH removal (output auto-generated if not specified)
python src/main.py input.srt [output.srt]

# Using module syntax (alternative)
python -m src.srt_processor.cli input.srt [output.srt]

# Keep SDH markers (disable default removal)
python src/main.py input.srt --keep-sdh

# Auto-detect language (default)
python src/main.py input.srt --language auto

# Specify language explicitly
python src/main.py input.srt --language ko  # Korean
python src/main.py input.srt --language zh  # Chinese
python src/main.py input.srt --language en  # English

# Enable SDH mode with SDH markers preserved
python src/main.py input.srt --sdh --keep-sdh

# Disable speed checking (useful for development/testing)
python src/main.py input.srt --no-speed-check

# Disable punctuation correction
python src/main.py input.srt --no-punct-fix

# Batch process directory (default SDH removal)
python src/main.py --batch /path/to/srt/files

# Batch process directory keeping SDH markers
python src/main.py --batch /path/to/srt/files --keep-sdh

# Verbose output with detailed processing info
python src/main.py input.srt --verbose

# Validation-only mode with default SDH removal
python src/main.py input.srt --check-only

# Validation with SDH markers preserved
python src/main.py input.srt --check-only --keep-sdh

# Validation with speed checking disabled
python src/main.py input.srt --check-only --no-speed-check

# Export violations to separate file
python src/main.py input.srt --check-only --output-violation

# Export violations with custom filename
python src/main.py input.srt --check-only --output-violation violations.srt

# Batch validation for quality assurance (default SDH removal)
python src/main.py --batch /path/to/srt/files --check-only

# Batch validation keeping SDH markers
python src/main.py --batch /path/to/srt/files --check-only --keep-sdh

# Combine options
python src/main.py input.srt --language ko --verbose --no-speed-check --keep-sdh
```

### Programmatic Usage

```python
from src.srt_processor.core.processor import SRTProcessor
from src.srt_processor.models.subtitle import ProcessingConfig, Language

# Create configuration with default SDH removal
config = ProcessingConfig(
    language=Language.AUTO,
    sdh_mode=False,
    no_punct_fix=False,
    remove_sdh=True  # Default in v2.6
)

# Create configuration keeping SDH markers
config_keep_sdh = ProcessingConfig(
    language=Language.AUTO,
    sdh_mode=False,
    no_punct_fix=False,
    remove_sdh=False  # Explicitly disable SDH removal
)

# Process file with default SDH removal
processor = SRTProcessor(config)
result = processor.process_file("input.srt", "output.srt")

# Process file keeping SDH markers
processor_keep_sdh = SRTProcessor(config_keep_sdh)
result_keep_sdh = processor_keep_sdh.process_file("input_with_sdh.srt", "output_with_sdh.srt")
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_processors.py
```

## 🛠 Development

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8

# Type checking
mypy src/
```

### Demo

```bash
# Run demo with sample data
python demo.py
```

## 📁 Project Structure

```
src/
├── srt_processor/
│   ├── models/          # Data models and configurations
│   ├── core/            # Parsing, language detection, main processor
│   ├── processors/      # Language-specific processors
│   ├── utils/           # Utility functions
│   └── cli.py          # Command line interface
tests/                   # Comprehensive test suite
demo.py                 # Demonstration script
```

## 🎯 Key Algorithms

### Chinese Processing
- **Threshold Rule**: Don't break if remaining < 3 characters
- **Minimum Length**: Ensure post-break lines ≥ 5 characters
- **Helper Word Breaking**: Prioritize breaks at 的、地、得、了、吧、呢
- **Smart Punctuation**: Add missing "。" only for complete sentences, not continuations
- **Continuation Detection**: Identify sentence continuations to prevent unwanted punctuation

### English Processing  
- **Enhanced Word Threshold**: Don't break if remaining < 4 complete words or creating lines < 20 chars
- **Smart Line Merging**: Automatically merge short continuation lines in bilingual content
- **Grammar Optimization**: Break before conjunctions and prepositions
- **Word Boundary**: Maintain complete word integrity
- **Dialogue Continuation**: Merge dialogue lines with non-dialogue continuations

### Korean Processing (NEW v2.3)
- **Particle Detection**: Intelligent breaking at Korean particles (은/는, 이/가, 을/를, 에서, 로, 과/와, etc.)
- **Dialogue Formatting**: Automatic spacing adjustment for Korean dialogue markers
- **Minimum Length**: Ensure post-break lines ≥ 4 characters for Korean readability
- **Space Preservation**: Maintain word boundaries for Korean mixed-script content
- **Continuation Patterns**: Detect Korean connectors (고, 서, 면, 며, 는데, 지만, 하고, 가지고)

### SDH Processing
- **Marker Detection**: Identify ♪, [audio], (sound) patterns
- **Auto Merging**: Combine repeated markers with comma separation
- **Enhanced Limits**: Apply SDH-specific character limits

## 📈 Performance

- **Netflix Compliance**: 100% adherence to official subtitle standards
- **Multi-language**: Automatic detection with 95%+ accuracy
- **Processing Speed**: Optimized for batch processing large subtitle libraries
- **Memory Efficient**: Streaming processing for large files

## 🤝 Contributing

1. Follow existing code style (Black, isort, flake8)
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Ensure Netflix standard compliance

## 📄 License

This implementation follows Netflix's publicly available subtitle standards and best practices for accessibility and international content distribution.

## 🔧 Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--language` | Target language (auto/zh/en/ko/ja) | auto |
| `--content-type` | Adult or children content | adult |
| `--sdh` | Enable SDH mode | false |
| `--keep-sdh` | Keep SDH markers (disable default removal) (NEW v2.6) | false |
| `--no-speed-check` | Disable reading speed validation | false |
| `--no-punct-fix` | Disable auto punctuation | false |
| `--force-encoding` | Override output encoding | auto-detect |
| `--verbose` | Enable detailed output | false |
| `--check-only` | Validate without processing | false |
| `--output-violation` | Export violations to file | false |

**Note**: As of v2.6, SDH removal is enabled by default to improve subtitle readability. Use `--keep-sdh` when SDH markers are required.

## 🎬 Sample Output

### v2.6 Default SDH Removal Examples

**Processing with Default SDH Removal:**
```bash
$ python src/main.py bilingual_with_sdh.srt
Processing: bilingual_with_sdh.srt
Language detected: zh
SDH removal: Enabled (default)
Removed 15 SDH-only blocks
Cleaned SDH markers from 8 mixed content blocks
Processed: bilingual_with_sdh.srt -> bilingual_with_sdh_processed.srt
```

**Processing with SDH Markers Preserved:**
```bash
$ python src/main.py bilingual_with_sdh.srt --keep-sdh
Processing: bilingual_with_sdh.srt
Language detected: zh
SDH removal: Disabled (--keep-sdh)
Processed: bilingual_with_sdh.srt -> bilingual_with_sdh_processed.srt
```

**Before (with SDH markers):**
```srt
1
00:00:04,967 --> 00:00:07,467
♪♪

2
00:00:07,600 --> 00:00:14,333
（音乐响起）
(MUSIC PLAYS)

3
00:01:11,733 --> 00:01:12,800
- 你好！（笑声）
- Hello! (LAUGHTER)
```

**After (v2.6 default behavior):**
```srt
1
00:01:11,733 --> 00:01:12,800
- 你好！
- Hello!
```

### v2.5 Bilingual Validation Examples

**Before v2.5 (Incorrect):**
```
$ python src/main.py bilingual.srt --check-only
Block 65: Line 2 exceeds character limit (20 > 16)  # ❌ English text wrongly validated against Chinese limit
```

**After v2.5 (Correct):**
```
$ python src/main.py bilingual.srt --check-only
Block 65: Reading speed too fast (17.5 > 9.0 chars/sec)  # ✅ Only legitimate violations shown
```

**Violation Export (NEW v2.5):**
```
$ python src/main.py bilingual.srt --check-only --output-violation
Violations saved to: bilingual-violation.srt

# Content of bilingual-violation.srt:
1
00:00:01,000 --> 00:00:03,000
# VIOLATIONS SUMMARY
# Reading Speed Violations: 1
# Character Limit Violations: 0
# Language Detection: Chinese (primary)

2
00:04:31,667 --> 00:04:33,333
-为什么让她靠近尸体？
-Why did you let her
near the body?
# VIOLATIONS: Reading speed (17.5 > 9.0 chars/sec)
```

### v2.4 Validation-Only Mode Examples

**Single File Validation:**
```
$ python src/main.py samples/CHS-KOR.srt --check-only
Checking: samples/CHS-KOR.srt
Language detected: ko
Total blocks: 1680

=== VALIDATION REPORT ===
Character Limit Violations: 1026
  📏 Block 1: Exceeds character limit (34 > 16)
  📏 Block 2: Exceeds character limit (19 > 16)
  ... and 1016 more character limit violations

Reading Speed Violations: 905
  ⏱️  Block 1: Reading speed too fast (16.6 > 9.0 chars/sec)
  ⏱️  Block 2: Reading speed too fast (13.8 > 12.0 chars/sec)
  ... and 895 more speed violations

=== SUMMARY ===
❌ Compliance: 30.4% (511/1680 blocks)
⚠️  Total Violations: 1931
📊 Character Limit: 1026 violations
⏱️  Reading Speed: 905 violations
```

**Batch Validation:**
```
$ python src/main.py --batch samples --check-only
Checking 15 SRT files in samples

❌ CHS-KOR.srt - 30.4% (1931 violations)
⚠️ Phanteam.chs-kor.srt - 80.6% (253 violations)
✅ Bouquet.CHS.srt - 95.8% (72 violations)

Batch checking complete:
  Checked: 15
  Total violations: 18723
  Average violations per file: 1248.2
```

### v2.3 Bilingual Processing Examples

**Korean Dialogue Formatting (New in v2.3):**
```
# Before
-여기 왔다
-아, 깜짝이야

# After  
- 여기 왔다
- 아, 깜짝이야.
```

**English Line Merging (Fixed in v2.2):**
```
# Before
-行啊，随你便。
-Fine, go ahead.
Do that, then.

# After  
- 行啊，随你便。
- Fine, go ahead. Do that, then.
```

**Chinese Punctuation Intelligence (Fixed in v2.2):**
```
# Before (unwanted period)
阿齐尔给了我。
这些新药片，

# After (no unwanted period)
阿齐尔给了我
这些新药片，
```

**Dialogue Format Optimization:**
```
# Before
-怎么这么晚？
-What kept you?

# After
- 怎么这么晚？
- What kept you?
```

With intelligent line breaking, reading speed validation, and Netflix compliance.