import json

with open("krk_original.json") as f:
    data = json.load(f)
    

import pandas as pd 

df = pd.DataFrame.from_dict(data)

print(df[df.duplicated()])