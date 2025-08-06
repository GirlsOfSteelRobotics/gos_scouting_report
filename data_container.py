import pandas as pd
df = pd.read_csv("data/2025tnkn/match_scouting.csv")


df["autoCoralL4Points"] = df["autoCoralL4"] * 7
df["autoCoralL3Points"] = df["autoCoralL3"] * 6
df["autoCoralL2Points"] = df["autoCoralL2"] * 4
df["autoCoralL1Points"] = df["autoCoralL1"] * 3