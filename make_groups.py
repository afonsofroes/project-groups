import pandas as pd
from groupmaker import GroupMaker

model = GroupMaker()

data_df = pd.read_csv("selections_pitch.csv")

model.fit(data_df)

model.groups()
