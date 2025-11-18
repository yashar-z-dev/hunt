# parser.add_argument("-d", "--debug", action="store_true", help="Print detailed logs")
# parser.add_argument("-a", "--all", action="store_true", help="Include archived/disabled/private programs too")

import json
from extract_data.process import DataExtractor, CONFIG

def get_extracet(debug: bool, all: bool) -> str:

    extractor = DataExtractor(config=CONFIG, include_all=all)
    results = extractor.extract()

    if isinstance(results, dict) and "error" in results:
        return json.dumps(results, indent=2, ensure_ascii=False)
    else:
        field_names = list(CONFIG["fields"].keys())
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
