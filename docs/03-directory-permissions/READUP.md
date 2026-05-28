

# Overview


## Technical Background


### Directory Basics 
A directory in Unix is a table of names and inode references, best illustrated by 
ls -ai.

```commandline
dev@dev:/tmp/lab-03-s1-700$ ls -ai
262475 .  
131074 ..  
262507 config.json  
262507 second
```

This shows the special directory entries self (.) and parent (..) as well as the 
child entries of a directory.
In this case a second file with a different name has been created pointing to the same inode
as config.json.
The directory structure lists this as a separate item.

The directory permissions answer the question:
> **Can I find/use names?**

### Read Permission
The **Unix Read Permission (r)** on a directory grants access to read this table.
As a general rule of thumb, using tab complete in a terminal on directory with active
read permission will work.

The metadata of the file, such as group, owner, file size are stored in the referenced Inode.

### Execute Permission

The Execute permission (x) on a directory facilitates a lookup/path traversal of known directory entries
and traverse the path to the target file.
Without Execute permission (x) on the directory, these entries cannot be resolved/looked up, meaning the referenced
inode cannot practically be used (e.g., via stat(), open(), cat()).

>**Important:**
>>**Even if a file is globally readable/writable/executable, it is not accessible unless Execute permission (`x`) is granted
on all parent directories required for pathname traversal.**


stat() is used here as a practical demonstration of this behavior.

```commandline
statx(AT_FDCWD, "lab-03-s1-700/config.json", AT_STATX_SYNC_AS_STAT|AT_SYMLINK_NOFOLLOW|AT_NO_AUTOMOUNT, STATX_ALL,
{stx_mask=STATX_ALL|STATX_MNT_ID, stx_attributes=0, stx_mode=S_IFREG|000, stx_size=40, ...}) = 0
```
Internally the following happens:

```commandline
AT_FDCWD
    ↓
lookup("lab-03-s1-700")
    ↓
check x permission
    ↓
lookup("config.json")
    ↓
check x permission
    ↓
inode found
    ↓
return metadata

```





```commandline
dev@dev:/tmp/lab-03-s1-700$ stat config.json 
  File: config.json
  Size: 40        	Blocks: 8          IO Block: 4096   regular file
Device: 252,0	Inode: 262507      Links: 2
Access: (0000/----------)  Uid: ( 1000/     dev)   Gid: ( 1001/shared_group)
Access: 2026-05-27 07:21:06.576196271 +0000
Modify: 2026-05-27 07:21:06.576196271 +0000
Change: 2026-05-27 08:13:36.329713579 +0000
 Birth: 2026-05-27 07:21:06.576196271 +0000
```

This provides the attributes which are commonly of interest for each entry, such as 
size, owner, group and timestamps.

Using the common ls -lai switch additionally performs a stat(() on each entry of the
directory. This shows the retrieval of the file metadata.

```commandline
dev@dev:/tmp/lab-03-s1-700$ ls -lai
total 16
262475 drwx------  2 dev  shared_group 4096 May 27 08:13 .
131074 drwxrwxrwt 34 root root         4096 May 27 07:54 ..
262507 ----------  2 dev  shared_group   40 May 27 07:21 config.json
262507 ----------  2 dev  shared_group   40 May 27 07:21 second


```

Consequently, in order to resolve metadata the name of the file is required as a prerequisite. 

## Results Read


The following table provides an overview of the results.



|USER| FILE                             | OP   | RESULT |
|----|----------------------------------|------|--------|
|dev | /tmp/lab-03-s1-700/config.json   | list | X      |
|dev | /tmp/lab-03-s2-600/config.json   | list | X      |
|dev | /tmp/lab-03-s3-500/config.json   | list | X      |
|dev | /tmp/lab-03-s4-400/config.json   | list | X      |
|dev | /tmp/lab-03-s5-300/config.json   | list | N      |
|dev | /tmp/lab-03-s6-200/config.json   | list | N      |
|dev | /tmp/lab-03-s7-100/config.json   | list | N      |
|dev | /tmp/lab-03-s8-000/config.json   | list | N      |


If the read permission is set an entitled entity can read out name and inode:

```commandline
/tmp/lab-03-s4-400/
config.json 263431
```


### Security Considerations

**Information leakage**: Child entries of directory visible 

Having read permissions on a directory facilitates information disclosure about the names 
of the files in the directory.
No further metadata of a file, such as permissions, owner or size can be obtained.




## Results Execute

The following table provides an overview of the results.

| USER | FILE                           | OP   | RESULT       |
|------|--------------------------------|------|--------------|
| dev  | /tmp/lab-03-s1-700/config.json | stat | X            |
| dev  | /tmp/lab-03-s2-600/config.json | stat | N            |
| dev  | /tmp/lab-03-s3-500/config.json | stat | X            |
| dev  | /tmp/lab-03-s4-400/config.json | stat | N            |
| dev  | /tmp/lab-03-s5-300/config.json | stat | X            |
| dev  | /tmp/lab-03-s6-200/config.json | stat | N            |
| dev  | /tmp/lab-03-s7-100/config.json | stat | X            |
| dev  | /tmp/lab-03-s8-000/config.json | stat | N            |

```commandline

dev@dev:/tmp$ stat lab-03-s5-300/config.json 
  File: lab-03-s5-300/config.json
  Size: 40        	Blocks: 8          IO Block: 4096   regular file
Device: 252,0	Inode: 263570      Links: 1
Access: (0000/----------)  Uid: ( 1000/     dev)   Gid: ( 1001/shared_group)
Access: 2026-05-27 07:21:06.594196588 +0000
Modify: 2026-05-27 07:21:06.594196588 +0000
Change: 2026-05-27 07:21:06.634197292 +0000
 Birth: 2026-05-27 07:21:06.594196588 +0000
dev@dev:/tmp$ stat lab-03-s4-400/config.json 
stat: cannot statx 'lab-03-s4-400/config.json': Permission denied

```

### Security Considerations

**Blind Access:** Names not visible, but known names usable

### Security Considerations

**Blind Access:** Names not visible, but known names usable

Test cases `/tmp/lab-03-s7-100/config.json` and `/tmp/lab-03-s5-300/config.json` demonstrate an important aspect of Unix
directory semantics: directory listing and file access are intentionally treated as separate concerns.

At first glance, the result may appear counter-intuitive: although directory listing fails, `stat()` executes
successfully.

This behavior is intentional by design.

In Unix, the Read permission (`r`) on a directory controls whether directory entries (names) can be enumerated. The
Execute permission (`x`) acts as **search/traversal permission** and determines whether already known directory entries
can be resolved during pathname traversal.

As a consequence, the absence of Read permission does **not** imply that files inside the directory are inaccessible.

If the filename is already known or can be guessed (e.g., `config.json`, `backup.zip`, `secret.txt`), traversal remains
possible as long as Execute permission (`x`) is present on the directory.

This enables operations such as:

* `stat()` to retrieve metadata
* `open()` to access file handles
* `cat()` to read file contents

provided the permissions of the referenced file allow the operation.

This design reflects a fundamental Unix principle:

> **Enumerating names and accessing known names are separate privileges.**

Consequently, directory confidentiality and file confidentiality should be treated as separate security concerns.
Preventing directory listing alone does not necessarily prevent access to files within the directory.


An equally important observation is the inverse case: missing Execute permission (`x`) on a directory acts as an
effective access barrier.

Even if files inside the directory are globally readable, writable or executable, they remain inaccessible if pathname
traversal fails due to missing Execute permission on the parent directory.

This highlights an important Unix principle:

> **File permissions alone do not determine accessibility — successful pathname traversal is required first.**

Common permission pattern in practice are:
- 711: Known entries are usable
- 750: Group can read and use entries


## Combining Read and Execute

The command ls -ali gives an impression which capabilities are available.
It should be noted that while __ls__ appears to be an atomic operation it is a sequence of operations,
such as read(), permission checks and stat().







```commandline

dev@dev:/tmp$ ls -ali lab*
lab-03-s1-700:
total 12
262475 drwx------  2 dev  shared_group 4096 May 27 11:31 .
131074 drwxrwxrwt 34 root root         4096 May 27 07:54 ..
262507 ----------  1 dev  shared_group   40 May 27 07:21 config.json

lab-03-s2-600:
ls: cannot access 'lab-03-s2-600/.': Permission denied
ls: cannot access 'lab-03-s2-600/config.json': Permission denied
ls: cannot access 'lab-03-s2-600/..': Permission denied
total 0
? d????????? ? ? ? ?            ? .
? d????????? ? ? ? ?            ? ..
? -????????? ? ? ? ?            ? config.json

lab-03-s3-500:
total 12
262867 dr-x------  2 dev  shared_group 4096 May 27 07:21 .
131074 drwxrwxrwt 34 root root         4096 May 27 07:54 ..
263057 ----------  1 dev  shared_group   40 May 27 07:21 config.json

lab-03-s4-400:
ls: cannot access 'lab-03-s4-400/.': Permission denied
ls: cannot access 'lab-03-s4-400/config.json': Permission denied
ls: cannot access 'lab-03-s4-400/..': Permission denied
total 0
? d????????? ? ? ? ?            ? .
? d????????? ? ? ? ?            ? ..
? -????????? ? ? ? ?            ? config.json
ls: cannot open directory 'lab-03-s5-300': Permission denied
ls: cannot open directory 'lab-03-s6-200': Permission denied
ls: cannot open directory 'lab-03-s7-100': Permission denied
ls: cannot open directory 'lab-03-s8-000': Permission denied

```

Interesting observations, summarized from above:

- **Blind Traversal:** s5-300 and s7-100 suggest that no access is possible: 
However as shown above, **if** the contents of the directory are already known or easily guessable, traversable and information retrievable is possible.
- s4-400 and s2-600:
The inode reference is conceptually available from the directory entry. However, GNU ls chooses not to expose it
  without successful path resolution, resulting in ? despite read access to the directory.






## Write Results

| Scenario            | File                            | dev   |
|:--------------------|:--------------------------------|:------|
| /tmp/lab-03-s1-700/ | /tmp/lab-03-s1-700/<targetfile> | X     |
| /tmp/lab-03-s2-600/ | /tmp/lab-03-s2-600/<targetfile>  | N     |
| /tmp/lab-03-s3-500/ | /tmp/lab-03-s3-500/<targetfile>  | N     |
| /tmp/lab-03-s4-400/ | /tmp/lab-03-s4-400/<targetfile>  | N     |
| /tmp/lab-03-s5-300/ | /tmp/lab-03-s5-300/<targetfile>  | X     |
| /tmp/lab-03-s6-200/ | /tmp/lab-03-s6-200/<targetfile>  | N     |
| /tmp/lab-03-s7-100/ | /tmp/lab-03-s7-100/<targetfile>  | N     |
| /tmp/lab-03-s8-000/ | /tmp/lab-03-s8-000/<targetfile>  | N     |


Before:
```commandline
dev@dev:/tmp/lab-03-s1-700$ ls
config.json delete.json rename_src.json

```

After:

```commandline
dev@dev:/tmp/lab-03-s1-700$ ls
config.json  create.json  rename_dst.json


```

Detail:

```commandline
root@dev:/tmp/lab-03-s2-600# ls
config.json  delete.json  rename_src.json

root@dev:/tmp/lab-03-s3-500# ls
config.json  delete.json  rename_src.json

root@dev:/tmp/lab-03-s4-400# ls
config.json  delete.json  rename_src.json

root@dev:/tmp/lab-03-s5-300# ls
config.json  create.json  rename_dst.json

root@dev:/tmp/lab-03-s6-200# ls
config.json  delete.json  rename_src.json

root@dev:/tmp/lab-03-s7-100# ls
config.json  delete.json  rename_src.json

root@dev:/tmp/lab-03-s8-000# ls
config.json  delete.json  rename_src.json

```















Detailed Results

| Scenario            | File                           | dev   |
|:--------------------|:-------------------------------|:------|
| /tmp/lab-03-s1-700/ | /tmp/lab-03-s1-700/create.json | X     |
| /tmp/lab-03-s2-600/ | /tmp/lab-03-s2-600/create.json | N     |
| /tmp/lab-03-s3-500/ | /tmp/lab-03-s3-500/create.json | N     |
| /tmp/lab-03-s4-400/ | /tmp/lab-03-s4-400/create.json | N     |
| /tmp/lab-03-s5-300/ | /tmp/lab-03-s5-300/create.json | X     |
| /tmp/lab-03-s6-200/ | /tmp/lab-03-s6-200/create.json | N     |
| /tmp/lab-03-s7-100/ | /tmp/lab-03-s7-100/create.json | N     |
| /tmp/lab-03-s8-000/ | /tmp/lab-03-s8-000/create.json | N     |



| Scenario            | File                               | dev   |
|:--------------------|:-----------------------------------|:------|
| /tmp/lab-03-s1-700/ | /tmp/lab-03-s1-700/rename_src.json | X     |
| /tmp/lab-03-s2-600/ | /tmp/lab-03-s2-600/rename_src.json | N     |
| /tmp/lab-03-s3-500/ | /tmp/lab-03-s3-500/rename_src.json | N     |
| /tmp/lab-03-s4-400/ | /tmp/lab-03-s4-400/rename_src.json | N     |
| /tmp/lab-03-s5-300/ | /tmp/lab-03-s5-300/rename_src.json | X     |
| /tmp/lab-03-s6-200/ | /tmp/lab-03-s6-200/rename_src.json | N     |
| /tmp/lab-03-s7-100/ | /tmp/lab-03-s7-100/rename_src.json | N     |
| /tmp/lab-03-s8-000/ | /tmp/lab-03-s8-000/rename_src.json | N     |


| Scenario            | File                           | dev   |
|:--------------------|:-------------------------------|:------|
| /tmp/lab-03-s1-700/ | /tmp/lab-03-s1-700/delete.json | X     |
| /tmp/lab-03-s2-600/ | /tmp/lab-03-s2-600/delete.json | N     |
| /tmp/lab-03-s3-500/ | /tmp/lab-03-s3-500/delete.json | N     |
| /tmp/lab-03-s4-400/ | /tmp/lab-03-s4-400/delete.json | N     |
| /tmp/lab-03-s5-300/ | /tmp/lab-03-s5-300/delete.json | X     |
| /tmp/lab-03-s6-200/ | /tmp/lab-03-s6-200/delete.json | N     |
| /tmp/lab-03-s7-100/ | /tmp/lab-03-s7-100/delete.json | N     |
| /tmp/lab-03-s8-000/ | /tmp/lab-03-s8-000/delete.json | N     |





Create Beispiel:


touch dir/newfile


resolve("dir")
↓
check x permission
↓
modify directory entries
↓
insert:
newfile -> inode 789




Delete

resolve("dir")
↓
resolve("config.json")
↓
remove entry


w in Unix:
If I can reach the namespace, I may mutate it.

300
-wx

ist der echte Write-Fall.

Das ist übrigens genau analog zu deinem Read-Modell:

400
r--

sehen

aber nicht benutzen

Und jetzt kommt der Mindfuck 😄

200 ist in Unix fast immer:

misconfiguration smell

weil:

write without search

praktisch kaum sinnvoll ist.


### `300`

```text
-wx
```


### Security Considerations




**Blind modification**: Names not visible, but known names changeable (wx)







## Summary of Security Considerations

- Read Access on a directory facilitates information disclosure of file names

- Not granting Execute bit on a directory acts as a hard stop and prevents using of files for entities

Patterns: 
- 750:
  - Other: no access to files in the directory, irregardless of the file permission
- 710: 
  - Other: same as 750
  - Group:  no directory listing possible - no further reconnaissance.
- 700: 
  - Other/Group: Hard stop for group and others 
    

