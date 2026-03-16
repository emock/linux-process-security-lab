from dataclasses import dataclass, asdict
import getpass
import json


path = ['/tmp/lab-02-s1-open/',
       '/tmp/lab-02-s2-group-access/',
        '/tmp/lab-02-s3-owner-only/']


files = ['config1_open.json',
         'config2_group.json',
         'config3_owner.json']


@dataclass
class AccessRecord:
    user: str
    file: str
    operation: str
    allowed: bool


records: list[AccessRecord] = []


current_user = getpass.getuser()


#                               DEV     component       thirdparty
# /tmp/lab-02-s1-open/config1   R       R               R
# /tmp/lab-02-s1-open/config2   R         N                 N
# /tmp/lab-02-s1-open/config3


for p in path:
    for filename in files:

        file = p + filename

        try:
            with open(file, "r") as f:
                records.append(AccessRecord(user=current_user, file=file, operation='read', allowed=True))
        except PermissionError:
            records.append(AccessRecord(user=current_user, file=file, operation='read', allowed=False))

# terminal output
print(f"{'USER':15} {'FILE':60} {'OP':8} RESULT")
print("-" * 100)
for r in records:
    result = "R" if r.allowed else "N"
    print(f"{r.user:15} {r.file:60} {r.operation:8} {result}")


report_file = current_user+"_read.json"
# optional JSON export
with open("/tmp/"+report_file, "w", encoding="utf-8") as f:
    json.dump([asdict(r) for r in records], f, indent=2)


