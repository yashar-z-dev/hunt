from typing import Optional
import json
from extract_data.process import DataExtractor
from configs.browser_config import BrowserConfig

def get_extracet(debug: bool, 
                 all: bool, 
                 config: BrowserConfig=BrowserConfig()) -> str:
    """
    - debug: print detailed logs
    - all  : Include archived/disabled/private programs too
    """
    extractor = DataExtractor(config=config, include_all=all)
    results: list[Optional[dict]] = extractor.extract()

    if results and isinstance(results[0], dict) and "error" in results[0]:
        return json.dumps(results, indent=2, ensure_ascii=False)

    else:
        field_names = list(config.fields.keys())
        output = []
        
        if not debug:
            # pipeline (CSV-like)
            for p in results:
                values = [str(p.get(field, "")) for field in field_names]
                output.append(",".join(values))
        else:
            output.append("\n==========================")
            output.append(f"[📦] Finished! Total programs collected: {len(results)}")
            output.append("==========================\n")
            for idx, p in enumerate(results, 1):
                values = [f"{field}: {p.get(field, '')}" for field in field_names]
                output.append(f"{idx:02d}. " + " — ".join(values))
        
        if output:
            return "\n".join(output)
        else:
            return "ERROR finally"
