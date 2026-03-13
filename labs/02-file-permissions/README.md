 
---

1. Make files executable: 
```
   chmod a+x setup.sh
   chmod a+x cleanup.sh
  ```
2. Execute ./setup.sh
3. Output:   
``` 
Logfile Path: /home/dev/logfile.log
```

4. The setup.sh performs the following actions on the system 
   1. Create users and shared group - Result:
   ```      
   dev@dev:~$ id partner_component
   uid=1001(partner_component) gid=1002(partner_component) groups=1002(partner_component),1001(shared_group)
   
   dev@dev:~$ id third_party  
   uid=1002(third_party) gid=1003(third_party) groups=1003(third_party)

   ```
   
   ```
   groups attacker
   attacker : attacker labgroup
    ```
   2. Setup the directories, files and POSIX DAC      
        ``` 
      dev@dev:~$ ls -al lab-02-s*
      
      lab-02-s1-open:
      total 20
      drwxrwxrwx 2 dev dev 4096 Mar 13 09:27 .
      drwxr-x--- 13 dev dev 4096 Mar 13 09:27 ..
      -rwxrwxrwx 1 dev dev 40 Mar 13 09:27 config1.json
      -rwxrwx--- 1 dev dev 40 Mar 13 09:27 config2.json
      -rwx------ 1 dev dev 40 Mar 13 09:27 config3.json
      
      lab-02-s2-group-access:
      total 20
      drwxrwx--- 2 dev dev 4096 Mar 13 09:27 .
      drwxr-x--- 13 dev dev 4096 Mar 13 09:27 ..
      -rwxrwxrwx 1 dev dev 40 Mar 13 09:27 config1.json
      -rwxrwx--- 1 dev dev 40 Mar 13 09:27 config2.json
      -rwx------ 1 dev dev 40 Mar 13 09:27 config3.json
      
      lab-02-s3-owner-only:
      total 20
      drwx------ 2 dev dev 4096 Mar 13 09:27 .
      drwxr-x--- 13 dev dev 4096 Mar 13 09:27 ..
      -rwxrwxrwx 1 dev dev 40 Mar 13 09:27 config1.json
      -rwxrwx--- 1 dev dev 40 Mar 13 09:27 config2.json
      -rwx------ 1 dev dev 40 Mar 13 09:27 config3.json

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

Szenario 7 – Symlink Attack

Attacker ersetzt:

config.json

durch

symlink

z.B.

config.json -> /etc/passwd

Wenn dein Programm blind öffnet:

open(config.json)

→ mögliches Problem.

Das ist eine klassische TOCTOU / Symlink Attack Surface.




Szenario 9 – Group Permissions

Noch gar nicht betrachtet.

Beispiel:

-rw-r----- dev config

Attacker:

user attacker
group config

Dann gilt:

group permissions

Das ist realistisch für Services.





Szenario 10 – Sticky Bit Directory

Wenn Directory:

/tmp

mit:

drwxrwxrwt

Dann kann ein User nicht einfach Files anderer löschen.

Das ist ein klassisches POSIX Szenario.