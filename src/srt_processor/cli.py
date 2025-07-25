"""Command line interface for SRT processor."""

import sys
from pathlib import Path
from typing import Optional

try:
    import click
except ImportError:
    click = None

from .core.processor import SRTProcessor
from .models.subtitle import ContentType, Language, ProcessingConfig


def main_cli(
    input_file: Optional[Path] = None,
    output_file: Optional[Path] = None,
    batch: Optional[Path] = None,
    language: str = "auto",
    content_type: str = "adult",
    sdh: bool = False,
    force_encoding: Optional[str] = None,
    no_speed_check: bool = False,
    no_punct_fix: bool = False,
    verbose: bool = False,
    check_only: bool = False,
    output_violation: Optional[str] = None,
    keep_sdh: bool = False,
) -> None:
    """SRT Subtitle Processor - Multi-language subtitle processing tool.

    Process SRT subtitle files with intelligent line breaking and reading speed control.
    Supports Chinese, English, Korean, and Japanese subtitles with Netflix standard compliance.
    """
    try:
        # Create processing configuration
        config = ProcessingConfig(
            language=Language(language),
            content_type=ContentType(content_type),
            sdh_mode=sdh,
            force_encoding=force_encoding,
            no_speed_check=no_speed_check,
            no_punct_fix=no_punct_fix,
            batch_mode=batch is not None,
            batch_directory=str(batch) if batch else None,
            check_only=check_only,
            output_violation=output_violation,
            remove_sdh=not keep_sdh,
        )

        processor = SRTProcessor(config)

        if batch:
            # Batch processing mode
            if check_only:
                _check_batch(batch, processor, verbose)
            else:
                _process_batch(batch, processor, verbose)
        elif input_file:
            # Single file processing mode
            if check_only:
                _check_single_file(input_file, processor, verbose)
            else:
                _process_single_file(input_file, output_file, processor, verbose)
        elif check_only and not input_file and not batch:
            print("Error: --check-only requires either input_file or --batch")
            sys.exit(1)
        else:
            print("Error: Either input_file or --batch must be specified")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


# Click CLI wrapper (only available if click is installed)
if click:

    @click.command()
    @click.argument(
        "input_file", type=click.Path(exists=True, path_type=Path), required=False
    )
    @click.argument("output_file", type=click.Path(path_type=Path), required=False)
    @click.option(
        "--batch",
        "-b",
        type=click.Path(exists=True, file_okay=False, path_type=Path),
        help="Batch process all SRT files in directory",
    )
    @click.option(
        "--language",
        "-l",
        type=click.Choice(["auto", "zh", "en", "ko", "ja"]),
        default="auto",
        help="Specify subtitle language",
    )
    @click.option(
        "--content-type",
        "-c",
        type=click.Choice(["adult", "children"]),
        default="adult",
        help="Content type for reading speed validation",
    )
    @click.option(
        "--sdh",
        is_flag=True,
        help="Enable SDH (Subtitles for Deaf and Hard of Hearing) mode",
    )
    @click.option(
        "--force-encoding", "-e", help="Force specific encoding for output files"
    )
    @click.option(
        "--no-speed-check", is_flag=True, help="Disable reading speed validation"
    )
    @click.option(
        "--no-punct-fix", is_flag=True, help="Disable automatic punctuation correction"
    )
    @click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
    @click.option(
        "--check-only", is_flag=True, help="Only validate subtitles without processing"
    )
    @click.option(
        "--output-violation",
        "-ov",
        default=None,
        flag_value="auto",
        help="Output violation blocks to specified file (or auto-generated with -violation suffix if no file specified)",
    )
    @click.option(
        "--keep-sdh",
        is_flag=True,
        help="Keep SDH (audio/music markers) instead of removing them by default",
    )
    def main(
        input_file: Optional[Path],
        output_file: Optional[Path],
        batch: Optional[Path],
        language: str,
        content_type: str,
        sdh: bool,
        force_encoding: Optional[str],
        no_speed_check: bool,
        no_punct_fix: bool,
        verbose: bool,
        check_only: bool,
        output_violation: Optional[str],
        keep_sdh: bool,
    ) -> None:
        """Click wrapper for main CLI function."""
        main_cli(
            input_file=input_file,
            output_file=output_file,
            batch=batch,
            language=language,
            content_type=content_type,
            sdh=sdh,
            force_encoding=force_encoding,
            no_speed_check=no_speed_check,
            no_punct_fix=no_punct_fix,
            verbose=verbose,
            check_only=check_only,
            output_violation=output_violation,
            keep_sdh=keep_sdh,
        )

else:

    def main() -> None:
        """Fallback main function when click is not available."""
        print("Click library not available. Install it with: pip install click")
        sys.exit(1)


def _check_single_file(
    input_file: Path,
    processor: SRTProcessor,
    verbose: bool,
) -> None:
    """Check a single SRT file for compliance without processing.

    Args:
        input_file: Input SRT file path
        processor: SRT processor instance
        verbose: Enable verbose output
    """
    print(f"Checking: {input_file}")

    try:
        # Check the file
        results = processor.check_file_only(str(input_file))

        # Display results
        print(f"Language detected: {results['detected_language']}")
        print(f"Total blocks: {results['statistics']['total_blocks']}")
        print()
        print("=== VALIDATION REPORT ===")

        # Character limit violations
        char_warnings = results.get("character_warnings", [])
        if char_warnings:
            print(f"Character Limit Violations: {len(char_warnings)}")
            for warning in char_warnings[:10]:  # Show first 10
                print(f"  📏 {warning}")
            if len(char_warnings) > 10:
                print(
                    f"  ... and {len(char_warnings) - 10} more character limit violations"
                )
        else:
            print("Character Limit Violations: 0")

        print()

        # Reading speed violations
        speed_warnings = results.get("speed_warnings", [])
        if not processor.config.no_speed_check:
            if speed_warnings:
                print(f"Reading Speed Violations: {len(speed_warnings)}")
                for warning in speed_warnings[:10]:  # Show first 10
                    print(f"  ⏱️  {warning}")
                if len(speed_warnings) > 10:
                    print(f"  ... and {len(speed_warnings) - 10} more speed violations")
            else:
                print("Reading Speed Violations: 0")
        else:
            print("Reading Speed Validation: disabled")

        print()
        print("=== SUMMARY ===")
        compliance_rate = results.get("compliance_rate", 0)
        compliant_blocks = results.get("compliant_blocks", 0)
        total_blocks = results["statistics"]["total_blocks"]

        if compliance_rate >= 90:
            status_icon = "✅"
        elif compliance_rate >= 70:
            status_icon = "⚠️"
        else:
            status_icon = "❌"

        print(
            f"{status_icon} Compliance: {compliance_rate:.1f}% ({compliant_blocks}/{total_blocks} blocks)"
        )
        print(f"⚠️  Total Violations: {len(results['warnings'])}")
        print(f"📊 Character Limit: {len(char_warnings)} violations")
        if not processor.config.no_speed_check:
            print(f"⏱️  Reading Speed: {len(speed_warnings)} violations")

        # Generate violation output file if requested
        if processor.config.output_violation:
            _output_violations_to_file(
                results, input_file, processor.config.output_violation, verbose
            )

    except Exception as e:
        print(f"Failed to check {input_file}: {e}", file=sys.stderr)
        raise


def _check_batch(
    batch_dir: Path,
    processor: SRTProcessor,
    verbose: bool,
) -> None:
    """Check all SRT files in a directory for compliance.

    Args:
        batch_dir: Directory containing SRT files
        processor: SRT processor instance
        verbose: Enable verbose output
    """
    # Find all SRT files in directory
    srt_files = list(batch_dir.glob("*.srt"))

    if not srt_files:
        print(f"No SRT files found in {batch_dir}")
        return

    print(f"Checking {len(srt_files)} SRT files in {batch_dir}")
    print()

    checked_count = 0
    failed_count = 0
    total_violations = 0

    for srt_file in srt_files:
        try:
            if verbose:
                print(f"Checking: {srt_file}")

            # Check the file
            results = processor.check_file_only(str(srt_file))
            checked_count += 1

            violations = len(results["warnings"])
            total_violations += violations
            compliance_rate = results.get("compliance_rate", 0)

            # Generate violation output file if requested (auto-generate for batch mode)
            if processor.config.output_violation:
                _output_violations_to_file(
                    results,
                    srt_file,
                    None,
                    verbose,  # Auto-generate filename for batch mode
                )

            if verbose:
                print(f"  Language: {results['detected_language']}")
                print(f"  Blocks: {results['statistics']['total_blocks']}")
                print(f"  Violations: {violations}")
                print(f"  Compliance: {compliance_rate:.1f}%")
            else:
                if compliance_rate >= 90:
                    status = "✅"
                elif compliance_rate >= 70:
                    status = "⚠️"
                else:
                    status = "❌"
                print(
                    f"{status} {srt_file.name} - {compliance_rate:.1f}% ({violations} violations)"
                )

        except Exception as e:
            failed_count += 1
            print(f"✗ {srt_file.name}: {e}", file=sys.stderr)
            if verbose:
                import traceback

                print(traceback.format_exc(), file=sys.stderr)

    # Summary
    print("\nBatch checking complete:")
    print(f"  Checked: {checked_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Total violations: {total_violations}")
    print(
        f"  Average violations per file: {total_violations/checked_count:.1f}"
        if checked_count > 0
        else "  No files checked"
    )


def _process_single_file(
    input_file: Path,
    output_file: Optional[Path],
    processor: SRTProcessor,
    verbose: bool,
) -> None:
    """Process a single SRT file.

    Args:
        input_file: Input SRT file path
        output_file: Optional output file path
        processor: SRT processor instance
        verbose: Enable verbose output
    """
    if verbose:
        print(f"Processing: {input_file}")

    # Generate output filename if not provided
    if not output_file:
        output_file = (
            input_file.parent / f"{input_file.stem}_processed{input_file.suffix}"
        )

    try:
        # Process the file
        result = processor.process_file(str(input_file), str(output_file))

        if verbose:
            print(
                f"Language detected: {result.detected_language.value if result.detected_language else 'unknown'}"
            )
            print(f"Blocks processed: {result.total_blocks}")

            # Show speed check status
            speed_check_status = (
                "disabled" if processor.config.no_speed_check else "enabled"
            )
            print(f"Speed validation: {speed_check_status}")

            # Perform validation and show results
            validation_results = processor.validate_document(result)
            if validation_results["warnings"]:
                print(f"Validation warnings: {len(validation_results['warnings'])}")
                for warning in validation_results["warnings"][
                    :5
                ]:  # Show first 5 warnings
                    print(f"  ⚠️  {warning}")
                if len(validation_results["warnings"]) > 5:
                    print(
                        f"  ... and {len(validation_results['warnings']) - 5} more warnings"
                    )
            else:
                print("Validation: ✅ No warnings")

            print(f"Output written to: {output_file}")
        else:
            print(f"Processed: {input_file} -> {output_file}")

    except Exception as e:
        print(f"Failed to process {input_file}: {e}", file=sys.stderr)
        raise


def _process_batch(
    batch_dir: Path,
    processor: SRTProcessor,
    verbose: bool,
) -> None:
    """Process all SRT files in a directory.

    Args:
        batch_dir: Directory containing SRT files
        processor: SRT processor instance
        verbose: Enable verbose output
    """
    # Find all SRT files in directory
    srt_files = list(batch_dir.glob("*.srt"))

    if not srt_files:
        print(f"No SRT files found in {batch_dir}")
        return

    if verbose:
        print(f"Found {len(srt_files)} SRT files in {batch_dir}")

    processed_count = 0
    failed_count = 0

    for srt_file in srt_files:
        try:
            # Generate output filename
            output_file = (
                srt_file.parent / f"{srt_file.stem}_processed{srt_file.suffix}"
            )

            if verbose:
                print(f"Processing: {srt_file}")

            # Process the file
            result = processor.process_file(str(srt_file), str(output_file))
            processed_count += 1

            if verbose:
                print(
                    f"  Language: {result.detected_language.value if result.detected_language else 'unknown'}"
                )
                print(f"  Blocks: {result.total_blocks}")

                # Show validation results for batch processing
                validation_results = processor.validate_document(result)
                if validation_results["warnings"]:
                    print(f"  Warnings: {len(validation_results['warnings'])}")
                else:
                    print("  Validation: ✅ No warnings")

                print(f"  Output: {output_file}")
            else:
                print(f"✓ {srt_file.name}")

        except Exception as e:
            failed_count += 1
            print(f"✗ {srt_file.name}: {e}", file=sys.stderr)
            if verbose:
                import traceback

                print(traceback.format_exc(), file=sys.stderr)

    # Summary
    print("\nBatch processing complete:")
    print(f"  Processed: {processed_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Total: {len(srt_files)}")


def _output_violations_to_file(
    results: dict,
    input_file: Path,
    output_path: Optional[str] = None,
    verbose: bool = False,
) -> None:
    """Output violation blocks to a dedicated SRT file.

    Args:
        results: Validation results from check_file_only
        input_file: Original input file path
        output_path: Optional output file path (auto-generated if None)
        verbose: Enable verbose output
    """
    # Generate output filename if not provided or if "auto" is specified
    if not output_path or output_path == "auto":
        # Auto-generate with "-violation" suffix
        output_path = str(
            input_file.parent / f"{input_file.stem}-violation{input_file.suffix}"
        )

    # Check if we have any violations
    violation_blocks = results.get("violation_blocks", [])
    if not violation_blocks:
        if verbose:
            print("No violations found, skipping violation file creation")
        return

    try:
        # Create violation SRT content
        srt_content = _generate_violation_srt_content(results)

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(srt_content)

        if verbose:
            print(f"Violation blocks written to: {output_path}")
            print(f"Total violation blocks: {len(violation_blocks)}")
        else:
            print(f"Violations saved: {output_path}")

    except Exception as e:
        print(f"Failed to write violation file {output_path}: {e}", file=sys.stderr)
        raise


def _generate_violation_srt_content(results: dict) -> str:
    """Generate SRT content containing only violation blocks with summary.

    Args:
        results: Validation results dictionary

    Returns:
        Complete SRT file content as string
    """
    lines = []

    # Add summary header as first "subtitle" block
    lines.append("1")
    lines.append("00:00:00,000 --> 00:00:05,000")
    lines.append("=== VIOLATION ANALYSIS SUMMARY ===")

    # Compliance statistics
    compliance_rate = results.get("compliance_rate", 0)
    total_blocks = results["statistics"]["total_blocks"]
    compliant_blocks = results.get("compliant_blocks", 0)
    total_violations = len(results.get("warnings", []))
    char_violations = len(results.get("character_warnings", []))
    speed_violations = len(results.get("speed_warnings", []))

    status_icon = (
        "✅" if compliance_rate >= 90 else "⚠️" if compliance_rate >= 70 else "❌"
    )

    lines.append(
        f"{status_icon} Compliance: {compliance_rate:.1f}% ({compliant_blocks}/{total_blocks} blocks)"
    )
    lines.append(f"⚠️ Total Violations: {total_violations}")
    lines.append(f"📊 Character Limit: {char_violations} violations")
    if not results.get("no_speed_check", False):
        lines.append(f"⏱️ Reading Speed: {speed_violations} violations")
    lines.append("")  # Empty line between blocks

    # Add violation blocks
    violation_blocks = results.get("violation_blocks", [])
    for i, violation_data in enumerate(violation_blocks):
        block = violation_data["block"]
        violations = violation_data["violations"]

        # Use original block index to preserve numbering consistency
        lines.append(str(block.index))

        # Time code
        lines.append(block.time_code.to_srt_format())

        # Violation information as comments
        violation_info = []
        import re

        for violation in violations:
            # Extract the violation details
            if "character limit" in violation:
                # Handle both old format "Block 5: Exceeds character limit (34 > 16)"
                # and new format "Block 5: Line 1 exceeds character limit (34 > 16)"
                match = re.search(
                    r"character limit \((\d+) > (\d+)(?:\s+(\w+))?\)", violation
                )
                if match:
                    actual, limit = match.groups()[:2]
                    language = (
                        match.groups()[2]
                        if len(match.groups()) > 2 and match.groups()[2]
                        else None
                    )

                    # Check if it's a line-specific violation
                    if "Line" in violation:
                        line_match = re.search(r"Line (\d+)", violation)
                        if line_match:
                            line_num = line_match.group(1)
                            if language:
                                violation_info.append(
                                    f"Line {line_num} character limit ({actual} > {limit} {language})"
                                )
                            else:
                                violation_info.append(
                                    f"Line {line_num} character limit ({actual} > {limit})"
                                )
                        else:
                            if language:
                                violation_info.append(
                                    f"Character limit ({actual} > {limit} {language})"
                                )
                            else:
                                violation_info.append(
                                    f"Character limit ({actual} > {limit})"
                                )
                    else:
                        if language:
                            violation_info.append(
                                f"Character limit ({actual} > {limit} {language})"
                            )
                        else:
                            violation_info.append(
                                f"Character limit ({actual} > {limit})"
                            )
            elif "Reading speed" in violation:
                # Extract numbers: "Block 5: Reading speed too fast (16.6 > 9.0 chars/sec)"
                match = re.search(r"Reading speed.*?\(([0-9.]+) > ([0-9.]+)", violation)
                if match:
                    actual, limit = match.groups()
                    violation_info.append(
                        f"Reading speed ({actual} > {limit} chars/sec)"
                    )

        # Add violation comment line
        if violation_info:
            lines.append(f"# VIOLATIONS: {', '.join(violation_info)}")

        # Add original subtitle lines
        lines.extend(block.lines)
        lines.append("")  # Empty line between blocks

    return "\n".join(lines)


if __name__ == "__main__":
    main()
