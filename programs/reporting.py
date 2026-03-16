import pandas as pd
from pathlib import Path

OPERATION = "read"
OTAG = "X"

# Directory mit JSON Ergebnissen
result_dir = Path("docs/02-file-permissions")





# Alle JSON Files einlesen
dfs = []
for file in result_dir.glob("*.json"):
    dfs.append(pd.read_json(file))

df = pd.concat(dfs, ignore_index=True)

# Nur READ Operation
df = df[df["operation"] == OPERATION]

# Boolean → R/N
df["allowed"] = df["allowed"].map({True: OTAG, False: "N"})

# Pivot Tabelle
table = df.pivot_table(
    index=["scenario", "file"],
    columns="user",
    values="allowed",
    aggfunc="first"
).reset_index()

# Spalten schöner benennen
table = table.rename(columns={
    "scenario": "Scenario",
    "file": "File",
    "partner_component": "partner"
})

print(table.to_markdown(index=False))