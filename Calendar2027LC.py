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
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics  
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.lib.colors import blue, green, black, red, pink, gray, brown, purple, orange, yellow, white, lightgrey
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch, mm
from reportlab.graphics.shapes import *
from svglib.svglib import svg2rlg, load_svg_file, SvgRenderer
from geopy.geocoders import Nominatim

monthnames = ["jan","feb","mar","apr","may","jun","jul","aug", "sep","oct","nov","dec"]
version = "NL"
alleventslines = []
raceevents = []
circuitsdata = []
weekdaycairo = [6, 0, 1, 2, 3, 4, 5]
openmojiscaling = 0.21
halfmoonlegendascaling = 0.25
stopwatchscaling = 0.021
daycalscaling = 0.4
twitterscaling = 0.45
linescaling = 0.03
outsidearea = "#2c2c2c"
circuitarea = "#ffa981"
text1 = "#696969"
text2 = "#808080"
left_padding = 0
bottom_padding = 0
A4_width = A4[0]
A4_height = A4[1]
width = A4_width
height = A4_height
arcdim = 20.0
calfont = "LiberationSerif"
rastermode = False

class RaceEvent:
    def __init__(self, summary, day, location, description, starttime, endtime, month):
        self.summary = summary
        self.day = day
        self.location = location
        self.description = description
        self.starttime = starttime
        self.endtime = endtime
        self.month = month
def weekDay(year, month, day):
    offset = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    afterFeb = 1
    if month > 2: afterFeb = 0
    aux = year - 1700 - afterFeb
    dayOfWeek  = 5
    dayOfWeek += (aux + afterFeb) * 365                  
    dayOfWeek += aux / 4 - aux / 100 + (aux + 100) / 400     
    dayOfWeek += offset[month - 1] + (day - 1)               
    dayOfWeek %= 7
    return round(dayOfWeek)
def sortondate():
    for n in range(len(circuitsdata) - 1, 0, -1):
        swapped = False  
        for i in range(n):
            datei = circuitsdata[i][2]
            datei1 = circuitsdata[i + 1][2]
            mi = int(datei[0:2])
            di = int(datei[2:4])
            mi1 = int(datei1[0:2])
            di1 = int(datei1[2:4])
            if mi > mi1 or (mi == mi1 and di > di1):
                circuitsdata[i], circuitsdata[i + 1] = circuitsdata[i + 1], circuitsdata[i]
                swapped = True
        if not swapped:
            break
def converttimetztolocal(timetz):
    utc_string = timetz
    utc_format = "%Y%m%dT%H%M%S"
    local_tz = pytz.timezone('Europe/Amsterdam')
    utc_dt = datetime.strptime(utc_string, utc_format)
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_dt
def converttimetztolocalclock(timetz):
    utc_string = timetz
    utc_format = "%Y%m%dT%H%M%S"
    local_tz = pytz.timezone('Europe/Amsterdam')
    utc_dt = datetime.strptime(utc_string, utc_format)
    #local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    local_dt = utc_dt
    hour = local_dt.hour
    minute = local_dt.minute
    return [hour, minute]
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
def lookupcircuit(state):
    cx = -1
    for j in range(len(circuitsdata)):
        if circuitsdata[j][25] == state:
            cx = j
    return cx

if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)
file_to_open = "Data/Circuits2027.csv"
with open(file_to_open, 'r') as file:
    csvreader = csv.reader(file, delimiter = ';')
    count = 0
    for row in csvreader:
        circuitsdata.append(row)
        print(circuitsdata[count][37])
        count += 1
eventcal = "Calendar/Formule12027" + version + ".ics"
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
#print("Count eventslines", len(alleventslines))
for i in range(len(alleventslines)):
    neweventpos = alleventslines[i].find("BEGIN:VEVENT")
    summaryeventpos = alleventslines[i].find("SUMMARY")
    locationeventpos = alleventslines[i].find("LOCATION")
    descriptioneventpos = alleventslines[i].find("DESCRIPTION")
    dtstarteventpos = alleventslines[i].find("DTSTART")
    dtendeventpos = alleventslines[i].find("DTEND")
    endeventpos = alleventslines[i].find("END:VEVENT")
    if neweventpos == 0:
        day = 0
        location = ""
        description = ""
        starttime = 0
        endtime = 0
        month = 0
    if dtstarteventpos == 0:
        eventdtstartstr = alleventslines[i][8:]
        datevaluepos = alleventslines[i].find("VALUE=DATE:")
        if datevaluepos == 8:
            eventdtstartstr = alleventslines[i][19:]
        year = int(eventdtstartstr[:4])
        month = int(eventdtstartstr[4:6])
        day = int(eventdtstartstr[6:8])
        weekday = weekDay(year, month, day)
        starttime = eventdtstartstr
    if dtendeventpos == 0:
        eventdtendstr = alleventslines[i][6:]
        endtime = eventdtendstr[9:11] + ':' + eventdtendstr[11:13]
    if summaryeventpos == 0:
        summary = alleventslines[i][8:]
    if locationeventpos == 0:
        location = alleventslines[i][9:]
    if descriptioneventpos == 0:
        description = alleventslines[i][12:]
    if endeventpos == 0:
        raceevents.append(RaceEvent(summary, day, location, description, starttime, endtime, month))
#        print(i, "summary", summary, "description", description)
print("Count race events", len(raceevents))
pdfmetrics.registerFont(TTFont('LiberationSerif', 'LiberationSerif-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSerifBold', 'LiberationSerif-Bold.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSerifItalic', 'LiberationSerif-Italic.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSerifBoldItalic', 'LiberationSerif-BoldItalic.ttf'))
my_canvas = canvas.Canvas("PDF/Calendar2027" + version + ".pdf")
my_canvas.setFillColor(HexColor(outsidearea))
my_canvas.rect(left_padding, bottom_padding, width, height, fill=1)
my_canvas.setFont(calfont, 25)
my_canvas.setTitle("Calendar 2027 " + version)

circuit_x = 10
circuit_y = 10
eventday1_x = 20
eventday1_y = 20
linkx1 = 0
linky1 = 0
linkx2 = 10
linky2 = 10
linkarea = (linkx1, linky1, linkx2, linky2)
headerheight = 50
bottommargin = 10
leftmargin = 8.0
rightmargin = 8.0
circuitscale = 0.06
eventwidth = (width - leftmargin - rightmargin) / 4
eventheight = (height - bottommargin - headerheight) / 6
colwidth = eventwidth
rowheight = eventheight
flagscale = 1.0
calscale = 0.06
clockscale = 1.0

drawing = svg2rlg('SVG/F1.svg')
renderPDF.draw(drawing, my_canvas, 100, 800)
my_canvas.setFont(calfont, 30)
my_canvas.setFillColor(HexColor("#ffffff"))
my_canvas.drawString(100, 775, "2027 Calendar " + version)
row = 6
col = 0
my_canvas.setFont(calfont, 12)
for i in range(len(raceevents)):
    raceevent = raceevents[i]
    summary = raceevents[i].summary
    partindex = summary.find(" (")
    event = summary[:partindex]
    if event == "Race":
        stateindex = raceevent.summary.find("Race (Grand Prix of ")
        state = raceevent.summary[stateindex + 20:len(raceevent.summary) - 1]
        cx = lookupcircuit(state)
        sc = float(circuitsdata[cx][35])
        drawing = scaleSVG('Location/' + state + 'R.svg', sc)
        renderPDF.draw(drawing, my_canvas, col * colwidth + leftmargin + 50, (row - 1) * rowheight + bottommargin + 50)
        my_canvas.setFillColor(HexColor("#ffffff"))
        my_canvas.drawString(col * colwidth + leftmargin + 35, (row - 1) * rowheight + bottommargin + 15, raceevents[i].location)
        my_canvas.drawString(col * colwidth + leftmargin + 35, (row - 1) * rowheight + bottommargin + 5, state)
        landcode = circuitsdata[cx][1][:2].upper()
        drawing = scaleSVG('Flags/' + landcode + 'tw.svg', flagscale)
        renderPDF.draw(drawing, my_canvas, col * colwidth + leftmargin + 4, (row - 1) * rowheight + bottommargin + 0)
        drawing = scaleSVG('SVG/calendar.svg', calscale)
        renderPDF.draw(drawing, my_canvas, col * colwidth + leftmargin + 4, (row - 1) * rowheight + bottommargin + 50)
        drawing = scaleSVG('Clocks/1530om.svg', clockscale)
        renderPDF.draw(drawing, my_canvas, col * colwidth + leftmargin + 14, (row - 1) * rowheight + bottommargin + 50)
        drawing = scaleSVG('SVG/PortimãoLC.svg', 0.05)
        renderPDF.draw(drawing, my_canvas, col * colwidth + leftmargin + 60, (row - 1) * rowheight + bottommargin + 50)
        col += 1
        if col == 4:
            col = 0
            row = row - 1
my_canvas.save()
key = input("Wait")
