# Permissions


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




---

## Permission Checks During `open()`

If a process tries to open a file (using `open()`), the kernel checks two things:

1. **Directory traversal**
2. **File permissions**

Permissions are checked when the file descriptor is created with `open()`.
Subsequent `read()` or `write()` operations do not re-evaluate file permissions.

So If a file is modified during read

```
fd = open(file)
chmod file
read(fd)

```

Reading will still work.


---

### 1. Directory Traversal

The process needs to have **execute (`x`) permissions on all intermediate directories**, for example:

```

/tmp
/tmp/lab02-02-s2-group-access

```

This allows the process to **traverse the directory**.

If the process does not have execute permissions on a directory, it cannot reach the file — even if the file itself has permissions such as `777`.

#### Example

User `third_party` cannot access:

```

/tmp/lab-02-s2-group-access/config1_open.json

```

User `partner` cannot access files inside the directory:

```

/tmp/lab-02-s3-owner-only/

```

For example:

```

config1_open.json
config2_group.json

````

although the file permissions themselves would allow access.

---

### 2. File Permissions

If the path is reachable, the kernel checks **file permissions**.

The kernel evaluates the following permission classes:

1. **owner bits**
2. **group bits**
3. **others bits**

Conceptually, this works similar to:

```python
if uid == file_owner:
    use owner bits
elif gid in file_group or supplementary_groups:
    use group bits
else:
    use others bits
````

Group checks include all supplementary groups of the process.


Assume a file has the following permissions set:

```
-r--rw---- dev shared_group
```

If a user is the owner of the file, only the owner permission bits are evaluated.
Group and others permissions are ignored.
The permission classes are **mutually exclusive** and not **additive** 

---

## Technical Background

When a process opens a file, the following steps are executed internally:

```
sys_open()
 → path_lookup()
      checks directory execute bits
 → inode_permission()
      checks file read bits
```

Linux checks the **inode** of a file, which contains the fields:

```
i_uid
i_gid
i_mode
```

The permission bits (`rwx`) are stored inside **`i_mode`**.

---

### Implications of Directory Permission Bits

For directories, the permission bits have slightly different meanings:

| Bit   | Meaning                                               |
| ----- | ----------------------------------------------------- |
| **r** | List the contents of a directory (`ls`)               |
| **w** | Change directory entries (create/delete/rename files) |
| **x** | Traverse the directory (`cd`)                         |

---

#### Case: `r` Without `x`

If a directory only has **read permissions** set:

```
r--r--r--
```

Then listing the contents using:

```
ls dir
```

is possible.

However, it will **not** be possible to traverse the directory:

```
cd dir
cat dir/file.txt
```

because the execute bit is missing.

---

#### Case: `x` Without `r`

If a directory only has **execute permissions** set:

```
--x--x--x
```

Then traversing the directory is possible:

```
cd dir
cat dir/file.txt
```

**if the filename is already known.**

However, listing the directory contents will fail:

```
ls dir
```

because read permissions are missing.

---

## Important Takeaways

* File permissions are irrelevant if the directory is not accessible for a process.
* Directory permissions control **path traversal**, while file permissions control **data access**.
* Even if a file is set to `600`, the file can still be:

    * deleted
    * replaced
    * renamed

  if the **directory permissions allow modification**.

[] This behavior will be explored in the next exercise.



---

## Detailed Results


| Scenario                     | File               | dev   | partner   | third_party   |
|:-----------------------------|:-------------------|:------|:----------|:--------------|
| /tmp/lab-02-s1-open/         | config1_open.json  | R     | R         | R             |
| /tmp/lab-02-s1-open/         | config2_group.json | R     | R         | N             |
| /tmp/lab-02-s1-open/         | config3_owner.json | R     | N         | N             |
| /tmp/lab-02-s2-group-access/ | config1_open.json  | R     | R         | N             |
| /tmp/lab-02-s2-group-access/ | config2_group.json | R     | R         | N             |
| /tmp/lab-02-s2-group-access/ | config3_owner.json | R     | N         | N             |
| /tmp/lab-02-s3-owner-only/   | config1_open.json  | R     | N         | N             |
| /tmp/lab-02-s3-owner-only/   | config2_group.json | R     | N         | N             |
| /tmp/lab-02-s3-owner-only/   | config3_owner.json | R     | N         | N             |

| Scenario                     | File               | dev   | partner   | third_party   |
|:-----------------------------|:-------------------|:------|:----------|:--------------|
| /tmp/lab-02-s1-open/         | config1_open.json  | W     | W         | W             |
| /tmp/lab-02-s1-open/         | config2_group.json | W     | W         | N             |
| /tmp/lab-02-s1-open/         | config3_owner.json | W     | N         | N             |
| /tmp/lab-02-s2-group-access/ | config1_open.json  | W     | W         | N             |
| /tmp/lab-02-s2-group-access/ | config2_group.json | W     | W         | N             |
| /tmp/lab-02-s2-group-access/ | config3_owner.json | W     | N         | N             |
| /tmp/lab-02-s3-owner-only/   | config1_open.json  | W     | N         | N             |
| /tmp/lab-02-s3-owner-only/   | config2_group.json | W     | N         | N             |
| /tmp/lab-02-s3-owner-only/   | config3_owner.json | W     | N         | N             |