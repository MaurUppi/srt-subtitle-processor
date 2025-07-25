#!/usr/bin/env python3
"""Demo script to test SRT processor with sample data."""

from src.srt_processor.core.parser import SRTParser
from src.srt_processor.core.processor import SRTProcessor
from src.srt_processor.models.subtitle import Language, ProcessingConfig


def demo_processing() -> None:
    """Demonstrate SRT processing with sample data."""
    print("🎬 SRT Subtitle Processor v2.0 Demo")
    print("=" * 50)

    # Sample SRT content based on source.txt format
    sample_content = """10
00:01:13,933 --> 00:01:18,233
-怎么这么晚？
-得躲着老爷子。
-What kept you?
-Had to sneak past the old man.

36
00:02:48,900 --> 00:02:50,500
-我以为你要休假一周。
-I thought you were
taking the week.

77
00:04:56,767 --> 00:04:59,167
有进展立即通知我。
Tell 'em to call me as soon as
they have something to report.

160
00:09:25,867 --> 00:09:32,667
我当时就想"嗯，是啊。确实说得通。"
You know, I thought, "Well, aye.
Aye, that makes sense."

171
00:10:03,767 --> 00:10:08,833
♪♪
♪♪

174
00:10:11,567 --> 00:10:14,533
为什么卡尔·因尼斯昨晚和你在一起。
why Cal Innes
was with you last night.
"""

    # Parse the content
    parser = SRTParser()
    document = parser.parse_content(sample_content)

    print(f"📄 Parsed {len(document.blocks)} subtitle blocks")

    # Create processor configuration
    config = ProcessingConfig(
        language=Language.AUTO, sdh_mode=False, no_punct_fix=False
    )

    processor = SRTProcessor(config)

    # Process the document
    print("\n🔄 Processing subtitles...")
    processed_doc = processor._process_document(document)

    print(f"✅ Processed {len(processed_doc.blocks)} blocks")
    print(
        f"🌐 Detected language: {processed_doc.detected_language.value if processed_doc.detected_language else 'unknown'}"
    )

    # Show some examples of processing
    print("\n📋 Processing Examples:")
    print("-" * 30)

    for i, (original, processed) in enumerate(
        zip(document.blocks[:3], processed_doc.blocks[:3])
    ):
        print(f"\nBlock {original.index}:")
        print("Original:")
        for line in original.lines:
            print(f"  {line}")
        print("Processed:")
        for line in processed.lines:
            print(f"  {line}")

    # Validate compliance
    validation = processor.validate_document(processed_doc)
    print("\n✅ Validation Results:")
    print(f"Valid: {validation['valid']}")
    print(f"Warnings: {len(validation['warnings'])}")
    print(f"Errors: {len(validation['errors'])}")

    if validation["warnings"]:
        print("\nWarnings:")
        for warning in validation["warnings"]:
            print(f"  ⚠️  {warning}")

    # Show final output format
    print("\n📤 Final SRT Output (first 500 chars):")
    output = processed_doc.to_srt_format()
    print(output[:500] + "..." if len(output) > 500 else output)

    print("\n🎉 Demo completed successfully!")
    print("\nKey v2.0 Features Demonstrated:")
    print("  ✓ Automatic language detection")
    print("  ✓ Dialogue format optimization (- space)")
    print("  ✓ Intelligent line breaking with thresholds")
    print("  ✓ Netflix standard compliance")
    print("  ✓ SDH marker detection")
    print("  ✓ Reading speed validation")


if __name__ == "__main__":
    demo_processing()
