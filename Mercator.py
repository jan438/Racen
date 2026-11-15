import sys
import math
from xml.dom.minidom import parse as parseXml
import os
from enum import Enum

def mercatorProjection(coord):
    """Calculate the Mercator projection of a coordinate pair"""

    # Assuming we're on earth, we have (according to GRS 80):
    r = 6378137.0

    # As long as meridian = 0 and can't be changed, we don't need:
    #    meridian = meridian * math.pi / 180.0
    #    x = r * ((coord[0] * math.pi / 180.0) - meridian)

    # Instead, we use this simplified version:
    x = r * coord[0] * math.pi / 180.0
    y = r * math.log(math.tan((math.pi / 4.0) + ((coord[1] * math.pi / 180.0) / 2.0)))

    return x, y

if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == "w":
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
    os.chdir(path)
cwd = os.getcwd()
print(cwd)
key = input("Wait")