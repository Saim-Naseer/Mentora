import pandas as pd
import json
from pathlib import Path

json_path = Path(__file__).resolve().parents[1] /"data.json"
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)  

df = pd.DataFrame(data)

df.to_csv("file.csv", index=False, encoding="utf-8")