from dataclasses import dataclass, asdict
import getpass
import json
from common import write_records, AccessRecord
import os

path = ['/tmp/lab-03-s1-700/',
        '/tmp/lab-03-s2-600/',
        '/tmp/lab-03-s3-500/',
        '/tmp/lab-03-s4-400/',
        '/tmp/lab-03-s5-300/',
        '/tmp/lab-03-s6-200/',
        '/tmp/lab-03-s7-100/',
        '/tmp/lab-03-s8-000/'
        ]

files = ['delete.json'
         ]

records: list[AccessRecord] = []

current_user = getpass.getuser()





def test_list_access(operation: str):
    op_map = {
        "c": "create",
        "r": "rename",
        "d": "delete"
    }

    otag = op_map[operation]

    for p in path:

        try:

            if otag == "create":
                file = p + "create.json"
                open(file, "w").close()
            elif otag == "rename":
                file = p + "rename_src.json"
                target = p + "rename_dst.json"
                os.rename( file, target)
            elif otag == "delete":
                file = p + "delete.json"
                os.remove(file)

            records.append(
                AccessRecord(user=current_user, scenario=p, file=file, operation=otag, allowed=True))
        except PermissionError:
            records.append(
                AccessRecord(user=current_user, scenario=p, file=file, operation=otag, allowed=False))

    report_file = current_user + "_" + otag + ".json"

    write_records("/tmp/", report_file, records)



test_list_access("c")
test_list_access("r")
test_list_access("d")

# terminal output
print(f"{'USER':15} {'FILE':60} {'OP':8} RESULT")
print("-" * 100)
for r in records:
    result = "X" if r.allowed else "N"
    print(f"{r.user:15} {r.file:60} {r.operation:8} {result}")





