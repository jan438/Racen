import os
import calendar
from datetime import datetime, date, timedelta
import pytz
import os
import sys
import csv
import math
import unicodedata
import svgwrite
from ics import Calendar, Event
from svgwrite import Drawing
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from reportlab.graphics.shapes import *
from svglib.svglib import svg2rlg, load_svg_file, SvgRenderer
from geopy.geocoders import Nominatim

monthnames = ["Januari","Februari","Maart","April","Mei","Juni","Juli","Augustus", "September","Oktober","November","December"]
alleventslines = []
raceevents = []

class RaceEvent:
    def __init__(self, categories, summary, day, location, starttime, endtime, month, geo):
        self.categories = categories
        self.summary = summary
        self.day = day
        self.location = location
        self.starttime = starttime
        self.endtime = endtime
        self.month = month
        self.geo = geo
def lookuplocation(lat, lon):
    location = geolocator.reverse(lat+","+lon)
    address = location.raw['address']
    code = address.get('country_code')
    return code
def converttimetztolocal(timetz):
    utc_string = timetz
    utc_format = "%Y%m%dT%H%M%SZ"
    local_tz = pytz.timezone('Europe/Amsterdam')
    utc_dt = datetime.strptime(utc_string, utc_format)
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_dt
def lookupraceevent(month, day):
    raceevent = None
    for i in range(len(raceevents)):
        if raceevents[i].month == month and raceevents[i].day == day:
            raceevent = raceevents[i]
    return raceevent
def scaleSVG(svgfile, scaling_factor):
    svg_root = load_svg_file(svgfile)
    svgRenderer = SvgRenderer(svgfile)
    drawing = svgRenderer.render(svg_root)
    scaling_x = scaling_factor
    scaling_y = scaling_factor
    drawing.width = drawing.minWidth() * scaling_x
    drawing.height = drawing.height * scaling_y
    drawing.scale(scaling_x, scaling_y)
    return drawing

if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)
eventcal = "Calendar/Formule1.ics"
in_file = open(os.path.join(path, eventcal), 'r')
count = 0
lastpos = 0
found = 0
for line in in_file:
    newlinepos = line.find("\t\n")
    lastsubstring = line[lastpos:newlinepos]
    alleventslines.append(lastsubstring)
    count += 1
in_file.close()
print("Count eventslines", len(alleventslines))
for i in range(len(alleventslines)):
    neweventpos = alleventslines[i].find("BEGIN:VEVENT")
    summaryeventpos = alleventslines[i].find("SUMMARY")
    locationeventpos = alleventslines[i].find("LOCATION")
    categorieseventpos = alleventslines[i].find("CATEGORIES")
    geoeventpos = alleventslines[i].find("GEO")
    dtstarteventpos = alleventslines[i].find("DTSTART")
    dtendeventpos = alleventslines[i].find("DTEND")
    endeventpos = alleventslines[i].find("END:VEVENT")
    if neweventpos == 0:
        day = 0
        location = ""
        starttime = 0
        endtime = 0
        month = 0
        categories = ""
        geo = ""
    if dtstarteventpos == 0:
        eventdtstartstr = alleventslines[i][8:]
        datevaluepos = alleventslines[i].find("VALUE=DATE:")
        if datevaluepos == 8:
            eventdtstartstr = alleventslines[i][19:]
        year = int(eventdtstartstr[:4])
        month = int(eventdtstartstr[4:6])
        day = int(eventdtstartstr[6:8])
        starttime = eventdtstartstr
    if dtendeventpos == 0:
        eventdtendstr = alleventslines[i][6:]
        endtime = eventdtendstr[9:11] + ':' + eventdtendstr[11:13]
    if summaryeventpos == 0:
        summary = alleventslines[i][8:]
    if categorieseventpos == 0:
        categories = alleventslines[i][11:]
    if locationeventpos == 0:
        location = alleventslines[i][9:]
    if geoeventpos == 0:
        geo = alleventslines[i][4:]
    if endeventpos == 0:
        raceevents.append(RaceEvent(categories, summary, day, location, starttime, endtime, month, geo))
print("Count race events", len(raceevents))
raceevent = lookupraceevent(8, 31)
if raceevent is not None:
    starttime = raceevent.starttime
    localtime = converttimetztolocal(starttime)
    print(raceevent.summary, raceevent.location, starttime, raceevent.categories, raceevent.geo, starttime, localtime)
else:
    print("Not found")
my_canvas = canvas.Canvas("PDF/Calendar2025.pdf")
my_canvas.setFont("Helvetica", 25)
my_canvas.setTitle("Calendar 2025")
drawing = svg2rlg('SVG/F1.svg')
renderPDF.draw(drawing, my_canvas, 100, 800)
row = 0
col = 2
leftmargin = 25
bottommargin = 100
colwidth = 180
rowheight = 140
flagoffset = 158
linkx1 = 0
linky1 = 0
linkx2 = 10
linky2 = 10
linkarea = (linkx1, linky1, linkx2, linky2)
geolocator = Nominatim(user_agent="my_geopy_app")
for i in range(12):
    renderPDF.draw(scaleSVG("SVG/" + monthnames[11 - i] + ".svg", 0.30), my_canvas, leftmargin + col * colwidth, bottommargin + row * rowheight)
    if i == 4:
        renderPDF.draw(scaleSVG("Flags/NL.svg", 0.25), my_canvas, leftmargin + flagoffset + col * colwidth, bottommargin + row * rowheight + 3)
        renderPDF.draw(scaleSVG("SVG/racingcar.svg", 0.025), my_canvas, leftmargin + flagoffset - 22 + col * colwidth, bottommargin + row * rowheight)
        linkx1 = leftmargin + flagoffset + col * colwidth
        linky1 = bottommargin + row * rowheight + 9
        linkx2 = linkx1 + 20
        linky2 = linky1 + 10
        linkarea = (linkx1, linky1, linkx2, linky2)
        my_canvas.linkAbsolute("Find the Meaning of Life", "Meaning_of_life", linkarea, addtopage = 1, thickness = 0, color = None)
    col -= 1
    if col == -1:
        row += 1
        col = 2
for i in range(len(raceevents)):
    col = 5
    row = 5
    raceevent = raceevents[i]
    if raceevent is not None and raceevent.categories == "Grand Prix,F1":
        result = raceevent.geo.split(";")
        code = lookuplocation(result[0], result[1]).upper()
        renderPDF.draw(scaleSVG("Flags/" + code + ".svg", 0.25), my_canvas, 200, 600)
        print("1", raceevent.summary, code)
my_canvas.showPage()
drawing = svg2rlg('SVG/F1.svg')
renderPDF.draw(drawing, my_canvas, 100, 800)
for i in range(len(raceevents)):
    raceevent = raceevents[i]
    if raceevent is not None and raceevent.categories == "Grand Prix,F1":
        print("2", raceevent.summary)
renderPDF.draw(scaleSVG("SVG/time.svg", 0.025), my_canvas, 250, 30)
my_canvas.drawString(250, 60, "Zandvoort")
my_canvas.bookmarkPage("Meaning_of_life", fit = "XYZ", left = 250,top = 30, zoom = 4)
my_canvas.save()
key = input("Wait")
