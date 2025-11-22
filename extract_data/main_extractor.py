from typing import Optional
import json
from extract_data.process import DataExtractor
from configs.browser_config import BrowserConfig

def get_extracet(debug: bool,
                 include_all: bool,
                 config: BrowserConfig = BrowserConfig()) -> str:
    """
    Extract program data and format output.

    Parameters:
    - debug       : If True, print detailed logs with field names and counts.
    - include_all : If True, include archived/disabled/private programs.
    - config      : BrowserConfig object defining fields to extract.

    Returns:
    - str : Formatted output (JSON if error, CSV-like if normal, or debug log).
    """
    extractor = DataExtractor(config=config, include_all=include_all)
    results: Optional[list[Optional[dict]]] = extractor.extract()

    # Case 1: Error in results
    if results is None:
        return None

    field_names = list(config.fields.keys())
    output: list[str] = []

    if debug:
        # Debug mode: pretty print with numbering
        output.append("\n==========================")
        output.append(f"[📦] Finished! Total programs collected: {len(results)}")
        output.append("==========================\n")

        for idx, program in enumerate(results, start=1):
            values = [f"{field}: {program.get(field, '')}" for field in field_names]
            output.append(f"{idx:02d}. " + " — ".join(values))
    else:
        # Normal mode: CSV-like pipeline
        for program in results:
            values = [str(program.get(field, "")) for field in field_names]
            output.append(",".join(values))

    return "\n".join(output) if output else "ERROR finally"
