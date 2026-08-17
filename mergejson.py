import requests
import json
import sys
import os
import time

circuit = "bh-2002"
with open("Data/" + circuit + "-2-1.json", 'r') as file1:
    data1 = json.load(file1)
with open("Data/" + circuit + "-2-2.json", 'r') as file2:
    data2 = json.load(file2)
merged_data = []
merged_data.append(data1)
merged_data.append(data2)
with open("Data/" + circuit + "-2.json", 'w') as outfile:
    json.dump(merged_data, outfile)

os.remove(file1)
os.remove(file2)

key = input("Wait")
