"""Display the results from Joao's model in a nice way"""
from model import make_groups
import pandas as pd


x_c = 1
data_df = pd.read_csv("Happiness test - class(2).csv")
res_df = make_groups(data_df)

students_df = data_df["student"]
res_df = pd.concat([students_df, res_df], axis=1)
res_df.columns = data_df.drop(columns=["pitched"]).columns
res_df.set_index("student", inplace=True)

display_df = res_df[res_df != 0].stack().reset_index()
display_df.columns = ["student", "project", "pref"]
display_df = display_df[["student", "project"]]
display_df.set_index("student", inplace=True)
display_df.sort_values(by=["project"], inplace=True)

print(display_df)
