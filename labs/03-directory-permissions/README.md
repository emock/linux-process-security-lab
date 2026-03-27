. Setup the directories, files and POSIX DAC

```
lab-03-s1-700:
total 12
drwx------  2 dev  shared_group 4096 Mar 27 13:49 .
drwxrwxrwt 28 root root         4096 Mar 27 13:49 ..
----------  1 dev  shared_group   40 Mar 27 13:49 config.json

lab-03-s2-500:
total 12
dr-x------  2 dev  shared_group 4096 Mar 27 13:49 .
drwxrwxrwt 28 root root         4096 Mar 27 13:49 ..
----------  1 dev  shared_group   40 Mar 27 13:49 config.json

lab-03-s3-300:
total 12
d-wx------  2 dev  shared_group 4096 Mar 27 13:49 .
drwxrwxrwt 28 root root         4096 Mar 27 13:49 ..
----------  1 dev  shared_group   40 Mar 27 13:49 config.json

lab-03-s4-200:
total 12
d-w-------  2 dev  shared_group 4096 Mar 27 13:49 .
drwxrwxrwt 28 root root         4096 Mar 27 13:49 ..
----------  1 dev  shared_group   40 Mar 27 13:49 config.json

lab-03-s5-100:
total 12
d--x------  2 dev  shared_group 4096 Mar 27 13:49 .
drwxrwxrwt 28 root root         4096 Mar 27 13:49 ..
----------  1 dev  shared_group   40 Mar 27 13:49 config.json

lab-03-s6-000:
total 12
d---------  2 dev  shared_group 4096 Mar 27 13:49 .
drwxrwxrwt 28 root root         4096 Mar 27 13:49 ..
----------  1 dev  shared_group   40 Mar 27 13:49 config.json


```


Result


USER            FILE                                                         OP       RESULT
----------------------------------------------------------------------------------------------------
dev /tmp/lab-03-s1-700/config.json list X
dev /tmp/lab-03-s2-500/config.json list X
dev /tmp/lab-03-s3-300/config.json list N
dev /tmp/lab-03-s4-200/config.json list N
dev /tmp/lab-03-s5-100/config.json list N
dev /tmp/lab-03-s6-000/config.json list N

Consider

🔥 1. Sticky Bit (der wichtigste Sonderfall)

Auch wenn du ihn separat machen willst — das ist DER Gamechanger.

chmod 1777 dir

👉 Verhalten:

wx vorhanden, aber:
❌ delete/rename verboten, wenn:
nicht File-Owner
nicht Dir-Owner

💡 Beispiel wie /tmp

🔥 2. File gehört anderem User (ohne Sticky Bit!)

Das hast du selbst schon erkannt — und ja, einmal testen lohnt sich.

Setup:

# dir gehört dev

chown dev:shared_group dir
chmod 770 dir

# file gehört anderem user

chown partner_component dir/file
chmod 000 dir/file

👉 Erwartung:

dev kann löschen ✅
partner_component kann auch löschen (wenn group passt) ✅

💡 Erkenntnis:

File-Owner ist egal (ohne sticky bit)

🔥 8. (Optional) Immutable Flag
chattr +i file

👉 Verhalten:

❌ delete trotz wx
❌ rename trotz wx

💡 Erkenntnis:

DAC ist nicht alles (FS-Level Controls)

