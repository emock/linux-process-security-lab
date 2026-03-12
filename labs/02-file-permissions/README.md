 
---

1. Make setup.sh executable: chmod a+x setup.sh 
2. Execute ./setup.sh
3. Output:   
``` 
Logfile Path: /home/dev/logfile.log
```

4. Permissions after setup.sh executed:
``` 
dev@dev:~/lab-02-config$ ls -al
total 12
drwxrwxr-x  2 dev dev 4096 Mar 12 15:33 .
drwxr-x--- 10 dev dev 4096 Mar 12 15:43 ..
-rw-rw-r--  1 dev dev   40 Mar 12 15:33 config.json
 
```
5. 

---
Scenario 1:
Prerequisites:
Attacker runs as the same user dev.

Attack steps:

- read the config file
- Inject content into the file

 
---
Scenario 2:
Prerequisites:
Attacker runs as user attacker.

Attack steps:

- read the config file
- Inject content into the file

---
Scenario 3:

Change Permissions of directory to 

rwx------

Permissions of the file are unchanged.

```

```


Result:

```

```

--- 
Scenario 4:

Change Permissions of file to

rwx------

```

```


Result:

```

```
