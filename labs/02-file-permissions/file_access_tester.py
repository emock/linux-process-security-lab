from dataclasses import dataclass, asdict
import getpass
import json
from common import write_records, AccessRecord


path = ['/tmp/lab-02-s1-open/',
       '/tmp/lab-02-s2-group-access/',
        '/tmp/lab-02-s3-owner-only/']


files = ['config1_open.json',
         'config2_group.json',
         'config3_owner.json']

records: list[AccessRecord] = []


current_user = getpass.getuser()


def test_access(operation:str):

    op_map = {
        "r": "read",
        "a": "write",
    }

    otag = op_map[operation]

    for p in path:
        for filename in files:

            file = p + filename

            try:
                with open(file, operation) as f:
                    records.append(AccessRecord(user=current_user, scenario=p, file=filename, operation=otag, allowed=True))
            except PermissionError:
                records.append(AccessRecord(user=current_user, scenario=p, file=filename, operation=otag, allowed=False))


    report_file = current_user +"_"+ otag +".json"

    write_records("/tmp/", report_file, records)



test_access("r")
test_access("a")

# terminal output
print(f"{'USER':15} {'FILE':60} {'OP':8} RESULT")
print("-" * 100)
for r in records:
    result = "X" if r.allowed else "N"
    print(f"{r.user:15} {r.file:60} {r.operation:8} {result}")





