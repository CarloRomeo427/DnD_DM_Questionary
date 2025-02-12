import json
import numpy as np
with open(f"/home/romeo/Projects/DnD_DM_Questionary/Humans/user_selection_20250212_155202_2149.json", "r") as f:
    data = json.load(f)

for obj in data:
    for key, value in obj.items():
        print(key, value)
        print()
    