import pandas as pd


m0 = pd.read_csv("cache/ny-test-3boroughs/matrix0.csv")
m1 = pd.read_csv("cache/ny-test-3boroughs/matrix1.csv")

m = pd.merge(m0, m1, on=["from_id", "to_id"], suffixes=["_0", "_1"])
m["delta"] = m["travel_time_1"] - m["travel_time_0"]

print(m[m["delta"] < 0].shape[0], m.shape[0])
print(m[m["delta"] < 0])
