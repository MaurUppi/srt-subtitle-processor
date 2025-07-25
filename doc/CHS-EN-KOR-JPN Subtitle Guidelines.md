# Official Subtitle Standards: Global Character Limits and Guidelines

Netflix, major broadcasters, and international standards organizations maintain detailed technical specifications for subtitle formatting that vary significantly across languages and platforms. **Netflix emerges as the most comprehensive and accessible source** for official subtitle standards, while traditional broadcasters like CCTV and Korean terrestrial networks maintain more restrictive internal guidelines.

## Character and word limits by language

### Chinese subtitle standards
**Netflix's official Chinese standards** specify **16 characters per line maximum** for both Simplified and Traditional Chinese, with **18 characters per line allowed for SDH** (Subtitles for Deaf and Hard of Hearing). Reading speed limits are **9 characters per second for adults** and **7 characters per second for children's content**.

CCTV's internal standards remain largely undocumented in public sources, though Chinese broadcasting generally follows the **open caption throughout system** rather than closed captions. Industry practice across Chinese broadcasters typically ranges from **14-16 characters per line**, with some broadcast specifications requiring **maximum 10 Chinese characters for titles** including brand and version information.

### English subtitle standards  
**Netflix maintains 42 characters per line** for both regular subtitles and SDH, matching widespread industry practice. Reading speed standards allow **up to 20 characters per second for adults** and **17 characters per second for children's content**. The **5/6 second minimum duration** applies to all subtitle events.

International broadcasting standards generally align with this **32-42 character range**, with BBC Online using **68% of 16:9 video width** and EBU-TT-D specifying **37 characters per line** for European broadcasting.

### Korean subtitle standards
**Netflix Korean guidelines specify 16 characters per line maximum** with unique character counting rules: **Korean characters count as 1 character, while Latin characters, spaces, and punctuation count as 0.5 characters**. Reading speeds allow **up to 12 characters per second for adults** and **9 characters per second for children**.

Korean terrestrial broadcasters (KBS, MBC, SBS) began implementing subtitle services only in **February 2023**, making this a rapidly evolving area. Traditional Korean broadcasting translation standards used **approximately 36 characters per line**, but modern practice has converged toward the **16-character standard**.

### Japanese subtitle standards
**Netflix Japanese standards are the most complex**, distinguishing between **horizontal subtitles (13 full-width characters per line)** and **vertical subtitles (11 full-width characters per line)**. SDH allows **16 full-width characters per line** for horizontal formatting. The **ARIB STD-B24 standard** provides the technical foundation for Japanese digital broadcasting subtitles.

Character counting follows **full-width = 1 character, half-width = 0.5 characters**, with strict **reading speed limits of 4 characters per second** for regular subtitles and **7 characters per second for SDH**.

## Line breaking rules and best practices

### Universal principles across languages
All major standards emphasize **semantic unity** - each line should contain complete thoughts when possible. **Maximum 2 lines per subtitle event** represents the universal standard, though Japanese SDH allows **3 lines when absolutely necessary**.

Text should **usually be kept to one line unless exceeding character limitations**, with preference for **bottom-heavy pyramid shape** when multiple lines are required. This creates better visual balance and reading flow.

### Language-specific line breaking rules
**English** follows detailed grammatical separation rules: avoid breaking between noun and article, verb and subject pronoun, or first and last names. **Break lines after punctuation marks**, before conjunctions, and before prepositions.

**Chinese** requires breaking at **logical semantic points** to maintain readability, with punctuation marks generally not appearing at line beginnings. **Use half-width numbers** (1,2,3) instead of full-width (１,２,３) to optimize character count.

**Korean** allows line breaks when **3 or more punctuation marks appear in one line** or **when a sentence is quoted**. No periods or commas should appear at line ends, though commas separate multiple sentences within a subtitle.

**Japanese** uses **two-em dash (⸺, U+2E3A)** for ongoing sentences split between subtitles, with **maximum two dashes per sentence**. Traditional punctuation (。) and (、) are replaced with spaces - half-width space for (、) and full-width space for (。).

## Specific platform guidelines

### Netflix's timed text style guide
Netflix maintains the **most comprehensive publicly available subtitle standards**, with separate detailed specifications for each language. Their **TTML1 format requirement** (.xml or .ttml) applies to all languages except Japanese, which uses **IMSC 1.1 format**.

Key technical requirements include **percentage-based positioning** (not pixels), **center-justified alignment**, and **minimum 2-frame gaps** between subtitle events. Netflix's **approved glyph list** restricts character usage to ensure consistent rendering across devices.

### CCTV and Chinese broadcasting standards
Chinese broadcasting operates under **National Radio and Television Administration (NRTA)** oversight, with **GY/T 270-2013 standard** existing for closed captions but not enforced. Chinese broadcasters use **burned-in subtitles exclusively** rather than closed captions, with **SimHei font** as the standard typeface.

### Japanese broadcasting standards (ARIB)
The **Association of Radio Industries and Businesses (ARIB)** maintains comprehensive Japanese broadcasting standards:
- **ARIB STD-B24**: Primary standard for Japanese digital broadcasting subtitle encoding
- **ARIB STD-B62**: Second generation multimedia coding specification  
- **ARIB STD-B69**: Closed caption file exchange format

**NTT's automated subtitle system** uses voice recognition technology to meet government requirements for subtitles on most programs **7 AM-midnight**.

### Korean broadcasting developments
Korean terrestrial broadcasting **began official subtitle services in February 2023**, with SBS becoming the first broadcaster to provide subtitles for drama reruns. This represents **the first time in Korean terrestrial broadcasting history** that dramas were officially broadcast with subtitles.

The **Korea Communications Commission (KCC)** regulates broadcasting standards, though specific technical specifications remain internal documents not publicly available.

## ISO and international standards

### ISO accessibility standards
**ISO/IEC 20071-23:2018** provides guidance for visual presentation of captions and subtitles, focusing on accessibility for users who cannot use audio information. **ISO/IEC 14496-30:2018** describes carriage of timed text in ISO base media file format.

### European broadcasting standards
**EBU-STL (EBU Tech 3264)** remains the binary format standard for European subtitle data exchange since 1991. **EBU-TT-D (EBU Tech 3380)** provides XML-based distribution for IP networks, with **37 characters per line** for BBC implementation.

### Reading speed recommendations
International standards generally recommend **160-250 words per minute for adult content** and **180 words per minute for children's content**. **BBC recommends 160-180 words per minute**, while **French standards specify 15 characters per second**.

## Comparison with current definitions

Your current definitions align **closely with Netflix's official standards** but contain some important differences:

**Chinese standards comparison:**
- Your definition: 18 characters per line max, merge lines under 6 characters
- Netflix official: **16 characters per line** (regular), **18 characters for SDH**
- **Your maximum matches Netflix SDH standards exactly**, while regular subtitles use the more restrictive 16-character limit

**English standards comparison:**
- Your definition: 42 characters per line max, minimum 5 words per line  
- Netflix official: **42 characters per line**, **no specific minimum word count**
- **Your character limit matches Netflix exactly**, though Netflix focuses on **reading speed (20 characters per second)** rather than minimum words per line

**Additional considerations:**
Your merge rules for Chinese (under 6 characters) align with Netflix's preference for **single-line text unless exceeding character limitations**. However, Netflix emphasizes **semantic completeness** over arbitrary character minimums.

The **5-word minimum for English** represents a stricter standard than Netflix's approach, which prioritizes **natural line breaking at grammatical boundaries** over minimum word counts.

## Conclusion

Netflix's publicly available Timed Text Style Guide represents the most comprehensive and technically detailed subtitle standards currently accessible, serving as the de facto international standard for streaming content. Traditional broadcasters maintain more restrictive internal guidelines, with Chinese and Korean broadcasters showing recent evolution toward international practices. Your current definitions demonstrate strong alignment with industry standards, particularly matching Netflix's technical specifications for character limits while implementing additional semantic rules for line combination.