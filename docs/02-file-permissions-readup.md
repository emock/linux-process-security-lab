
| Scenario | File  | dev | partner | third_party |
|----------| ----- | --- | ------- | ----------- |
| s1 open  | open  | R   | R       | R           |
| s1 open  | group | R   | R       | N           |
| s1 open  | owner | R   | N       | N           |
| s2 group | open  | R   | R       | N           |
| s2 group | group | R   | R       | N           |
| s2 group | owner | R   | N       | N           |
| s3 owner | open  | R   | N       | N           |
| s3 owner | group | R   | N       | N           |
| s3 owner | owner | R   | N       | N           |


Key Insights:

The directory permissions regulate who can traverse the contents of the directory.
Specifically:
Scenario s3 owner, with wordl readable config file is neither readable by the partner nor the thirdparty user.

The file content permission decide - if a user has access to the directory - who can access the file:
Scenario:
| Scenario | File | dev | partner | third_party |
|----------| ----- | --- | ------- | ----------- |
| s2 group | owner | R | N | N |

Only the Owner can access the file, as the permissions are set to:
chmod u=rw,g=,o= "$TARGET_DIR2/config3_owner.json"