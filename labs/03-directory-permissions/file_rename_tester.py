from dataclasses import dataclass, asdict
import getpass
import json
from common import write_records, AccessRecord
import os




path = ['/tmp/lab-03-s1-700/',
        '/tmp/lab-03-s2-500/',
        '/tmp/lab-03-s3-300/',
        '/tmp/lab-03-s4-200/',
        '/tmp/lab-03-s5-100/',
        '/tmp/lab-03-s6-000/'
        ]

files = ['config.json'
         ]

records: list[AccessRecord] = []

current_user = getpass.getuser()


def test_list_access(operation: str):
    op_map = {
        "r": "list",
    }

    otag = op_map[operation]

    for p in path:
        for filename in files:

            file = p + filename

            try:
                entries = os.listdir(p)


                # with open(file, operation) as f:
                records.append(
                    AccessRecord(user=current_user, scenario=p, file=file, operation=otag, allowed=True))
            except PermissionError:
                records.append(
                    AccessRecord(user=current_user, scenario=p, file=file, operation=otag, allowed=False))

    report_file = current_user + "_" + otag + ".json"

    write_records("/tmp/", report_file, records)





#
# def test_access(operation: str):
#     op_map = {
#         "r": "read",
#         "a": "write",
#     }
#
#     otag = op_map[operation]
#
#     for p in path:
#         for filename in files:
#
#             file = p + filename
#
#             try:
#                 with open(file, operation) as f:
#                     records.append(
#                         AccessRecord(user=current_user, scenario=p, file=filename, operation=otag, allowed=True))
#             except PermissionError:
#                 records.append(
#                     AccessRecord(user=current_user, scenario=p, file=filename, operation=otag, allowed=False))
#
#     report_file = current_user + "_" + otag + ".json"
#
#     write_records("/tmp/", report_file, records)

test_list_access("r")
# test_access("r")
# test_access("a")

# terminal output
print(f"{'USER':15} {'FILE':60} {'OP':8} RESULT")
print("-" * 100)
for r in records:
    result = "X" if r.allowed else "N"
    print(f"{r.user:15} {r.file:60} {r.operation:8} {result}")





