# Overview

## Technical Background

When a process opens a file (using `open()`), the kernel checks two things

1. **Directory traversal**
2. **File permissions**

```
sys_open()
 → path_lookup()
      checks directory execute bits
 → inode_permission()
      checks file read bits
```

If the path is reachable, i.e. the check of directory access is successful, the kernel checks **file permissions**.
Handling of Directory permissions is elaborated in detail in the lab directory permissions.
We will focus therefore on the second step, the file access.

The **inode** of a file contains the fields:

```
i_uid
i_gid
i_mode
```

The permission bits (`rwx`) are stored inside **`i_mode`**.

The kernel evaluates the permissions conceptually similar to the following pseudo-code:

```python
if uid == file_owner:
  use owner bits
elif gid in file_group or supplementary_groups:
  use group bits
else:
  use others bits
````
Group checks include both the primary group **and** all supplementary groups of the process.

#### Example

Assume a file has the following permissions set:

```
-r--rw---- dev shared_group
```

If a user is the owner of the file and a member of `shared_group` the owner permission bits are evaluated.
The Group and others permissions are ignored.
Hence the user `dev` will only have read access on the file.
The permission classes are **mutually exclusive** and not **additive**


### Time of check, Time of use
Permissions are checked once when the file descriptor is created with `open()`.
Subsequent `read()` or `write()` operations do not re-evaluate file permissions._

So if the permissions of a file are modified during a `read` operation, reading will still work.

Example:
```
fd = open(file)
chmod file
read(fd)

```


## Results

## Overview of Read and Write Permissions

| Scenario                     | File               | dev   | partner   | third_party   |
|:-----------------------------|:-------------------|:------|:----------|:--------------|
| /tmp/lab-02-s1-open/         | config1_open.json  | X     | X         | X             |
| /tmp/lab-02-s1-open/         | config2_group.json | X     | X         | N             |
| /tmp/lab-02-s1-open/         | config3_owner.json | X     | N         | N             |
| /tmp/lab-02-s2-group-access/ | config1_open.json  | X     | X         | N             |
| /tmp/lab-02-s2-group-access/ | config2_group.json | X     | X         | N             |
| /tmp/lab-02-s2-group-access/ | config3_owner.json | X     | N         | N             |
| /tmp/lab-02-s3-owner-only/   | config1_open.json  | X     | N         | N             |
| /tmp/lab-02-s3-owner-only/   | config2_group.json | X     | N         | N             |
| /tmp/lab-02-s3-owner-only/   | config3_owner.json | X     | N         | N             |

X meaning: Read and Write is possible

In the following we will discuss selected key insights

### Directory Traversal as a prerequisite to File Access

Although this overlaps with the lab on directories it is a key insight for file accesses.
The process needs to have **execute (`x`) permissions on all intermediate directories**, for example:
`/tmp` and `/tmp/lab02-02-s2-group-access`.
This allows the process to **traverse the directory**.
If the process does not have execute permissions on a directory, it cannot reach the file — even if the file itself has
permissions such as `777`.
This is illustrated in two scenarios, for both read and write access:
1. lab-02-s2: The user `third_party` cannot access `/tmp/lab-02-s2-group-access/config1_open.json`.
2. lab-02-s3: User `partner` cannot access files, such as `config1_open.json` or `config2_group.json` inside the directory 
`/tmp/lab-02-s3-owner-only/`, although the file permissions themselves would allow access.

## Important Takeaways

* File permissions are irrelevant if the directory is not accessible for a process.
* Directory permissions control **path traversal**, while file permissions control **data access**.


