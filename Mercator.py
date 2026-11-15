import sys
import math
from xml.dom.minidom import parse as parseXml
import os
import csv
from enum import Enum

def parseGpx(gpxFile):
    """Get the latitude and longitude data of all track segments in a GPX file"""
    # Get the XML information
    try:
        gpx = parseXml(gpxFile)
    except IOError as error:
        print('Error while reading file: {}. Terminating.'.format(error), file = sys.stderr)
        sys.exit(1)
    except:
        print('Error while parsing XML data:', file = sys.stderr)
        print(sys.exc_info(), file = sys.stderr)
        print('Terminating.', file = sys.stderr)
        sys.exit(1)
    gpsData = []
    for track in gpx.getElementsByTagName('trk'):
        for trackseg in track.getElementsByTagName('trkseg'):
            trackSegData = []
            for point in trackseg.getElementsByTagName('trkpt'):
                trackSegData.append(
                    (float(point.attributes['lon'].value), float(point.attributes['lat'].value))
                )
            if(trackSegData != []):
                gpsData.append(trackSegData)
    return gpsData
def GPX_to_SVG(cx, gpxfile, circuit):
    print(gpxfile)
    gpsData = parseGpx("Data/" + gpxfile + ".gpx")
    print("gpsData", gpsData)
    if gpsData == []:
        print('No data to convert. Terminating.', file = sys.stderr)
        sys.exit(1)
    #gpsData = combineSegments(gpsData)
    # Calculate a plane projection for a GPS dataset
    # At the moment, we only have the Mercator projection
    #gpsData = calcProjection(gpsData, projection)
    # Move the projected data to the 0,0 origin of a cartesial coordinate system
    # and get the raw width and height of the resulting vector data
    #gpsData, width, height = moveProjectedData(gpsData)
    # Write the resulting SVG data to the requested output file or STDOUT
    #writeSvgData(gpsData, width, height, cmdArgs)
    return
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
circuitsdata = []
file_to_open = "Data/Circuits2027.csv"
with open(file_to_open, 'r') as file:
    csvreader = csv.reader(file, delimiter = ';')
    count = 0
    for row in csvreader:
        circuitsdata.append(row)
        count += 1
print(count)
for i in range(len(circuitsdata)):
    if circuitsdata[i][0] == "GillesVilleneuve":
    #if True:
        cx = i
        print(cx, "GPX_to_SVG", circuitsdata[cx][1], circuitsdata[cx][0])
        GPX_to_SVG(cx, circuitsdata[cx][1], circuitsdata[cx][0])
key = input("Wait")