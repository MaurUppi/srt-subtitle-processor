# SDH Removal Feature Design

Based on analysis of the codebase and sample files, this document outlines the comprehensive SDH removal feature that integrates cleanly with the existing architecture. **As of v2.6, SDH removal is enabled by default** for improved subtitle clarity and readability.

## 📋 Analysis Summary

### SDH Patterns Identified:
- **Music markers**: `♪♪`, `♪♪♪`
- **Audio descriptions**: `[ Mid-tempo music plays ]`, `[ Chuckles ]`, `[ Giggles ]`, `[ Sighs ]`
- **Sound effects**: `[ Mobile vibrates ]`, `[ Knock on door ]`
- **Dialogue with SDH markers**: `-[ Chuckles ]`, `-[ Sobbing ] Ruth?`

### Expected Behavior (v2.6 Default):
- **Remove blocks containing only SDH markers** (music, sounds, audio descriptions) **by default**
- **Preserve dialogue blocks**, even if they contain SDH markers mixed with speech
- **Resort subtitle indices** to maintain sequential numbering
- **Maintain all timing information** for remaining blocks
- Use `--keep-sdh` flag to disable SDH removal when needed

## 🏗️ Architecture Design

### 1. **Enhanced SDH Detection System**

```python
class SDHClassifier:
    """Enhanced SDH pattern detection and classification."""
    
    SDH_PATTERNS = {
        'music_markers': [r'♪+', r'🎵+', r'🎶+'],
        'sound_descriptions': [r'\[.*?\]', r'\(.*?\)', r'【.*?】'],
        'audio_markers': [r'\[.*?(music|sound|audio|plays|rings|vibrates).*?\]'],
        'emotional_markers': [r'\[.*?(chuckles|giggles|sighs|sobs|crying).*?\]']
    }
    
    def classify_block(self, block: SubtitleBlock) -> SDHClassification
    def is_sdh_only_block(self, block: SubtitleBlock) -> bool
    def contains_dialogue_content(self, block: SubtitleBlock) -> bool
```

### 2. **SDH Removal Pipeline**

```python
class SDHRemovalProcessor:
    """Processes SRT documents to remove SDH content."""
    
    def remove_sdh_blocks(self, document: SRTDocument) -> SRTDocument:
        """Remove SDH-only blocks and resort indices."""
        
    def _filter_sdh_blocks(self, blocks: List[SubtitleBlock]) -> List[SubtitleBlock]:
        """Filter out SDH-only blocks."""
        
    def _resort_indices(self, blocks: List[SubtitleBlock]) -> List[SubtitleBlock]:
        """Resort subtitle indices sequentially."""
```

### 3. **Configuration Integration**

```python
@dataclass
class ProcessingConfig:
    # ... existing fields ...
    remove_sdh: bool = True  # SDH removal enabled by default (v2.6)
    
    def should_remove_sdh(self) -> bool:
        """Check if SDH removal is enabled."""
        return self.remove_sdh
```

### 4. **CLI Integration**

```bash
# v2.6: SDH removal is now enabled by default
# Use --keep-sdh to disable SDH removal when needed
--keep-sdh      Keep SDH (audio/music markers) instead of removing them by default

# Usage examples:
python src/main.py input.srt                    # SDH removal enabled by default
python src/main.py input.srt --keep-sdh         # Disable SDH removal
python src/main.py --batch /path/to/files       # Batch processing with default SDH removal
python src/main.py input.srt --keep-sdh --verbose  # Keep SDH with verbose output
```

## 🔄 Processing Flow Integration

### Modified Processing Pipeline (v2.6):
1. **Parse SRT** → Document with all blocks
2. **Detect Language** → Language classification  
3. **Detect Block Languages** → Mixed content handling
4. **🎯 SDH Removal** → Filter SDH blocks + resort indices (**enabled by default**, use `--keep-sdh` to disable)
5. **Language Processing** → Apply language-specific rules
6. **Validation** → Check compliance
7. **Output** → Write processed file

### Integration Points:
- **SRTProcessor.process_file()**: SDH removal enabled by default after language detection
- **SRTProcessor.check_file_only()**: SDH removal included in validation mode by default
- **CLI**: `--keep-sdh` flag to disable default SDH removal with help text and batch support
- **Models**: Extended `ProcessingConfig` and `SubtitleBlock` with SDH metadata and Unicode support

## 📊 Feature Specifications

### SDH Block Detection Logic:
```python
def is_sdh_only_block(self, block: SubtitleBlock) -> bool:
    """
    SDH-only blocks contain ONLY:
    - Music markers (♪♪, ♪♪♪)
    - Pure audio descriptions [Music plays], [Chuckles]
    - Sound effects [Mobile vibrates], [Knock on door]
    
    NOT SDH-only (preserve):
    - Dialogue with SDH: "-[ Sobbing ] It's Cal."
    - Mixed content: "Hello? [Mobile vibrates]" 
    - Regular dialogue: "- What kept you?"
    """
```

### Index Resorting Algorithm:
```python
def _resort_indices(self, blocks: List[SubtitleBlock]) -> List[SubtitleBlock]:
    """
    After SDH removal:
    Original: [1, 2, 3, 4, 5] → Remove blocks 1,2,4 → [3, 5]
    Resorted: [1, 2] with original timing preserved
    """
    for i, block in enumerate(blocks):
        block.index = i + 1
    return blocks
```

## 🎯 Implementation Benefits

### ✅ **Clean Integration**:
- Leverages existing `SubtitleBlock.is_sdh_marker()` method and enhanced Unicode detection
- **v2.6**: SDH removal enabled by default with `--keep-sdh` flag for opt-out
- Maintains backward compatibility with all existing features

### ✅ **Intelligent Processing**:
- Preserves dialogue with embedded SDH markers (comprehensive content cleaning)
- Maintains timing accuracy for remaining blocks
- Supports all languages with Unicode pattern matching (ASCII and full-width characters)
- Handles bilingual content with mixed character encodings

### ✅ **Comprehensive Coverage**:
- Works with batch processing (default SDH removal, or `--batch --keep-sdh`)
- Compatible with validation mode (default SDH removal, or `--check-only --keep-sdh`)
- Integrates with verbose output and violation reporting
- Enhanced Unicode support for Chinese, Japanese, Korean SDH markers

## 🎬 Usage Examples

### **Before SDH Removal:**
```srt
1
00:00:04,967 --> 00:00:07,467
[ Mid-tempo music plays ]

2
00:00:07,600 --> 00:00:14,333
♪♪

3
00:01:11,733 --> 00:01:12,800
-Cal!

4
00:01:23,867 --> 00:01:24,700
-[ Chuckles ]

5
00:02:56,333 --> 00:02:57,233
[ Mobile vibrates ]

6
00:03:02,300 --> 00:03:04,400
-[ Sobbing ] Ruth?
```

### **After SDH Removal (v2.6 Default Behavior):**
```srt
1
00:01:11,733 --> 00:01:12,800
-Cal!

2
00:03:02,300 --> 00:03:04,400
-[ Sobbing ] Ruth?
```

**Key Features (v2.6):**
- ✅ **Default SDH Removal**: Automatically removes pure SDH blocks (music, sounds, audio descriptions)
- ✅ **Smart Content Preservation**: Preserves dialogue with embedded SDH markers (`-[ Sobbing ] Ruth?`)
- ✅ **Sequential Resorting**: Resorts indices sequentially (1, 2 instead of 3, 6)
- ✅ **Timing Accuracy**: Maintains original timing information
- ✅ **Unicode Support**: Handles both ASCII `()` and full-width `（）` parentheses
- ✅ **Opt-out Available**: Use `--keep-sdh` when SDH markers are needed

This design provides a robust, well-integrated solution that improves subtitle readability by default while maintaining flexibility and the high code quality standards of the existing codebase.

## Implementation Status (v2.6)

1. ✅ **Enhanced SDH Detection**: Comprehensive SDH pattern detection with Unicode support
2. ✅ **SDH Filtering Logic**: SDH block filtering with dialogue preservation and content cleaning
3. ✅ **Index Resorting**: Sequential index resorting after removal implemented
4. ✅ **Configuration Updates**: `remove_sdh` flag enabled by default in ProcessingConfig
5. ✅ **CLI Integration**: `--keep-sdh` option with proper help text for opt-out behavior
6. ✅ **Unicode Enhancement**: Full-width parentheses `（）` and ASCII `()` support
7. ✅ **Testing**: Validated implementation with bilingual sample files and edge cases
8. ✅ **Documentation**: Updated for v2.6 default behavior and new CLI option