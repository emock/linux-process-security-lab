from dataclasses import dataclass


path = ['/tmp/lab-02-s1-open/',
       '/tmp/lab-02-s2-group-access/',
        '/tmp/lab-02-s3-owner-only/']


files = ['config1.json',
         'config2.json',
         'config3.json']


@dataclass
class Result:
    read: bool
    # write: bool
    # rename: bool
    # delete: bool


results = {}


#                               DEV     component       thirdparty
# /tmp/lab-02-s1-open/config1   R       R               R
# /tmp/lab-02-s1-open/config2   R         N                 N
# /tmp/lab-02-s1-open/config3


for p in path:
    for filename in files:

        file = p + filename

        try:
            with open(file, "r") as f:
                # print ("READ")
                read_result = Result(read=True)

        except PermissionError:
            # print ("Permission denied")
            read_result = Result(read=False)

        results[file] = read_result


# print (results)

print(f"{'FILE':40} READ")
print("-" * 50)

for file, result in results.items():
    status = "R" if result.read else "N"
    print(f"{file:40} {status}")