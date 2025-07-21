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
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch, mm
from reportlab.graphics.shapes import *
from svglib.svglib import svg2rlg, load_svg_file, SvgRenderer
from geopy.geocoders import Nominatim

monthnames = ["Januari","Februari","Maart","April","Mei","Juni","Juli","Augustus", "September","Oktober","November","December"]
alleventslines = []
raceevents = []
circuitsdata = []
weekdaycairo = [6, 0, 1, 2, 3, 4, 5]
scalingcar = 0.028
scalingqcar = 0.28
scalingtcar = 0.28
scalingscar = 0.024

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
def converttimetztolocalclock(timetz):
    utc_string = timetz
    utc_format = "%Y%m%dT%H%M%SZ"
    local_tz = pytz.timezone('Europe/Amsterdam')
    utc_dt = datetime.strptime(utc_string, utc_format)
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
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

if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)
file_to_open = "Data/Circuits2025.csv"
with open(file_to_open, 'r') as file:
    csvreader = csv.reader(file, delimiter = ';')
    count = 0
    for row in csvreader:
        circuitsdata.append(row)
        count += 1
sortondate()
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
        weekday = weekDay(year, month, day)
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
my_canvas.drawString(100, 775, "2025")
row = 0
col = 2
leftmargin = 25
bottommargin = 50
colwidth = 180
rowheight = 160
weekheight = 19
daywidth = 22
weekwidth = 7 * daywidth
flagoffset_x = weekwidth + 4
flagoffset_y = 18
rcaroffset_y = 20
scaroffset_y = 14
qcaroffset_y = 17
tcaroffset_y = 17
linkx1 = 0
linky1 = 0
linkx2 = 10
linky2 = 10
linkarea = (linkx1, linky1, linkx2, linky2)
geolocator = Nominatim(user_agent="my_geopy_app")
for i in range(12):
    renderPDF.draw(scaleSVG("SVG/" + monthnames[11 - i] + ".svg", 0.30), my_canvas, leftmargin + col * colwidth, bottommargin + row * rowheight)
    col -= 1
    if col == -1:
        row += 1
        col = 2
for i in range(len(raceevents)):
    raceevent = raceevents[i]
    month = raceevent.month
    day = raceevent.day
    raceday = weekdaycairo[weekDay(2025, month, day)]
    if month == 1 or month == 2 or month == 3:
        row = 3
    if month == 4 or month == 5 or month == 6:
        row = 2
    if month == 7 or month == 8 or month == 9:
        row = 1
    if month == 10 or month == 11 or month == 12:
        row = 0
    col = (month - 1) % 3
    weeknr = round(day / 7 + 1)
    y_offset = (6 - weeknr) * weekheight
    if raceevent is not None and raceevent.categories == "Grand Prix,F1":
        result = raceevent.geo.split(";")
        code = lookuplocation(result[0], result[1]).upper()
        if month == 4 or month == 5 or month == 7 or month == 9 or month == 10 or month == 12:
            y_offset = y_offset + weekheight
        renderPDF.draw(scaleSVG("SVG/formula-1color.svg", scalingcar), my_canvas, leftmargin + raceday * daywidth + col * colwidth, bottommargin + row * rowheight + y_offset + rcaroffset_y)
        [hour,minute] = converttimetztolocalclock(raceevent.starttime)
        strhour = str(hour)
        strminute = str(minute)
        if len(strminute) == 1:
            strminute = "0" + strminute
        startevent = strhour + ":" + strminute
        my_canvas.setFont("Helvetica", 7)
        strday = str(day)
        if day < 10:
            strday = " " + str(day)   
        my_canvas.drawString(leftmargin + raceday * daywidth + col * colwidth - 0.3, bottommargin + row * rowheight + y_offset + rcaroffset_y, strday)
        my_canvas.setFont("Helvetica", 6)
        my_canvas.drawString(leftmargin + raceday * daywidth + col * colwidth + 8.3, bottommargin + row * rowheight + y_offset + rcaroffset_y, startevent)
        renderPDF.draw(scaleSVG("Flags/" + code + ".svg", 0.25), my_canvas, leftmargin + flagoffset_x + col * colwidth, bottommargin + row * rowheight + y_offset + flagoffset_y)
        linkx1 = leftmargin + flagoffset_x + col * colwidth
        linky1 = bottommargin + row * rowheight + y_offset + flagoffset_y
        linkx2 = linkx1 + 20
        linky2 = linky1 + 10
        linkarea = (linkx1, linky1, linkx2, linky2)
        my_canvas.linkAbsolute("Find ", raceevent.location, linkarea, addtopage = 1, thickness = 0, color = None)
    elif raceevent is not None and raceevent.categories == "Sprint,F1":
        if month == 4 or month == 7 or month == 9 or month == 10 or month == 12:
            y_offset = y_offset + weekheight
        renderPDF.draw(scaleSVG("SVG/racingcar.svg", scalingscar), my_canvas, leftmargin + raceday * daywidth + col * colwidth, bottommargin + row * rowheight + y_offset + scaroffset_y)
    elif raceevent is not None and raceevent.categories == "Vrije Training 1,F1":
        if month == 4 or month == 7 or month == 9 or month == 12:
            y_offset = y_offset + weekheight
        renderPDF.draw(scaleSVG("SVG/T.svg", scalingtcar), my_canvas, leftmargin + raceday * daywidth + col * colwidth, bottommargin + row * rowheight + y_offset + tcaroffset_y)
        my_canvas.setFont("Helvetica", 5)
        my_canvas.drawString(leftmargin + raceday * daywidth + col * colwidth + 6, bottommargin + row * rowheight + y_offset + tcaroffset_y + 8.4, "1")
    elif raceevent is not None and raceevent.categories == "Vrije Training 3,F1":
        if month == 4 or month == 7 or month == 9 or month == 10 or month == 12:
            y_offset = y_offset + weekheight
        renderPDF.draw(scaleSVG("SVG/T.svg", scalingtcar), my_canvas, leftmargin + raceday * daywidth + col * colwidth, bottommargin + row * rowheight + y_offset + tcaroffset_y)
        my_canvas.setFont("Helvetica", 5)
        my_canvas.drawString(leftmargin + raceday * daywidth + col * colwidth + 6, bottommargin + row * rowheight + y_offset + tcaroffset_y + 8.4, "3")
    elif raceevent is not None and raceevent.categories == "Kwalificatie,F1":
        if month == 4 or month == 7 or month == 9 or month == 10 or month == 12:
            y_offset = y_offset + weekheight
        y_offset = y_offset + 0.4 * weekheight
        renderPDF.draw(scaleSVG("SVG/RQ.svg", scalingqcar), my_canvas, leftmargin + raceday * daywidth + col * colwidth, bottommargin + row * rowheight + y_offset + qcaroffset_y)
    elif raceevent is not None and raceevent.categories == "Vrije Training 2,F1":
        if month == 4 or month == 7 or month == 9 or month == 12:
            y_offset = y_offset + weekheight
        y_offset = y_offset + 0.4 * weekheight
        renderPDF.draw(scaleSVG("SVG/T.svg", scalingtcar), my_canvas, leftmargin + raceday * daywidth + col * colwidth, bottommargin + row * rowheight + y_offset + tcaroffset_y)
        my_canvas.setFont("Helvetica", 5)
        my_canvas.drawString(leftmargin + raceday * daywidth + col * colwidth + 6, bottommargin + row * rowheight + y_offset + tcaroffset_y + 8.4, "2")
    elif raceevent is not None and raceevent.categories == "Sprint Qualifying,F1":
        if month == 4 or month == 7 or month == 9 or month == 12:
            y_offset = y_offset + weekheight
        y_offset = y_offset + 0.4 * weekheight
        renderPDF.draw(scaleSVG("SVG/SQ.svg", scalingqcar), my_canvas, leftmargin + raceday * daywidth + col * colwidth, bottommargin + row * rowheight + y_offset + qcaroffset_y)
my_canvas.showPage()
colwidth = 148
rowheight = 120
my_canvas.setFont("Helvetica", 12)
my_canvas.setFillColor(HexColor('#FECDE5'))
bottommargin = 30
my_canvas.rect(0, bottommargin, 4 * colwidth, 6 * rowheight + bottommargin, fill=1)
my_canvas.setFillColorRGB(0,0,0)
leftmargin = 5
row = 5
col = 0
eventwidth = 138
eventheight = 112
for i in range(24):
    image = "Circuits/Location/" + circuitsdata[i][5] + "_location_map.png"
    my_canvas.drawImage(image, col * colwidth + 2.1, row * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
    my_canvas.setFillColor(HexColor('#ffaca4'))
    print(circuitsdata[i][25], circuitsdata[i][26])
    my_canvas.circle(col * colwidth + 20, row * rowheight + bottommargin + 20, 6.0, stroke = 0, fill = 1)
    my_canvas.setFillColorRGB(0,0,0)
    col += 1
    if col == 4:
       row -= 1
       col = 0
drawing = svg2rlg('SVG/F1.svg')
renderPDF.draw(drawing, my_canvas, 100, 800)
row = 6
col = 0
clockoffsetx = 95
clockoffsety = -5
for i in range(len(raceevents)):
    raceevent = raceevents[i]
    if raceevent is not None:
        if raceevent.categories == "Vrije Training 1,F1":
            my_canvas.line(col * colwidth + 12.0, row * rowheight + 32.0, col * colwidth + colwidth - 8.0, row * rowheight + 32.0)
            p = my_canvas.beginPath()
            p.arc(col * colwidth + 2.0, row * rowheight + 12.0, col * colwidth + 22.0, row * rowheight + 32.0, startAng = 90, extent = 90)
            my_canvas.drawPath(p, fill = 0, stroke = 1)
            my_canvas.line(col * colwidth + 2.0, row * rowheight - 80.0, col * colwidth + 2.0, row * rowheight + 22.0)
                 
            my_canvas.line(col * colwidth + 2.0, row * rowheight - 80, col * colwidth + 130.0, row * rowheight - 80)
            p = my_canvas.beginPath()
            p.arc(col * colwidth + 120.0, row * rowheight - 80.0, col * colwidth + 140.0, row * rowheight - 60.0, startAng = 270, extent = 90)
            my_canvas.drawPath(p, fill = 0, stroke = 1)
            my_canvas.line(col * colwidth + 140.0, row * rowheight + 32, col * colwidth + 140.0, row * rowheight - 70.0)
            result = raceevent.summary.split("(")
            result = result[0][4:-1]
            my_canvas.drawString(leftmargin + col * colwidth, row * rowheight, result)
            [hour,minute] = converttimetztolocalclock(raceevent.starttime)
            strhour = str(hour)
            strminute = str(minute)
            if len(strminute) == 1:
                strminute = "0" + strminute
            startevent = strhour + ":" + strminute
            my_canvas.drawString(col * colwidth + 100, row * rowheight, startevent)
            my_canvas.bookmarkPage(raceevent.location, fit = "FitR", left = leftmargin + col * colwidth, bottom = row * rowheight - 100, right = leftmargin + col * colwidth + colwidth, top = row * rowheight + rowheight - 100)
            i = i + 1
            raceevent = raceevents[i] 
            result = raceevent.summary.split("(")
            result = result[0][4:-1]
            my_canvas.drawString(leftmargin + col * colwidth, row * rowheight - 15, result)
            [hour,minute] = converttimetztolocalclock(raceevent.starttime)
            strhour = str(hour)
            strminute = str(minute)
            if len(strminute) == 1:
                strminute = "0" + strminute
            startevent = strhour + ":" + strminute
            my_canvas.drawString(col * colwidth + 100, row * rowheight - 15, startevent)
            i = i + 1
            raceevent = raceevents[i]
            result = raceevent.summary.split("(")
            result = result[0][4:-1]
            my_canvas.drawString(leftmargin + col * colwidth, row * rowheight - 30, result)
            [hour,minute] = converttimetztolocalclock(raceevent.starttime)
            strhour = str(hour)
            strminute = str(minute)
            if len(strminute) == 1:
                strminute = "0" + strminute
            startevent = strhour + ":" + strminute
            my_canvas.drawString(col * colwidth + 100, row * rowheight - 30, startevent)
            i = i + 1
            raceevent = raceevents[i]
            result = raceevent.summary.split("(")
            result = result[0][4:-1]
            my_canvas.drawString(leftmargin + col * colwidth, row * rowheight - 45, result)
            [hour,minute] = converttimetztolocalclock(raceevent.starttime)
            strhour = str(hour)
            strminute = str(minute)
            if len(strminute) == 1:
                strminute = "0" + strminute
            startevent = strhour + ":" + strminute
            my_canvas.drawString(col * colwidth + 100, row * rowheight - 45, startevent)
            i = i + 1
            raceevent = raceevents[i]
            result = raceevent.summary.split("(")
            x = result[1].find("van ")
            if raceevent.location == "Imola":
                my_canvas.drawString(leftmargin + col * colwidth, row * rowheight - 75, "Imola")
            elif raceevent.location == "Austin":
                my_canvas.drawString(leftmargin + col * colwidth, row * rowheight - 75, "Austin")
            elif raceevent.location == "Las Vegas":
                my_canvas.drawString(leftmargin + col * colwidth, row * rowheight - 75, "Las Vegas")
            else:
                my_canvas.drawString(leftmargin + col * colwidth, row * rowheight - 75, result[1][x + 4:-1])
            [hour,minute] = converttimetztolocalclock(raceevent.starttime)
            strhour = str(hour)
            if len(strhour) == 1:
                strhour = "0" + strhour
            renderPDF.draw(scaleSVG("SVG/" + strhour + "00" + ".svg", 0.030), my_canvas, clockoffsetx + col * colwidth, clockoffsety + row * rowheight - 75)
            col += 1
            if col == 4:
                col = 0
                row = row - 1
                if row < 0:
                    break
my_canvas.save()
key = input("Wait")
