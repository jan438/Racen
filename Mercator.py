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
def calcProjection(gpsData):
    projectedData = []
    for segment in gpsData:
        projectedSegment = []
        for coord in segment:
            projectedSegment.append(mercatorProjection(coord))
        projectedData.append(projectedSegment)
    return projectedData
def writeSvgData(gpsData, width, height):
    maxPixels = 500
    dropSinglePoints = True
    outfile = "SVG/out.svg"
    scaleFactor = 1.0
    if scaleFactor == None:
        if width <= maxPixels and height <= maxPixels:
            scale = 1
        elif width > height:
            scale = maxPixels / width
        else:
            scale = maxPixels / height
    else:
        scale = 1.0 / scaleFactor
    if outfile != '/dev/stdout':
        try:
            fp = open(outfile, 'w')
        except IOError as error:
            print("Can't open output file: {}. Terminating.".format(error), file = sys.stderr)
            sys.exit(1)
    else:
        fp = sys.stdout
    fp.write( '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
    fp.write(('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
              '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'))
    fp.write( '<!-- Created with gpx2svg {} -->\n'.format(__version__))
    if scaleFactor == None:
        unit = 'px'
    else:
        unit = 'mm'
    fp.write(('<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
              'width="{width}{unit}" height="{height}{unit}" '
              'viewBox="0 0 {width} {height}">\n').format(unit = unit,
                                                          width = width * scale,
                                                          height = height * scale))
    circularSegments, straightSegments = searchCircularSegments(gpsData)
    realCircularSegments = []
    singlePoints = []
    for segment in circularSegments:
        segment.pop()
        if len(segment) == 1:
            if dropSinglePoints == False:
                singlePoints.append(segment)
        else:
            realCircularSegments.append(segment)
    circularSegments = realCircularSegments
    if len(singlePoints) > 0:
        fp.write('<g>\n')
        for segment in singlePoints:
            x, y = scaleCoords(segment[0], height, scale)
            fp.write(
                '<circle cx="{}" cy="{}" r="0.5" style="stroke:none;fill:black"/>\n'.format(x, y)
            )
        fp.write('</g>\n')
    if len(circularSegments) > 0:
        fp.write('<g>\n')
        for segment in circularSegments:
            fp.write('<path d="M')
            for x, y in generateScaledSegment(segment, height, scale):
                fp.write(' {} {}'.format(x, y))
            fp.write(' Z" style="fill:none;stroke:black"/>\n')
        fp.write('</g>\n')
    if len(straightSegments) > 0:
        fp.write('<g>\n')
        for segment in straightSegments:
            fp.write('<path d="M')
            for x, y in generateScaledSegment(segment, height, scale):
                fp.write(' {} {}'.format(x, y))
            fp.write('" style="fill:none;stroke:black"/>\n')
        fp.write('</g>\n')
    fp.write('</svg>\n')
    if fp != sys.stdout:
        fp.close()
def GPX_to_SVG(cx, gpxfile, circuit):
    print(gpxfile)
    gpsData = parseGpx("Data/" + gpxfile + ".gpx")
    print("gpsData", gpsData)
    if gpsData == []:
        print('No data to convert. Terminating.', file = sys.stderr)
        sys.exit(1)
    #gpsData = combineSegments(gpsData)
    gpsData = calcProjection(gpsData)
    print("after calcProjection", gpsData)
    #gpsData, width, height = moveProjectedData(gpsData)
    #writeSvgData(gpsData, width, height)
    return
def mercatorProjection(coord):
    r = 6378137.0
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