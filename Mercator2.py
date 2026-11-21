import sys
import math
from xml.dom.minidom import parse as parseXml
import os
import csv
import json
import gpxpy
import gpxpy.gpx
import io
from enum import Enum
from geopy.distance import great_circle

def get_property(properties, key, default='noname'):
    return properties.get(key) or properties.get(key.capitalize(), default)
def process_linestring(geom, properties, gpx, circuit):
    node = geom['coordinates']
    gpx_track = gpxpy.gpx.GPXTrack(name=circuit)
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)
    cnt = 0
    for coord in node:
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(coord[1],  coord[0]))
        cnt += 1
    print(circuit, "linestring", cnt)
def process_point(geom, properties, custom_symbol, gpx, circuit):
    node = geom['coordinates']
    new_wpt = gpxpy.gpx.GPXWaypoint()
    new_wpt.name = get_property(properties, 'f1')
    symbol = properties.get('sym')
    if symbol is None and custom_symbol != "":
        new_wpt.symbol = custom_symbol
    else:
        new_wpt.symbol = symbol
    new_wpt.latitude, new_wpt.longitude = node[1], node[0]
    gpx.waypoints.append(new_wpt)
    print(circuit, "point", new_wpt.name)
def process_geometry(geom, properties, custom_symbol, gpx, circuit):
    geom_type = geom['type']
    if geom_type == 'LineString':
        process_linestring(geom, properties, gpx, circuit)
    elif geom_type == 'Point':
        process_point(geom, properties, custom_symbol, gpx, circuit)
    return
def parseGpx(gpxFile):
    try:
        gpx = parseXml(gpxFile)
    except:
        print('Terminating.', file = sys.stderr)
        sys.exit(1)
    trkData = []
    for track in gpx.getElementsByTagName('trk'):
        for trackseg in track.getElementsByTagName('trkseg'):
            trackSegData = []
            for point in trackseg.getElementsByTagName('trkpt'):
                trackSegData.append(
                    (float(point.attributes['lon'].value), float(point.attributes['lat'].value))
                )
            if(trackSegData != []):
                trkData.append(trackSegData)
    wptData = []
    for wpt in gpx.getElementsByTagName('wpt'):
        lon = wpt.attributes['lon'].value
        lat = wpt.attributes['lat'].value
        name = wpt.getElementsByTagName('name')[0].firstChild.data
        wptData.append((name, lon, lat))
    return trkData, wptData
def calcProjection(trkData):
    projectedData = []
    for segment in trkData:
        projectedSegment = []
        for coord in segment:
            projectedSegment.append(mercatorProjection(coord))
        projectedData.append(projectedSegment)
    return projectedData
def extentOfProjectedData(trkData):
    minX = maxX = trkData[0][0][0]
    minY = maxY = trkData[0][0][1]
    for segment in trkData:
        for coord in segment:
            if coord[0] < minX:
                minX = coord[0]
            if coord[0] > maxX:
                maxX = coord[0]
            if coord[1] < minY:
                minY = coord[1]
            if coord[1] > maxY:
                maxY = coord[1]
    return minX, maxX, minY, maxY
def moveProjectedData(trkData):
    minX, maxX, minY, maxY = extentOfProjectedData(trkData)
    movedtrkData = []
    for segment in trkData:
        movedSegment = []
        for coord in segment:
            movedSegment.append((coord[0] - minX, coord[1] - minY))
        movedtrkData.append(movedSegment)
    return movedtrkData, maxX - minX, maxY - minY
def searchCircularSegments(trkData):
    circularSegments = []
    straightSegments = []
    for segment in trkData:
        if segment[0] == segment[len(segment) - 1]:
            circularSegments.append(segment)
        else:
            straightSegments.append(segment)
    return circularSegments, straightSegments
def scaleCoords(coord, height, scale):
    return coord[0] * scale, (coord[1] * -1 + height) * scale
def generateScaledSegment(segment, height, scale):
    for coord in segment:
        yield scaleCoords(coord, height, scale)
def writeSvgData(trkData, width, height, outfile):
    maxPixels = 3000
    dropSinglePoints = False
    if width <= maxPixels and height <= maxPixels:
        scale = 1
    elif width > height:
        scale = maxPixels / width
    else:
        scale = maxPixels / height
    fp = open(outfile, 'w')
    fp.write( '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
    fp.write(('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
              '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'))
    unit = 'px'
    fp.write(('<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
              'width="{width}{unit}" height="{height}{unit}" '
              'viewBox="0 0 {width} {height}">\n').format(unit = unit,
                                                          width = width * scale,
                                                          height = height * scale))
    circularSegments, straightSegments = searchCircularSegments(trkData)
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
                '<circle cx="{}" cy="{}" r="0.5" style="stroke:none;fill:white"/>\n'.format(x, y)
            )
        fp.write('</g>\n')
    if len(circularSegments) > 0:
        fp.write('<g>\n')
        for segment in circularSegments:
            fp.write('<path d="M')
            for x, y in generateScaledSegment(segment, height, scale):
                fp.write(' {} {}'.format(x, y))
            fp.write(' Z" style="fill:none;stroke:white"/>\n')
        fp.write('</g>\n')
    if len(straightSegments) > 0:
        fp.write('<g>\n')
        for segment in straightSegments:
            fp.write('<path d="M')
            for x, y in generateScaledSegment(segment, height, scale):
                fp.write(' {} {}'.format(x, y))
            fp.write('" style="fill:none;stroke:white"/>\n')
        fp.write('</g>\n')
    fp.write('</svg>\n')
    fp.close()
def GeoJSON_to_SVG(cx, circuit):
    def nearestpoint(waypoint, coords):
        np = -1
        print("waypoint", waypoint[0], "lon", waypoint[1], "lat", waypoint[2])
        for i in range(len(coords)):
            lon1 = waypoint[1]
            lat1 = waypoint[2]
            coord1 = (lat1, lon1)
            lon2 = coords[i][0]
            lat2 = coords[i][1]
            coord2 = (lat2, lon2)
            d = great_circle(coord1, coord2).km
            print(i, "lon", coords[i][0], "lat", coords[i][1])
        return np
    custom_symbol = "Red"
    with open('Circuits/GeoJSON/' + circuit + '2.geojson', 'r') as infile:
        geodata = json.load(infile)
    gpx = gpxpy.gpx.GPX()
    for feature in geodata['features']:
        geom = feature['geometry']
        properties = feature['properties']
        process_geometry(geom, properties, custom_symbol, gpx, circuit)
    with open('Circuits/GPX/' + circuit + '.gpx', 'w') as outfile:
        outfile.write( gpx.to_xml())
    origtrkData, wptData = parseGpx("Circuits/GPX/" + circuit + ".gpx")
    if origtrkData == []:
        print('No data to convert. Terminating.', file = sys.stderr)
        sys.exit(1)
    trkData = calcProjection(origtrkData)
    trkData, width, height = moveProjectedData(trkData)
    np = nearestpoint(wptData[0], origtrkData[0])
    writeSvgData(trkData, width, height, "SVG/" + circuit + "x.svg")
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
#print(cwd)
circuitsdata = []
file_to_open = "Data/Circuits2027.csv"
with open(file_to_open, 'r') as file:
    csvreader = csv.reader(file, delimiter = ';')
    count = 0
    for row in csvreader:
        circuitsdata.append(row)
        count += 1
#print(count)
for i in range(len(circuitsdata)):
    if circuitsdata[i][1] == "sg-2008":
    #if True:
        cx = i
        #print(cx, "GPX_to_SVG", circuitsdata[cx][1])
        GeoJSON_to_SVG(cx, circuitsdata[cx][1])
key = input("Wait")
