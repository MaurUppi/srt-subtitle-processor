# SRT字幕断行处理工具 v2.2

一个功能强大的多语言字幕处理工具，支持中文、英文、韩语、日语字幕的智能断行和阅读速度控制，包含SDH（听障字幕）专业支持。

## 🚀 新版本特性

### v2.2 最新更新
- **智能合并算法**：每种语言都有专门的智能合并算法
- **对话格式检测**：自动识别和处理对话型字幕
- **增强的处理器架构**：统一的处理器基类，语言特定的处理逻辑
- **完善的对话处理**：统一的"- "格式，支持多行对话智能合并
- **架构一致性**：所有语言处理器使用相同的智能合并模式

### v2.0 重大更新
- **多语言支持**：全新支持中文、英文、韩语、日语四种语言
- **智能语言检测**：自动识别字幕语言并应用相应处理规则
- **SDH字幕支持**：专业的听障字幕处理模式
- **阅读速度控制**：根据语言和内容类型智能检测阅读速度
- **对话格式优化**：特殊处理对话型字幕格式
- **模块化架构**：重构代码结构，提升可维护性
- **增强命令行界面**：更丰富的参数选项和帮助信息

## 📦 安装要求

- Python 3.8 或更高版本
- 无需额外依赖库（使用Python标准库）

## 🛠️ 使用方法

### 单文件处理模式

```bash
# 基本用法（自动生成输出文件）
python srt_batch_processor-v2.2.py input.srt

# 指定输出文件
python srt_batch_processor-v2.2.py input.srt output.srt

# 支持路径处理
python srt_batch_processor-v2.2.py /path/to/input.srt

# 指定语言和内容类型
python srt_batch_processor-v2.2.py input.srt --language zh --content-type children
```

### 批处理模式

```bash
# 处理当前目录所有.srt文件
python srt_batch_processor-v2.2.py --batch

# 处理指定目录
python srt_batch_processor-v2.2.py --batch /path/to/subtitles/

# 批处理并指定参数
python srt_batch_processor-v2.2.py --batch --language auto --force-encoding utf-8
```

### SDH字幕处理

```bash
# 启用SDH模式
python srt_batch_processor-v2.2.py input.srt --sdh

# 自动检测SDH + 指定语言
python srt_batch_processor-v2.2.py input.srt --language ja --sdh
```

## 📋 命令行参数

| 参数 | 短参数 | 选项 | 说明 | 默认值 |
|------|--------|------|------|-------|
| `input_file` | - | - | 输入SRT文件路径 | - |
| `output_file` | - | - | 输出SRT文件路径（可选） | 自动生成 |
| `--batch` | `-b` | `[目录]` | 批处理模式 | 当前目录 |
| `--language` | `-l` | `auto/zh/en/ko/ja` | 指定语言 | `auto` |
| `--content-type` | `-c` | `adult/children` | 内容类型 | `adult` |
| `--sdh` | - | - | 启用SDH模式 | `False` |
| `--force-encoding` | `-e` | 编码格式 | 强制输出编码 | 自动检测 |
| `--no-speed-check` | - | - | 禁用阅读速度检查 | `False` |

## 🌍 多语言支持

### 支持的语言

| 语言 | 代码 | 字符限制 | 阅读速度 (成人/儿童) | 特殊处理 |
|------|------|----------|---------------------|----------|
| 中文 | `zh` | 16字符 (SDH: 18) | 9/7 字符/秒 | 智能标点断行 |
| 英文 | `en` | 42字符 | 20/17 字符/秒 | 单词边界断行 |
| 韩语 | `ko` | 16字符 | 12/9 字符/秒 | 韩文字符计算 |
| 日语 | `ja` | 13字符 (SDH: 16) | 4/4 字符/秒 (SDH: 7/7) | 全角半角混合计算 |

### 自动语言检测

程序会自动分析字幕内容，根据字符特征判断语言类型：

- **中文检测**：汉字Unicode范围 (0x4e00-0x9fff) + 中文标点
- **英文检测**：ASCII字母字符
- **韩语检测**：韩文字符Unicode范围 (0xac00-0xd7af)
- **日语检测**：假名字符 (平假名 + 片假名) + 汉字组合

## 🎯 处理规则详解

### 中文字幕处理

- **字符限制**：普通字幕16字符，SDH字幕18字符
- **智能合并**：`smart_merge_chinese_lines()` 方法处理多行合并
- **智能断行**：优先在标点符号、语气停顿词后断行
- **语气停顿词**：的、了、吧、呢、啊、哦、嗯、呀、哇、吗、嘛
- **短行合并**：少于6个字符的行自动合并
- **对话处理**：特殊处理以 "-" 开头的对话格式

### 英文字幕处理

- **字符限制**：42字符（所有类型统一）
- **智能合并**：`smart_merge_english_lines()` 方法处理连词和标点
- **单词完整性**：绝不在单词中间断行
- **避免短行**：优化连词和介词的断行位置
- **智能合并**：根据标点符号智能合并多行
- **连词处理**：识别and、but、because等连词，优化断行位置

### 韩语字幕处理

- **字符限制**：16字符
- **智能合并**：`smart_merge_korean_lines()` 方法处理韩语标点
- **混合计算**：韩文字符1倍，ASCII字符0.5倍
- **标点处理**：支持韩语标点符号：'。！？，：""（）【】《》'
- **对话格式**：统一的"- "格式处理

### 日语字幕处理

- **字符限制**：普通13字符，SDH 16字符
- **智能合并**：`smart_merge_japanese_lines()` 方法处理日语标点
- **字符计算**：全角字符1倍，半角字符0.5倍
- **标点处理**：支持日语标点符号：'。！？、：""（）【】《》〈〉'
- **SDH特殊处理**：检测音效标记，应用SDH速度限制

## 🔧 架构特点

### 处理器架构

#### 基础处理器 (`BaseLanguageProcessor`)
- **对话格式检测**：`detect_dialogue_format()` - 检测以"-"开头的对话行
- **对话行处理**：`process_dialogue_lines()` - 专门处理对话格式
- **对话格式化**：`format_dialogue_line()` - 统一格式化为"- "格式

#### 语言特定处理器
- **ChineseProcessor**：`smart_merge_chinese_lines()` + `break_chinese_line()`
- **EnglishProcessor**：`smart_merge_english_lines()` + `break_english_line()`
- **KoreanProcessor**：`smart_merge_korean_lines()` + `_break_korean_line()`
- **JapaneseProcessor**：`smart_merge_japanese_lines()` + `_break_japanese_line()`

### 智能合并算法

#### 中文智能合并
```python
def smart_merge_chinese_lines(self, lines: List[str]) -> str:
    # 根据中文标点符号智能合并多行
    # 处理：'。！？，、；：""（）【】《》〈〉'
```

#### 英文智能合并
```python
def smart_merge_english_lines(self, lines: List[str]) -> str:
    # 根据英文标点和连词智能合并
    # 避免在连词前断行
```

#### 韩语智能合并
```python
def smart_merge_korean_lines(self, lines: List[str]) -> str:
    # 根据韩语标点符号智能合并
    # 处理：'。！？，：""（）【】《》'
```

#### 日语智能合并
```python
def smart_merge_japanese_lines(self, lines: List[str]) -> str:
    # 根据日语标点符号智能合并
    # 处理：'。！？、：""（）【】《》〈〉'
```

### 对话格式处理

#### 对话检测逻辑
```python
def detect_dialogue_format(self, lines: List[str]) -> bool:
    dialogue_lines = [line for line in lines if line.strip().startswith("-")]
    return len(dialogue_lines) >= 1  # 至少1行对话才认为是对话格式
```

#### 对话处理流程
1. **检测对话格式**：识别以"-"开头的行
2. **智能合并**：应用语言特定的智能合并算法
3. **断行处理**：根据语言规则进行断行
4. **格式化输出**：统一格式化为"- "格式

## 🔍 SDH字幕支持

### SDH检测模式

程序会自动检测以下SDH标记：
- `[音效]` 格式
- `(sound effect)` 格式
- `(music)` 格式
- `(noise)` 格式
- `♪音乐♪` 格式
- 音符符号 ♪ ♫

### SDH处理规则

- **中文SDH**：字符限制18 (vs 普通16)
- **日语SDH**：字符限制16 (vs 普通13)，阅读速度7字符/秒 (vs 普通4)
- **自动检测**：无需手动指定，程序会自动识别SDH内容

## 📊 阅读速度控制

### 速度标准

| 语言 | 成人内容 | 儿童内容 | SDH特殊 |
|------|----------|----------|---------|
| 中文 | 9字符/秒 | 7字符/秒 | - |
| 英文 | 20字符/秒 | 17字符/秒 | - |
| 韩语 | 12字符/秒 | 9字符/秒 | - |
| 日语 | 4字符/秒 | 4字符/秒 | 7字符/秒 |

### 速度检测

- **自动检测**：计算字符数/显示时长
- **超标警告**：显示实际速度 vs 标准速度
- **可选禁用**：使用 `--no-speed-check` 参数

## 🔧 使用示例

### 示例1：自动检测处理

```bash
# 自动检测语言，生成 input-edit.srt
python srt_batch_processor-v2.2.py input.srt
```

### 示例2：指定日语SDH处理

```bash
# 日语SDH字幕，儿童内容
python srt_batch_processor-v2.2.py japanese_sdh.srt --language ja --content-type children --sdh
```

### 示例3：批处理多语言字幕

```bash
# 处理指定目录，自动检测所有语言
python srt_batch_processor-v2.2.py --batch /path/to/subtitles/
```

### 示例4：编码转换

```bash
# 强制UTF-8输出
python srt_batch_processor-v2.2.py input.srt --force-encoding utf-8
```

## 📝 处理效果对比

### 中文字幕处理

**处理前：**
```srt
263
00:12:07,254 --> 00:12:09,651
任何依赖肌肉信号的设备
都会存在延迟问题。
```

**处理后：**
```srt
263
00:12:07,254 --> 00:12:09,651
任何依赖肌肉信号的设备都会存在延迟问题。
```

### 英文字幕处理

**处理前：**
```srt
264
00:12:09,651 --> 00:12:12,254
Any device that relies on
muscle signals is going to
suffer from latency.
```

**处理后：**
```srt
264
00:12:09,651 --> 00:12:12,254
Any device that relies on muscle signals
is going to suffer from latency.
```

### 对话格式处理

**处理前：**
```srt
442
00:23:51,600 --> 00:23:54,433
-埃伦不是那种
沉溺悲伤的人。
-Ellen wasn't one
for dwelling on sad stuff.
```

**处理后：**
```srt
442
00:23:51,600 --> 00:23:54,433
- 埃伦不是那种沉溺悲伤的人。
- Ellen wasn't one for dwelling on sad stuff.
```

### 日语SDH处理

**处理前：**
```srt
266
00:12:15,651 --> 00:12:18,254
[音楽が流れる]
これは素晴らしい技術です。
```

**处理后：**
```srt
266
00:12:15,651 --> 00:12:18,254
[音楽が流れる]これは素晴らしい技術です。
```

## 🎨 模块化设计

### 核心组件

- **LanguageDetector**：语言自动检测
- **SDHDetector**：SDH字幕检测
- **ReadingSpeedCalculator**：阅读速度计算
- **BaseLanguageProcessor**：语言处理器基类
- **具体语言处理器**：中文、英文、韩语、日语专用处理器

### 配置管理

```python
ProcessingConfig(
    language=Language.AUTO,          # 语言设置
    content_type=ContentType.ADULT,  # 内容类型
    is_sdh=False,                    # SDH模式
    force_encoding=None,             # 强制编码
    no_speed_check=False            # 禁用速度检查
)
```

### 统计信息

- **处理结果统计**：成功/失败文件数量
- **速度警告汇总**：显示阅读速度超标的字幕
- **编码信息**：输入输出编码显示

## ⚠️ 注意事项

### 文件处理

- **安全性**：批处理不会覆盖原文件
- **备份建议**：处理重要文件前建议备份
- **文件命名**：自动生成 `-edit` 后缀文件

### 编码处理

- **自动检测**：支持 UTF-8、GBK、GB2312、UTF-16、Latin1
- **编码保持**：默认保持输入输出编码一致
- **强制转换**：可指定输出编码格式

### 处理限制

- **格式支持**：仅支持标准SRT格式
- **语言混合**：可处理多语言混合字幕
- **特殊字符**：正确处理各语言特殊字符

## 🐛 故障排除

### 常见问题

**Q: 提示"无法读取文件"**  
A: 检查文件编码或路径是否正确，尝试指定 `--force-encoding utf-8`

**Q: 阅读速度警告过多**  
A: 使用 `--no-speed-check` 禁用检查，或检查字幕时长设置

**Q: 日语字幕处理效果不佳**  
A: 尝试启用SDH模式 `--sdh`，或手动指定 `--language ja`

**Q: 对话格式断行异常**  
A: 程序会自动检测对话格式，确保以 "-" 开头的行格式正确

### 调试建议

1. **详细输出**：程序会显示检测到的语言、编码、SDH状态
2. **速度检查**：注意阅读速度警告，调整字幕时长
3. **编码问题**：使用 `--force-encoding` 解决编码问题
4. **批处理**：检查目录路径和文件权限

## 🔄 版本历史

### v2.2 (当前版本)
- ✅ 智能合并算法：每种语言都有专门的智能合并方法
- ✅ 对话格式检测：完善的对话格式检测和处理
- ✅ 架构统一：所有语言处理器使用相同的处理模式
- ✅ 韩语增强：添加智能合并和对话处理支持
- ✅ 日语增强：添加智能合并和对话处理支持
- ✅ 一致性改进：统一的"- "格式处理

### v2.0 (重大更新)
- ✅ 全面重构，支持中英韩日四种语言
- ✅ 智能语言检测和自动处理
- ✅ SDH字幕专业支持
- ✅ 阅读速度控制系统
- ✅ 对话格式特殊处理
- ✅ 模块化架构设计
- ✅ 增强的命令行界面

### v1.7 (上一版本)
- ✅ 基础双语字幕处理
- ✅ 批处理功能
- ✅ 编码自动检测
- ✅ 智能断行优化

### v1.6
- ✅ 智能标点符号处理
- ✅ 连接词识别功能
- ✅ 短行合并优化

### v1.5
- ✅ 双语字幕智能识别
- ✅ 基础断行功能
- ✅ SRT格式解析

## 💡 技术亮点

### 智能算法

- **语言检测**：基于Unicode范围和字符特征
- **智能合并**：语言特定的智能合并算法
- **断行优化**：语言特定的断行规则
- **阅读速度**：科学的速度计算标准
- **SDH识别**：正则表达式模式匹配

### 架构优化

- **处理器继承**：统一的基类，语言特定的实现
- **智能合并**：每种语言都有专门的合并算法
- **对话处理**：统一的对话格式检测和处理
- **配置管理**：完善的配置系统

### 性能优化

- **批量处理**：高效的文件处理流程
- **编码检测**：多编码格式自动识别
- **错误处理**：完善的异常处理机制
- **用户体验**：友好的进度提示和错误信息

## 📄 许可证

本项目采用 MIT 许可证。

## 🤝 贡献指南

欢迎提交问题报告和功能建议：

1. **问题报告**：详细描述问题和复现步骤
2. **功能建议**：说明使用场景和预期效果
3. **代码贡献**：遵循现有代码风格和架构设计

## 📧 联系方式

- **问题反馈**：通过 GitHub Issues
- **功能讨论**：通过 GitHub Discussions
- **紧急问题**：通过邮件联系

---

**享受更专业的多语言字幕处理体验！** 🎬🌍✨