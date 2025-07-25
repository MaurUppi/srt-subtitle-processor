# TODO: Fix Bilingual Subtitle Validation Issue

## Problem Analysis

### Issue Description
The violation checking logic incorrectly applies single-language rules to bilingual subtitles. In the example:

**Original:**
```
65
00:04:31,667 --> 00:04:33,333
-为什么让她靠近尸体？
-Why did you let her
near the body?
```

**Current (Incorrect) Validation:**
```
# VIOLATIONS: Line 2 character limit (20 > 16)
```
- Line 1: Chinese text (should use 16-char limit) ✅
- Line 2: English text "Why did you let her" (20 chars, should use 42-char limit) ❌ **Incorrectly flagged**
- Line 3: English text "near the body?" (should use 42-char limit) ✅

### Root Cause
The validation logic in `processor.py:382` applies the block's detected language to all lines:
```python
char_limit = self.config.get_character_limit(block_language)  # Uses block language for all lines
for line_idx, line in enumerate(block.lines):
    if len(line) > char_limit:  # Same limit applied to all lines
```

But bilingual blocks require **per-line language detection** and **per-line validation rules**.

## Solution Plan

### Phase 1: Implement Per-Line Language Detection for Validation
1. **Modify `validate_document()` method** to detect language of each line individually
2. **Apply language-specific character limits** per line instead of per block
3. **Apply language-specific reading speed rules** when appropriate

### Phase 2: Enhanced Bilingual Support
1. **Improve language detection accuracy** for mixed-language lines
2. **Handle edge cases** like punctuation-only lines, empty lines
3. **Optimize performance** to avoid redundant language detection calls

### Phase 3: Testing and Validation
1. **Create comprehensive test cases** with various bilingual combinations
2. **Verify compliance** with Netflix standards for each language
3. **Ensure backward compatibility** with single-language content

## Implementation Steps

### Step 1: Update Character Limit Validation Logic
**File:** `src/srt_processor/core/processor.py`
**Location:** `validate_document()` method around line 382

**Current Logic:**
```python
char_limit = self.config.get_character_limit(block_language)
for line_idx, line in enumerate(block.lines):
    if len(line) > char_limit:
```

**New Logic:**
```python
for line_idx, line in enumerate(block.lines):
    # Detect language for each line individually
    line_language = self.language_detector.detect_line_language(line)
    char_limit = self.config.get_character_limit(line_language)
    if len(line) > char_limit:
```

### Step 2: Update Reading Speed Validation
**Consider:** Reading speed should still be calculated at block level since it's based on timing, but validation rules should consider the dominant language or apply strictest rules.

### Step 3: Update Violation Output Format
**File:** `src/srt_processor/cli.py`
**Enhancement:** Include language information in violation messages for clarity.

**Example:**
```
# VIOLATIONS: Line 2 character limit (20 > 16 Chinese), Line 3 character limit (45 > 42 English)
```

### Step 4: Test Cases
Create test files with:
1. Chinese-English bilingual content
2. Korean-English bilingual content  
3. Mixed dialogue vs. narrative text
4. Edge cases (empty lines, punctuation-only)

## Expected Results

### Before Fix:
```
# VIOLATIONS: Line 2 character limit (20 > 16)  ❌ Wrong limit applied
```

### After Fix:
```
# No character limit violations  ✅ Correct validation
```

**Validation Logic:**
- Line 1: "-为什么让她靠近尸体？" (Chinese, 11 chars, limit 16) ✅
- Line 2: "-Why did you let her" (English, 20 chars, limit 42) ✅  
- Line 3: "near the body?" (English, 14 chars, limit 42) ✅

## ✅ **COMPLETED - Priority: HIGH**

### **Implementation Results**

**✅ Step 1: Per-Line Language Detection**
- Updated `validate_document()` method in `processor.py` to detect language for each line individually
- Character limits now applied per-line based on detected language (Chinese: 16, English: 42, etc.)
- Added language code to violation messages for clarity

**✅ Step 2: Enhanced Violation Output**
- Updated violation parsing in `cli.py` to handle language-specific format
- Violation comments now show: `Line 1 character limit (32 > 16 zh), Line 2 character limit (114 > 42 en)`

**✅ Step 3: Reading Speed Validation**
- Reading speed validation correctly remains at block level (timing-based)
- Block-level language detection used for speed limits (appropriate for timing calculations)

### **Test Results - User's Example**

**Before Fix:**
```
# VIOLATIONS: Line 2 character limit (20 > 16)  ❌ Wrong limit applied
```

**After Fix:**
```
# VIOLATIONS: Reading speed (27.0 > 9.0 chars/sec)  ✅ Only speed violation, no character limit violations
```

**Validation Analysis:**
- Line 1: "-为什么让她靠近尸体？" (Chinese, 11 chars ≤ 16 limit) ✅
- Line 2: "-Why did you let her" (English, 20 chars ≤ 42 limit) ✅  
- Line 3: "near the body?" (English, 14 chars ≤ 42 limit) ✅

**🎯 Issue Resolved:** Bilingual subtitle validation now correctly applies language-specific character limits per line while maintaining proper reading speed validation at the block level.