# SRT字幕断行处理工具  产品需求文档 (PRD)

一个功能强大的多语言字幕处理工具，支持中文、英文、韩语、日语字幕的智能断行和阅读速度控制，包含SDH（听障字幕）专业支持。


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
| `--no-speed-check` | - | - | 禁用阅读速度检查 | `true	` |

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
