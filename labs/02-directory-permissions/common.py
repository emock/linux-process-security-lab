from dataclasses import dataclass, asdict
import json



@dataclass
class AccessRecord:
    user: str
    scenario: str
    file: str
    operation: str
    allowed: bool



def write_records(path, report_file, records):

    # optional JSON export
    with open("/tmp/" + report_file, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in records], f, indent=2)