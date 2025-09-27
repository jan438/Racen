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
outsidearea = "#9e9e9e"
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
def lookupcircuit(description):
    cx = -1
    for j in range(len(circuitsdata)):
        if circuitsdata[j][0] == description:
            cx = j
    return cx

if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)
file_to_open = "Data/Circuits2026.csv"
with open(file_to_open, 'r') as file:
    csvreader = csv.reader(file, delimiter = ';')
    count = 0
    for row in csvreader:
        circuitsdata.append(row)
        count += 1
eventcal = "Calendar/Formule12026" + version + ".ics"
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
print("Count race events", len(raceevents))
raceevent = lookupraceevent(3, 8)
if raceevent is not None:
    starttime = raceevent.starttime
    localtime = converttimetztolocal(starttime)
    print(raceevent.summary, raceevent.location, description, starttime, starttime, localtime)
else:
    print("Not found")
pdfmetrics.registerFont(TTFont('LiberationSerif', 'LiberationSerif-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSerifBold', 'LiberationSerif-Bold.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSerifItalic', 'LiberationSerif-Italic.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSerifBoldItalic', 'LiberationSerif-BoldItalic.ttf'))
my_canvas = canvas.Canvas("PDF/Calendar2026" + version + ".pdf")
my_canvas.setFillColor(HexColor(outsidearea))
my_canvas.rect(left_padding, bottom_padding, width, height, fill=1)
my_canvas.setFont(calfont, 25)
my_canvas.setTitle("Calendar 2026 " + version)

circuit_x = 10
circuit_y = 10
eventday1_x = 20
eventday1_y = 20
linkx1 = 0
linky1 = 0
linkx2 = 10
linky2 = 10
linkarea = (linkx1, linky1, linkx2, linky2)
colwidth = 147
rowheight = 120
my_canvas.setFont(calfont, 12)
bottommargin = 30
leftmargin = 8.0
circuitscale = 0.06
eventwidth = 137
eventheight = 112

drawing = svg2rlg('SVG/F1.svg')
renderPDF.draw(drawing, my_canvas, 100, 800)
my_canvas.setFont(calfont, 30)
my_canvas.setFillColor(HexColor("#000000"))
my_canvas.drawString(100, 775, "2026 Calendar " + version)
row = 6
col = 0
caloffsetx = 64.3
caloffsety = 10
calblank_dy = -7.0
calday_dy = -6.0
flagoffset_x = 91
flagoffset_y = 90
clockoffsetx = 112.9
clockoffsety = 88
halfmoonoffsetx = 120.0
halfmoonoffsety = 88
clock_dx = 26.5
event_dx = 12.5
event_dy = -5
stopwatchdigit_x = 5.8
stopwatchdigit_y = -3.5
poleline_y = -17.0
polelineletter_x = 5.0
polelineletter_y = -15.0
my_canvas.setStrokeColor(black)
my_canvas.setLineWidth(1)
for i in range(len(raceevents)):
    raceevent = raceevents[i]
    if raceevent is not None:
        subsummary = raceevent.summary[:10]
        if subsummary == "Practice 1":
            cx = lookupcircuit(raceevent.description)
            print(cx, raceevent.description)
            locationmap = circuitsdata[cx][5]
            image = "Circuits/Location/" + locationmap + "_location_map.png"
            my_canvas.drawImage(image, col * colwidth + leftmargin, (row - 1) * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
            countrycode = circuitsdata[cx][1][:2]
            countrycode = countrycode.upper()
            renderPDF.draw(scaleSVG("Flags/" + countrycode + "tw.svg", 0.5), my_canvas, flagoffset_x + col * colwidth + leftmargin, flagoffset_y + (row - 1) * rowheight + bottommargin + 10)
            circle_x = float(circuitsdata[cx][26])
            circle_y = float(circuitsdata[cx][27])
            my_canvas.setFillColor(HexColor(circuitarea))
            my_canvas.circle(col * colwidth + leftmargin + circle_x, (row - 1) * rowheight + bottommargin + 10 + circle_y, 4.0, stroke = 0, fill = 1)
            if rastermode:
                my_canvas.circle(col * colwidth + leftmargin + circle_x, (row - 1) * rowheight + bottommargin + 10 + circle_y, 10.0, stroke = 1, fill = 0)
            circuit_x = float(circuitsdata[cx][28])
            circuit_y = float(circuitsdata[cx][29])
            renderPDF.draw(scaleSVG("SVG/" + raceevent.description + "LCC.svg", circuitscale), my_canvas, circuit_x + col * colwidth + leftmargin, circuit_y + (row - 1) * rowheight + bottommargin + 10)
            eventday1_x = float(circuitsdata[cx][30])
            eventday1_y = float(circuitsdata[cx][31])
            eventday2_x = float(circuitsdata[cx][32])
            eventday2_y = float(circuitsdata[cx][33])
            my_canvas.line(leftmargin + col * colwidth + 9.9, row * rowheight + 32.0, leftmargin + col * colwidth + colwidth - 10.1, row * rowheight + 32.0)
            my_canvas.setFillColor(HexColor(text1))
            my_canvas.line(leftmargin + col * colwidth - 0.1, row * rowheight - 80.0, leftmargin + col * colwidth - 0.1, row * rowheight + 22.0)   
            my_canvas.line(leftmargin + col * colwidth - 0.1, row * rowheight - 80, leftmargin + col * colwidth + 127.9, row * rowheight - 80)
            my_canvas.line(leftmargin + col * colwidth + 137.9, row * rowheight + 32, leftmargin + col * colwidth + 137.9, row * rowheight - 70.0)
            renderPDF.draw(scaleSVG("SVG/calendar-blank.svg", 0.65), my_canvas, leftmargin + caloffsetx + col * colwidth, caloffsety + row * rowheight)
            my_canvas.setFont(calfont, 11)
            result = raceevent.summary.split("(")
            result = result[0][:-1]
            renderPDF.draw(scaleSVG("SVG/calendar-blank.svg", daycalscaling), my_canvas, leftmargin + col * colwidth + eventday1_x, row * rowheight + eventday1_y + calblank_dy)
            strraceday = str(raceevent.day)
            daywidth = pdfmetrics.stringWidth(strraceday, calfont, 11)
            dayxoffset = 0
            if raceevent.day < 10:
                dayxoffset = 0.5 * daywidth
            my_canvas.drawString(leftmargin + col * colwidth + eventday1_x + 1.5 + dayxoffset, row * rowheight + eventday1_y + calday_dy, strraceday)
            if result[:10] == "Practice 1":
                renderPDF.draw(scaleSVG("SVG/stopwatchtw.svg", stopwatchscaling), my_canvas, leftmargin + col * colwidth + eventday1_x + event_dx, row * rowheight + eventday1_y - 6.9)
                my_canvas.drawString(leftmargin + col * colwidth + eventday1_x + event_dx + stopwatchdigit_x, row * rowheight + eventday1_y + stopwatchdigit_y, "1")
                [hour,minute] = converttimetztolocalclock(raceevent.starttime)
                strhour = "{:02d}".format(hour)
                strminute = "{:02d}".format(minute)
                startevent = strhour + strminute
                renderPDF.draw(scaleSVG("Clocks/" + startevent + "tw.svg", twitterscaling), my_canvas, leftmargin + col * colwidth + eventday1_x + clock_dx, row * rowheight + eventday1_y - 6.1)
            i = i + 1
            raceevent = raceevents[i] 
            result = raceevent.summary.split("(")
            result = result[0][:-1]
            if result[:10] == "Practice 2":
                renderPDF.draw(scaleSVG("SVG/stopwatchtw.svg", stopwatchscaling), my_canvas, leftmargin + col * colwidth + eventday1_x + event_dx, row * rowheight + eventday1_y + event_dy - 17.9)
                my_canvas.drawString(leftmargin + col * colwidth + eventday1_x + event_dx + stopwatchdigit_x, row * rowheight + eventday1_y + event_dy - 11.0 + stopwatchdigit_y, "2")
                [hour,minute] = converttimetztolocalclock(raceevent.starttime)
                strhour = "{:02d}".format(hour)
                strminute = "{:02d}".format(minute)
                startevent = strhour + strminute
                renderPDF.draw(scaleSVG("Clocks/" + startevent + "tw.svg", twitterscaling), my_canvas, leftmargin + col * colwidth + eventday1_x + clock_dx, row * rowheight + eventday1_y + event_dy - 17.1)
            elif result[:17] == "Sprint Qualifying":
                renderPDF.draw(scaleSVG("SVG/poleline.svg", linescaling), my_canvas, leftmargin + col * colwidth + eventday1_x + event_dx, row * rowheight + eventday1_y + event_dy + poleline_y)
                my_canvas.drawString(leftmargin + col * colwidth + eventday1_x + event_dx + polelineletter_x, row * rowheight + eventday1_y + event_dy + polelineletter_y, "S")
                [hour,minute] = converttimetztolocalclock(raceevent.starttime)
                strhour = "{:02d}".format(hour)
                strminute = "{:02d}".format(minute)
                startevent = strhour + strminute
                renderPDF.draw(scaleSVG("Clocks/" + startevent + "tw.svg", twitterscaling), my_canvas, leftmargin + col * colwidth + eventday1_x + clock_dx, row * rowheight + eventday1_y + event_dy - 17.1) 
            i = i + 1
            raceevent = raceevents[i]
            result = raceevent.summary.split("(")
            result = result[0][:-1]
            renderPDF.draw(scaleSVG("SVG/calendar-blank.svg", daycalscaling), my_canvas, leftmargin + col * colwidth + eventday2_x, row * rowheight + eventday2_y + calblank_dy)
            strraceday = str(raceevent.day)
            daywidth = pdfmetrics.stringWidth(strraceday, calfont, 11)
            dayxoffset = 0
            if raceevent.day < 10:
                dayxoffset = 0.5 * daywidth
            my_canvas.drawString(leftmargin + col * colwidth + eventday2_x + 1.5 + dayxoffset, row * rowheight + eventday2_y + calday_dy, strraceday)
            if result[:10] == "Practice 3":
                renderPDF.draw(scaleSVG("SVG/stopwatchtw.svg", stopwatchscaling), my_canvas, leftmargin + col * colwidth + eventday2_x + event_dx, row * rowheight + eventday2_y - 6.9)
                my_canvas.drawString(leftmargin + col * colwidth + eventday2_x + event_dx + stopwatchdigit_x, row * rowheight + eventday2_y + stopwatchdigit_y, "3")
                [hour,minute] = converttimetztolocalclock(raceevent.starttime)
                strhour = "{:02d}".format(hour)
                strminute = "{:02d}".format(minute)
                startevent = strhour + strminute
                renderPDF.draw(scaleSVG("Clocks/" + startevent + "tw.svg", twitterscaling), my_canvas, leftmargin + col * colwidth + eventday2_x + clock_dx, row * rowheight + eventday2_y - 6.1)
            elif result[:10] == "Sprint":
                renderPDF.draw(scaleSVG("SVG/racecarom.svg", openmojiscaling), my_canvas, leftmargin + col * colwidth + eventday2_x + event_dx, row * rowheight + eventday2_y - 6.9)
                [hour,minute] = converttimetztolocalclock(raceevent.starttime)
                strhour = "{:02d}".format(hour)
                strminute = "{:02d}".format(minute)
                startevent = strhour + strminute
                renderPDF.draw(scaleSVG("Clocks/" + startevent + "tw.svg", twitterscaling), my_canvas, leftmargin + col * colwidth + eventday2_x + clock_dx, row * rowheight + eventday2_y - 6.1)
            i = i + 1
            raceevent = raceevents[i]
            result = raceevent.summary.split("(")
            result = result[0][:-1]
            if result[:10] == "Qualifying":
                renderPDF.draw(scaleSVG("SVG/poleline.svg", linescaling), my_canvas, leftmargin + col * colwidth + eventday2_x + event_dx, row * rowheight + eventday2_y + event_dy + poleline_y)
                my_canvas.drawString(leftmargin + col * colwidth + eventday2_x + event_dx + 5.0, row * rowheight + eventday2_y + event_dy + polelineletter_y, "R")
                [hour,minute] = converttimetztolocalclock(raceevent.starttime)
                strhour = "{:02d}".format(hour)
                strminute = "{:02d}".format(minute)
                startevent = strhour + strminute
                renderPDF.draw(scaleSVG("Clocks/" + startevent + "tw.svg", twitterscaling), my_canvas, leftmargin + col * colwidth + eventday2_x + clock_dx, row * rowheight + eventday2_y + event_dy - 17.1) 
            i = i + 1
            raceevent = raceevents[i]
            result = raceevent.summary.split("(")
            result = result[1][:-1]
            result = result[14:]
            my_canvas.setFont(calfont, 12)
            my_canvas.drawString(leftmargin + col * colwidth + 5.9, row * rowheight - 75, result)
            [hour,minute] = converttimetztolocalclock(raceevent.starttime)
            strhour = "{:02d}".format(hour)
            strminute = "{:02d}".format(minute)
            startevent = strhour + strminute
            renderPDF.draw(scaleSVG("Clocks/" + startevent + "tw.svg", 0.5), my_canvas, leftmargin + clockoffsetx + col * colwidth, clockoffsety + row * rowheight - 75)
            if hour < 12:
                renderPDF.draw(scaleSVG("Clocks/halfmoontw.svg", 0.3), my_canvas, leftmargin + halfmoonoffsetx + col * colwidth, halfmoonoffsety + row * rowheight - 75)
            my_canvas.setFont(calfont, 8)
            my_canvas.setFillColor(HexColor("#ffffff"))
            my_canvas.drawString(leftmargin + caloffsetx + 3.5 + col * colwidth, caloffsety + 16.2 + row * rowheight, monthnames[raceevent.month - 1])
            my_canvas.setFillColor(HexColor(text2))
            my_canvas.setFont(calfont, 11)
            my_canvas.drawString(leftmargin + col * colwidth + 5.9, row * rowheight - 65, raceevent.location)
            my_canvas.setFillColor(HexColor(text1))
            my_canvas.setFont(calfont, 14)
            strraceday = str(raceevent.day)
            daywidth = pdfmetrics.stringWidth(strraceday, calfont, 14)
            dayxoffset = 0
            if raceevent.day < 10:
                dayxoffset = 0.5 * daywidth
            my_canvas.drawString(leftmargin + caloffsetx + 4.0 + col * colwidth + dayxoffset, caloffsety + 3.0 + row * rowheight, strraceday)
            col += 1
            if col == 4:
                col = 0
                row = row - 1
                if row < 0:
                    break
                    
my_canvas.setFillColor(HexColor("#cecece"))                    
my_canvas.rect(10.0, 5.0, 500.0, 25.0, fill=1)
my_canvas.setFillColor(HexColor(text1))
renderPDF.draw(scaleSVG("SVG/stopwatchtw.svg", stopwatchscaling), my_canvas, leftmargin + 10.0, 10.0)
my_canvas.drawString(leftmargin + 30.0, 10.0, "Practice")
renderPDF.draw(scaleSVG("SVG/poleline.svg", linescaling), my_canvas, leftmargin + 110, 10.0)
my_canvas.drawString(leftmargin + 130.0, 10.0, "Qualifying")
renderPDF.draw(scaleSVG("SVG/racecarom.svg", openmojiscaling), my_canvas, leftmargin + 210.0, 10.0)
my_canvas.drawString(leftmargin + 230.0, 10.0, "Sprint")
my_canvas.setFillColor(HexColor(circuitarea))
my_canvas.circle(leftmargin + 310.0, 15.0, 4.0, stroke = 0, fill = 1)
my_canvas.setFillColor(HexColor(text1))
my_canvas.drawString(leftmargin + 330.0, 10.0, "Location")
renderPDF.draw(scaleSVG("Clocks/halfmoontw.svg", halfmoonlegendascaling), my_canvas, leftmargin + 410.0, 10.0)
my_canvas.drawString(leftmargin + 430.0, 10.0, "Race A.M.")

row = 6
col = 0
my_canvas.setFillColor(HexColor(outsidearea))
my_canvas.setLineWidth(1)
for i in range(24):
    my_canvas.setStrokeColor(HexColor(outsidearea))
    p = my_canvas.beginPath()
    p.arc(leftmargin + col * colwidth - 0.1, row * rowheight + 12.0, leftmargin + col * colwidth - 0.1 + arcdim, row * rowheight + 12.0 + arcdim, startAng = 90, extent = 90)
    p.lineTo(leftmargin + col * colwidth - 0.1, row * rowheight + 12.0 + arcdim)
    my_canvas.drawPath(p, fill=1, stroke=0)
    p = my_canvas.beginPath()
    p.arc(leftmargin + col * colwidth + 117.9, row * rowheight - 80.0, leftmargin + col * colwidth + 137.9, row * rowheight - 60.0, startAng = 270, extent = 90)
    p.lineTo(leftmargin + col * colwidth + 137.9, row * rowheight - 80.0)
    my_canvas.drawPath(p, fill = 1, stroke = 0)
    my_canvas.line(leftmargin + col * colwidth - 0.1, row * rowheight + 32.0, leftmargin + col * colwidth + 8.0, row * rowheight + 32.0)
    my_canvas.line(leftmargin + col * colwidth + 132, row * rowheight - 80, leftmargin + col * colwidth + 140.9, row * rowheight - 80)
    my_canvas.setStrokeColor(black)
    p = my_canvas.beginPath()
    p.arc(leftmargin + col * colwidth - 0.1, row * rowheight + 12.0, leftmargin + col * colwidth - 0.1 + arcdim, row * rowheight + 12.0 + arcdim, startAng = 90, extent = 90)
    my_canvas.drawPath(p, fill = 0, stroke = 1)
    p = my_canvas.beginPath()
    p.arc(leftmargin + col * colwidth + 117.9, row * rowheight - 80.0, leftmargin + col * colwidth + 137.9, row * rowheight - 60.0, startAng = 270, extent = 90)
    my_canvas.drawPath(p, fill = 0, stroke = 1)
    col += 1
    if col == 4:
        col = 0
        row -= 1

row = 5
col = 0        
if rastermode:
    for i in range(24):
        # vertical lines
        for j in range(13):
            my_canvas.line(leftmargin + col * colwidth + (j + 1) * 10, bottommargin + 10 + row * rowheight, leftmargin + col * colwidth + (j + 1) * 10, bottommargin + 10 + (row + 1) * rowheight)
        # horizontal lines
        for j in range(11):
            my_canvas.line(leftmargin + col * colwidth, bottommargin + 10 + row * rowheight + (j + 1) * 10, leftmargin + (col + 1) * colwidth, bottommargin + 10 + row * rowheight + (j + 1) * 10)
        col += 1
        if col == 4:
            col = 0
            row -= 1

my_canvas.save()
key = input("Wait")
