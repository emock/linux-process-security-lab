

# Overview



## Overview of Syscalls

| Operation   | Syscall               |
| ----------- | --------------------- |
| stat        | `statx`, `newfstatat` |
| create/open | `openat`              |
| rename      | `renameat2`           |
| delete      | `unlinkat`            |
| mkdir       | `mkdirat`             |


strace -e trace=file python3 test.py 2>&1 | grep openat

Options:
strace outputs by default on STDERR - using 2>&1 we can redirect it to STDOUT and use grep with coloring.
The parameters -e (only relevant syscalls) and -f (no follow children) help to reduce the scope to 
filesystem scope.

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

A central observation is that directory permissions and file permissions protect different concerns:

- directories control visibility, traversal and modification of names
- files control access to file contents


### Read Permission
The **Unix Read Permission (r)** on a directory grants access to read the file descriptor table.

```commandline
root@dev:/tmp# ls -ai lab-03-s7-100/
269903 .
131074 ..
269930 config.json
269981 delete.json
269962 rename_src.json
```
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


### Write Permission

The directory write permission in Unix may be summarized as 

> If I can reach the namespace, I **may** mutate it.

In contrast to file write permissions, directory write permissions do not control file content 
modification. Instead, they control changes to the directory namespace, i.e., the mapping of file names
to inodes.

In practice, directory write permission in combination with Execute (wx) facilitates the
following operations:
- Creation of new files
- Renaming of existing files
- Deletion of files

The following section explores, why the execute bit is needed for proper functioning.

Let's first illustrate what happens behind the scenes in each of these cases:


Create using **touch dir/newfile**

```commandline
resolve("dir")
↓
check x permission
↓
check w permission
↓
modify directory entries
↓
insert:
newfile -> inode 789
↓
return
```

Rename using `mv dir/old dir/new`

```commandline
resolve parent dir
↓
check x permission
↓
check w permission
↓
resolve "old" entry
↓
create/update:
new -> inode 123
↓
remove:
old -> inode 123
↓
same inode remains referenced
↓
return
```

During a rename operation the inode itself remains unchanged. Only the directory entry (name → inode mapping) is
modified.

Delete using `rm dir/config.json`

```commandline
resolve("dir")
↓
check x permission
↓
check w permission
↓
resolve("config.json")
↓
remove entry
↓
return
```

As can be seen in all the write operation scenarios multiple `resolve()` steps are involved.
For this to succeed the execute permission needs to be set in the directory.
This explains why  `wx` facilitates write operations and while write-only `w` does not work.


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






## Results Write

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

In case write operation is successfull the target directory is modified as follows:

```commandline
dev@dev:/tmp/lab-03-s1-700$ ls
config.json  create.json  rename_dst.json


```


### Security Considerations

**Blind modification**: s5-300 shows that while file names are not visible, creation of new files as well as
deletion and renaming of known names is possible.

**Legitimate use cases:**
Blind modification patterns (`733`, `730`, `300`) are uncommon but not inherently insecure.

Historically, such permission models have been used for **drop-box style directories**, where entities may create files
without being able to enumerate or inspect existing directory contents.

Typical examples include:

* mail spools
* upload/drop folders
* print queues
* temporary job submission directories

The underlying design principle is:

> **Write permitted, reconnaissance restricted.**

In modern systems these patterns are less common and should therefore be reviewed carefully to distinguish intentional
security design from accidental over-permissioning.

## Summary of Security Considerations

### Information Disclosure (Directory Enumeration)

Granting Read permission (`r`) on a directory enables enumeration of directory entries (file names).

This may facilitate information disclosure if file names reveal implementation details, configuration names or
predictable targets.

Typical patterns:

* `744` / `740`

  * Group/Other may enumerate file names.
* `766` / `760`

  * Same as above, additionally combined with write capabilities.

Impact:

* Usually **Low / Informational**
* Security relevance increases when file names are sensitive or predictable.

---

### Traversal Barrier (Path Resolution Protection)

Missing Execute permission (`x`) on a directory acts as an effective access barrier.

Even if files inside the directory are globally readable, writable or executable, they remain inaccessible when pathname
traversal fails.

Typical protective patterns:

* `750`

  * **Other:** no access to files in the directory, regardless of file permissions.
* `710`

  * **Other:** hard stop.
  * **Group:** traversal possible for already known names, but no directory listing.
* `700`

  * **Group/Other:** complete isolation.

Security effect:

* Prevents unintended access to child files.
* Reduces reconnaissance opportunities.
* Provides strong containment against unknown path discovery.

---

### Blind Access (Known Names Usable)

Execute permission without Read permission (`x` without `r`) enables access to already known directory entries.

Typical patterns:

* `711`
* `710`
* `300`
* `100`

Security implication:

* Directory listing blocked.
* Known or guessable file names remain accessible.
* Impact depends strongly on filename predictability.

Example risks:

```text
config.json
credentials.db
backup.zip
```

---

### Blind Modification (Known Names Mutable)

Write + Execute (`wx`) without Read permission permits directory modification despite invisible contents.

Typical patterns:

* `733`
* `730`
* `300`

Security implication:

* Creation of new files possible.
* Renaming/deletion possible for known names.
* Directory contents remain invisible.

This behavior is intentional by Unix design and demonstrates that visibility and mutability are separate privileges.

# Annex

## Detailed Results Write

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

### Create

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

### Rename

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

### Delete

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



