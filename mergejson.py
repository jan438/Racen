import requests
import json
import sys
import os
import time

with open("Data/ae-2009-2-1.json", 'r') as file:
    data = json.load(file)

key = input("Wait")
