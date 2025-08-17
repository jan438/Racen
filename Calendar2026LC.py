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
alleventslines = []
raceevents = []
circuitsdata = []
weekdaycairo = [6, 0, 1, 2, 3, 4, 5]
scalingcar = 0.028
scalingqcar = 0.28
scalingtcar = 0.28
scalingscar = 0.024
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
file_to_open = "Data/Circuits2026.csv"
with open(file_to_open, 'r') as file:
    csvreader = csv.reader(file, delimiter = ';')
    count = 0
    for row in csvreader:
        circuitsdata.append(row)
        count += 1
sortondate()
eventcal = "Calendar/Formule12026.ics"
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
raceevent = lookupraceevent(3, 8)
if raceevent is not None:
    starttime = raceevent.starttime
    localtime = converttimetztolocal(starttime)
    print(raceevent.summary, raceevent.location, starttime, raceevent.categories, raceevent.geo, starttime, localtime)
else:
    print("Not found")
pdfmetrics.registerFont(TTFont('LiberationSerif', 'LiberationSerif-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSerifBold', 'LiberationSerif-Bold.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSerifItalic', 'LiberationSerif-Italic.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSerifBoldItalic', 'LiberationSerif-BoldItalic.ttf'))
my_canvas = canvas.Canvas("PDF/Calendar2026LC.pdf")
my_canvas.setFillColor(HexColor(outsidearea))
my_canvas.rect(left_padding, bottom_padding, width, height, fill=1)
my_canvas.setFont(calfont, 25)
my_canvas.setTitle("Calendar 2026")

row = 0
col = 2
flagoffset_x = 81
flagoffset_y = 90
circuit_x = 10
circuit_y = 10
linkx1 = 0
linky1 = 0
linkx2 = 10
linky2 = 10
linkarea = (linkx1, linky1, linkx2, linky2)
geolocator = Nominatim(user_agent="my_geopy_app")
colwidth = 147
rowheight = 120
my_canvas.setFont(calfont, 12)
bottommargin = 30
leftmargin = 8.0
circuitscale = 0.06
row = 5
col = 0
eventwidth = 137
eventheight = 112
my_canvas.setFillColor(HexColor(circuitarea))
image = "Circuits/Location/Australia_location_map.png"
my_canvas.drawImage(image, 0 * colwidth + leftmargin, 5 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/AUtw.svg", 0.5), my_canvas, flagoffset_x + 0 * colwidth + leftmargin, flagoffset_y + 5 * rowheight + bottommargin + 10)
my_canvas.circle(0 * colwidth + leftmargin + 105, 5 * rowheight + bottommargin + 10 + 20, 4.0, stroke = 0, fill = 1)
circuit_x = 60
circuit_y = 30
renderPDF.draw(scaleSVG("SVG/AlbertParkLC.svg", circuitscale), my_canvas, circuit_x + 0 * colwidth + leftmargin, circuit_y + 5 * rowheight + bottommargin + 10)
image = "Circuits/Location/China_location_map.png"
my_canvas.drawImage(image, 1 * colwidth + leftmargin, 5 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/CNtw.svg", 0.5), my_canvas, flagoffset_x + 1 * colwidth + leftmargin, flagoffset_y + 5 * rowheight + bottommargin + 10)
my_canvas.circle(1 * colwidth + leftmargin + 90, 5 * rowheight + bottommargin + 20 + 35, 4.0, stroke = 0, fill = 1)
circuit_x = 60
circuit_y = 30
renderPDF.draw(scaleSVG("SVG/ShanghaiLC.svg", circuitscale), my_canvas, circuit_x + 1 * colwidth + leftmargin, circuit_y + 5 * rowheight + bottommargin + 10)
image = "Circuits/Location/Japan_location_map.png"
my_canvas.drawImage(image, 2 * colwidth + leftmargin, 5 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/JPtw.svg", 0.5), my_canvas, flagoffset_x + 2 * colwidth + leftmargin, flagoffset_y + 5 * rowheight + bottommargin + 10)
my_canvas.circle(2 * colwidth + leftmargin + 73, 5 * rowheight + bottommargin + 10 + 45, 4.0, stroke = 0, fill = 1)
circuit_x = 60
circuit_y = 30
renderPDF.draw(scaleSVG("SVG/SuzukaLC.svg", circuitscale), my_canvas, circuit_x + 2 * colwidth + leftmargin, circuit_y + 5 * rowheight + bottommargin + 10)
image = "Circuits/Location/Bahrain_location_map.png"
my_canvas.drawImage(image, 3 * colwidth + leftmargin, 5 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/BHtw.svg", 0.5), my_canvas, flagoffset_x + 3 * colwidth + leftmargin, flagoffset_y + 5 * rowheight + bottommargin + 10)
my_canvas.circle(3 * colwidth + leftmargin + 55, 5 * rowheight + bottommargin + 10 + 56, 4.0, stroke = 0, fill = 1)
circuit_x = 60
circuit_y = 30
renderPDF.draw(scaleSVG("SVG/BahrainLC.svg", circuitscale), my_canvas, circuit_x + 3 * colwidth + leftmargin, circuit_y + 5 * rowheight + bottommargin + 10)

image = "Circuits/Location/Saudi_Arabia_location_map.png"
my_canvas.drawImage(image, 0 * colwidth + leftmargin, 4 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/SAtw.svg", 0.5), my_canvas, flagoffset_x + 0 * colwidth + leftmargin, flagoffset_y + 4 * rowheight + bottommargin + 10)
my_canvas.circle(0 * colwidth + leftmargin + 17, 4 * rowheight + bottommargin + 10 + 35, 4.0, stroke = 0, fill = 1)
circuit_x = 60
circuit_y = 30
renderPDF.draw(scaleSVG("SVG/JeddahCornicheLC.svg", circuitscale), my_canvas, circuit_x + 0 * colwidth + leftmargin, circuit_y + 4 * rowheight + bottommargin + 10)
image = "Circuits/Location/USA_Florida_location_map.png"
my_canvas.drawImage(image, 1 * colwidth + leftmargin, 4 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/UStw.svg", 0.5), my_canvas, flagoffset_x + 1 * colwidth + leftmargin, flagoffset_y + 4 * rowheight + bottommargin + 10)
my_canvas.circle(1 * colwidth + leftmargin + 130, 4 * rowheight + bottommargin + 10 + 25, 4.0, stroke = 0, fill = 1)
circuit_x = 60
circuit_y = 30
renderPDF.draw(scaleSVG("SVG/MiamiLC.svg", circuitscale), my_canvas, circuit_x + 1 * colwidth + leftmargin, circuit_y + 4 * rowheight + bottommargin + 10)
image = "Circuits/Location/Canada_location_map.png"
my_canvas.drawImage(image, 2 * colwidth + leftmargin, 4 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/CAtw.svg", 0.5), my_canvas, flagoffset_x + 2 * colwidth + leftmargin, flagoffset_y + 4 * rowheight + bottommargin + 10)
my_canvas.circle(2 * colwidth + leftmargin + 99, 4 * rowheight + bottommargin + 10 + 15, 4.0, stroke = 0, fill = 1)
circuit_x = 60
circuit_y = 30
renderPDF.draw(scaleSVG("SVG/GillesVilleneuveLC.svg", circuitscale), my_canvas, circuit_x + 2 * colwidth + leftmargin, circuit_y + 4 * rowheight + bottommargin + 10)
image = "Circuits/Location/Monaco_location_map.png"
my_canvas.drawImage(image, 3 * colwidth + leftmargin, 4 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/MCtw.svg", 0.5), my_canvas, flagoffset_x + 3 * colwidth + leftmargin, flagoffset_y + 4 * rowheight + bottommargin + 10)
my_canvas.circle(3 * colwidth + leftmargin + 60, 4 * rowheight + bottommargin + 10 + 55, 4.0, stroke = 0, fill = 1)
circuit_x = 60
circuit_y = 30
renderPDF.draw(scaleSVG("SVG/MonacoLC.svg", circuitscale), my_canvas, circuit_x + 3 * colwidth + leftmargin, circuit_y + 4 * rowheight + bottommargin + 10)

image = "Circuits/Location/Spain_location_map.png"
my_canvas.drawImage(image, 0 * colwidth + leftmargin, 3 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/EStw.svg", 0.5), my_canvas, flagoffset_x + 0 * colwidth + leftmargin, flagoffset_y + 3 * rowheight + bottommargin + 10)
my_canvas.circle(0 * colwidth + leftmargin + 115, 3 * rowheight + bottommargin + 10 + 75, 4.0, stroke = 0, fill = 1)
circuit_x = 60
circuit_y = 30
renderPDF.draw(scaleSVG("SVG/CatalunyaLC.svg", circuitscale), my_canvas, circuit_x + 0 * colwidth + leftmargin, circuit_y + 3 * rowheight + bottommargin + 10)
image = "Circuits/Location/Austria_location_map.png"
my_canvas.drawImage(image, 1 * colwidth + leftmargin, 3 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/ATtw.svg", 0.5), my_canvas, flagoffset_x + 1 * colwidth + leftmargin, flagoffset_y + 3 * rowheight + bottommargin + 10)
my_canvas.circle(1 * colwidth + leftmargin + 85, 3 * rowheight + bottommargin + 10 + 40, 4.0, stroke = 0, fill = 1)
circuit_x = 60
circuit_y = 30
renderPDF.draw(scaleSVG("SVG/RedBullRingLC.svg", circuitscale), my_canvas, circuit_x + 1 * colwidth + leftmargin, circuit_y + 3 * rowheight + bottommargin + 10)
image = "Circuits/Location/United_Kingdom_location_map.png"
my_canvas.drawImage(image, 2 * colwidth + leftmargin, 3 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/GBtw.svg", 0.5), my_canvas, flagoffset_x + 2 * colwidth + leftmargin, flagoffset_y + 3 * rowheight + bottommargin + 10)
my_canvas.circle(2 * colwidth + leftmargin + 105, 3 * rowheight + bottommargin + 40 + 5, 4.0, stroke = 0, fill = 1)
circuit_x = 60
circuit_y = 30
renderPDF.draw(scaleSVG("SVG/SilverstoneLC.svg", circuitscale), my_canvas, circuit_x + 2 * colwidth + leftmargin, circuit_y + 3 * rowheight + bottommargin + 10)
image = "Circuits/Location/Belgium_location_map.png"
my_canvas.drawImage(image, 3 * colwidth + leftmargin, 3 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/BEtw.svg", 0.5), my_canvas, flagoffset_x + 3 * colwidth + leftmargin, flagoffset_y + 3 * rowheight + bottommargin + 10)
my_canvas.circle(3 * colwidth + leftmargin + 105, 3 * rowheight + bottommargin + 10 + 59, 4.0, stroke = 0, fill = 1)
circuit_x = 60
circuit_y = 30
renderPDF.draw(scaleSVG("SVG/SpaFrancorchampsLC.svg", circuitscale), my_canvas, circuit_x + 3 * colwidth + leftmargin, circuit_y + 3 * rowheight + bottommargin + 10)

image = "Circuits/Location/Hungary_location_map.png"
my_canvas.drawImage(image, 0 * colwidth + leftmargin, 2 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/HUtw.svg", 0.5), my_canvas, flagoffset_x + 0 * colwidth + leftmargin, flagoffset_y + 2 * rowheight + bottommargin + 10)
my_canvas.circle(0 * colwidth + leftmargin + 58, 2 * rowheight + bottommargin + 10 + 60, 4.0, stroke = 0, fill = 1)
circuit_x = 60
circuit_y = 30
renderPDF.draw(scaleSVG("SVG/HungaroringLC.svg", circuitscale), my_canvas, circuit_x + 0 * colwidth + leftmargin, circuit_y + 2 * rowheight + bottommargin + 10)
image = "Circuits/Location/Netherlands_location_map.png"
my_canvas.drawImage(image, 1 * colwidth + leftmargin, 2 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/NLtw.svg", 0.5), my_canvas, flagoffset_x + 1 * colwidth + leftmargin, flagoffset_y + 2 * rowheight + bottommargin + 10)
my_canvas.circle(1 * colwidth + leftmargin + 48, 2 * rowheight + bottommargin + 10 + 65, 4.0, stroke = 0, fill = 1)
circuit_x = 60
circuit_y = 30
renderPDF.draw(scaleSVG("SVG/ZandvoortLC.svg", circuitscale), my_canvas, circuit_x + 1 * colwidth + leftmargin, circuit_y + 2 * rowheight + bottommargin + 10)
image = "Circuits/Location/Italy_location_map.png"
my_canvas.drawImage(image, 2 * colwidth + leftmargin, 2 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/ITtw.svg", 0.5), my_canvas, flagoffset_x + 2 * colwidth + leftmargin, flagoffset_y + 2 * rowheight + bottommargin + 10)
my_canvas.circle(2 * colwidth + leftmargin + 35, 2 * rowheight + bottommargin + 10 + 88, 4.0, stroke = 0, fill = 1)
circuit_x = 60
circuit_y = 30
renderPDF.draw(scaleSVG("SVG/MonzaLC.svg", circuitscale), my_canvas, circuit_x + 2 * colwidth + leftmargin, circuit_y + 2 * rowheight + bottommargin + 10)
image = "Circuits/Location/Spain_location_map.png"
my_canvas.drawImage(image, 3 * colwidth + leftmargin, 2 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/EStw.svg", 0.5), my_canvas, flagoffset_x + 3 * colwidth + leftmargin, flagoffset_y + 2 * rowheight + bottommargin + 10)
my_canvas.circle(3 * colwidth + leftmargin + 55, 2 * rowheight + bottommargin + 10 + 55, 4.0, stroke = 0, fill = 1)
circuit_x = 60
circuit_y = 30
renderPDF.draw(scaleSVG("SVG/MadringLC.svg", circuitscale), my_canvas, circuit_x + 3 * colwidth + leftmargin, circuit_y + 2 * rowheight + bottommargin + 10)

image = "Circuits/Location/Azerbaijan_location_map.png"
my_canvas.drawImage(image, 0 * colwidth + leftmargin, 1 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/AZtw.svg", 0.5), my_canvas, flagoffset_x + 0 * colwidth + leftmargin, flagoffset_y + 1 * rowheight + bottommargin + 10)
my_canvas.circle(0 * colwidth + leftmargin + 100, 1 * rowheight + bottommargin + 10 + 55, 4.0, stroke = 0, fill = 1)
circuit_x = 55
circuit_y = 15
renderPDF.draw(scaleSVG("SVG/BakuCityLC.svg", circuitscale), my_canvas, circuit_x + 0 * colwidth + leftmargin, circuit_y + 1 * rowheight + bottommargin + 10)
image = "Circuits/Location/Singapore_location_map.png"
my_canvas.drawImage(image, 1 * colwidth + leftmargin, 1 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/SGtw.svg", 0.5), my_canvas, flagoffset_x + 1 * colwidth + leftmargin, flagoffset_y + 1 * rowheight + bottommargin + 10)
my_canvas.circle(1 * colwidth + leftmargin + 75, 1 * rowheight + bottommargin + 10 + 45, 4.0, stroke = 0, fill = 1)
circuit_x = 55
circuit_y = 15
renderPDF.draw(scaleSVG("SVG/MarinaBayLC.svg", circuitscale), my_canvas, circuit_x + 1 * colwidth + leftmargin, circuit_y + 1 * rowheight + bottommargin + 10)
image = "Circuits/Location/USA_Texas_location_map.png"
my_canvas.drawImage(image, 2 * colwidth + leftmargin, 1 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/UStw.svg", 0.5), my_canvas, flagoffset_x + 2 * colwidth + leftmargin, flagoffset_y + 1 * rowheight + bottommargin + 10)
my_canvas.circle(2 * colwidth + leftmargin + 85, 1 * rowheight + bottommargin + 10 + 42, 4.0, stroke = 0, fill = 1)
circuit_x = 55
circuit_y = 15
renderPDF.draw(scaleSVG("SVG/theAmericasLC.svg", circuitscale), my_canvas, circuit_x + 2 * colwidth + leftmargin, circuit_y + 1 * rowheight + bottommargin + 10)
image = "Circuits/Location/Mexico_location_map.png"
my_canvas.drawImage(image, 3 * colwidth + leftmargin, 1 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/MXtw.svg", 0.5), my_canvas, flagoffset_x + 3 * colwidth + leftmargin, flagoffset_y + 1 * rowheight + bottommargin + 10)
my_canvas.circle(3 * colwidth + leftmargin + 75, 1 * rowheight + bottommargin + 10 + 55, 4.0, stroke = 0, fill = 1)
circuit_x = 55
circuit_y = 15
renderPDF.draw(scaleSVG("SVG/HermanosRodríguezLC.svg", circuitscale), my_canvas, circuit_x + 3 * colwidth + leftmargin, circuit_y + 1 * rowheight + bottommargin + 10)

image = "Circuits/Location/Brazil_location_map.png"
my_canvas.drawImage(image, 0 * colwidth + leftmargin, 0 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/BRtw.svg", 0.5), my_canvas, flagoffset_x + 0 * colwidth + leftmargin, flagoffset_y + 0 * rowheight + bottommargin + 10)
my_canvas.circle(0 * colwidth + leftmargin + 92, 0 * rowheight + bottommargin + 10 + 33, 4.0, stroke = 0, fill = 1)
circuit_x = 55
circuit_y = 15
renderPDF.draw(scaleSVG("SVG/JoseCarlosPaceLC.svg", circuitscale), my_canvas, circuit_x + 0 * colwidth + leftmargin, circuit_y + 0 * rowheight + bottommargin + 10)
image = "Circuits/Location/USA_Nevada_location_map.png"
my_canvas.drawImage(image, 1 * colwidth + leftmargin, 0 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/UStw.svg", 0.5), my_canvas, flagoffset_x + 1 * colwidth + leftmargin, flagoffset_y + 0 * rowheight + bottommargin + 10)
my_canvas.circle(1 * colwidth + leftmargin + 115, 0 * rowheight + bottommargin + 10 + 15, 4.0, stroke = 0, fill = 1)
circuit_x = 55
circuit_y = 15
renderPDF.draw(scaleSVG("SVG/LasVegasLC.svg", circuitscale), my_canvas, circuit_x + 1 * colwidth + leftmargin, circuit_y + 0 * rowheight + bottommargin + 10)
image = "Circuits/Location/Qatar_location_map.png"
my_canvas.drawImage(image, 2 * colwidth + leftmargin, 0 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/QAtw.svg", 0.5), my_canvas, flagoffset_x + 2 * colwidth + leftmargin, flagoffset_y + 0 * rowheight + bottommargin + 10)
my_canvas.circle(2 * colwidth + leftmargin + 75, 0 * rowheight + bottommargin + 10 + 65, 4.0, stroke = 0, fill = 1)
circuit_x = 55
circuit_y = 15
renderPDF.draw(scaleSVG("SVG/LusailLC.svg", circuitscale), my_canvas, circuit_x + 2 * colwidth + leftmargin, circuit_y + 0 * rowheight + bottommargin + 10)
image = "Circuits/Location/United_Arab_Emirates_location_map.png"
my_canvas.drawImage(image, 3 * colwidth + leftmargin, 0 * rowheight + bottommargin + 10, width=eventwidth, height=eventheight, mask=None)
renderPDF.draw(scaleSVG("Flags/AEtw.svg", 0.5), my_canvas, flagoffset_x + 3 * colwidth + leftmargin, flagoffset_y + 0 * rowheight + bottommargin + 10)
my_canvas.circle(3 * colwidth + leftmargin + 85, 0 * rowheight + bottommargin + 10 + 65, 4.0, stroke = 0, fill = 1)
circuit_x = 55
circuit_y = 15
renderPDF.draw(scaleSVG("SVG/YasMarinaLC.svg", circuitscale), my_canvas, circuit_x + 3 * colwidth + leftmargin, circuit_y + 0 * rowheight + bottommargin + 10)

row = 6
col = 0
my_canvas.setFillColor(HexColor(outsidearea))
my_canvas.setStrokeColor(HexColor(outsidearea))
my_canvas.setLineWidth(1)
for i in range(24):
    p = my_canvas.beginPath()
    p.arc(leftmargin + col * colwidth - 0.1, row * rowheight + 12.0, leftmargin + col * colwidth - 0.1 + arcdim, row * rowheight + 12.0 + arcdim, startAng = 90, extent = 90)
    p.lineTo(leftmargin + col * colwidth - 0.1, row * rowheight + 12.0 + arcdim)
    my_canvas.drawPath(p, fill=1, stroke=0)
    p = my_canvas.beginPath()
    p.arc(leftmargin + col * colwidth + 117.9, row * rowheight - 80.0, leftmargin + col * colwidth + 137.9, row * rowheight - 60.0, startAng = 270, extent = 90)
    p.lineTo(leftmargin + col * colwidth + 137.9, row * rowheight - 80.0)
    my_canvas.drawPath(p, fill = 1, stroke = 0)
    col += 1
    if col == 4:
        col = 0
        row -= 1

drawing = svg2rlg('SVG/F1.svg')
renderPDF.draw(drawing, my_canvas, 100, 800)
my_canvas.setFont(calfont, 30)
my_canvas.setFillColor(HexColor("#000000"))
my_canvas.drawString(100, 775, "2026 Calendar")
row = 6
col = 0
caloffsetx = 54.3
caloffsety = 10
clockoffsetx = 102.9
clockoffsety = 88
my_canvas.setStrokeColor(black)
my_canvas.setLineWidth(1)
for i in range(len(raceevents)):
    raceevent = raceevents[i]
    if raceevent is not None:
        subsummary = raceevent.summary[:10]
        if subsummary == "Practice 1":
            my_canvas.line(leftmargin + col * colwidth + 9.9, row * rowheight + 32.0, leftmargin + col * colwidth + colwidth - 10.1, row * rowheight + 32.0)
            p = my_canvas.beginPath()
            p.arc(leftmargin + col * colwidth - 0.1, row * rowheight + 12.0, leftmargin + col * colwidth - 0.1 + arcdim, row * rowheight + 12.0 + arcdim, startAng = 90, extent = 90)
            my_canvas.drawPath(p, fill = 0, stroke = 1)
            my_canvas.setFillColor(HexColor(text1))
            my_canvas.line(leftmargin + col * colwidth - 0.1, row * rowheight - 80.0, leftmargin + col * colwidth - 0.1, row * rowheight + 22.0)   
            my_canvas.line(leftmargin + col * colwidth - 0.1, row * rowheight - 80, leftmargin + col * colwidth + 127.9, row * rowheight - 80)
            p = my_canvas.beginPath()
            p.arc(leftmargin + col * colwidth + 117.9, row * rowheight - 80.0, leftmargin + col * colwidth + 137.9, row * rowheight - 60.0, startAng = 270, extent = 90)
            my_canvas.drawPath(p, fill = 0, stroke = 1)
            my_canvas.line(leftmargin + col * colwidth + 137.9, row * rowheight + 32, leftmargin + col * colwidth + 137.9, row * rowheight - 70.0)
            renderPDF.draw(scaleSVG("SVG/calendar-blank.svg", 0.65), my_canvas, leftmargin + caloffsetx + col * colwidth, caloffsety + row * rowheight)
            my_canvas.setFont(calfont, 11)
            result = raceevent.summary.split("(")
            result = result[0][:-1]
            if result[:8] == "Practice":
                print(result)
            my_canvas.drawString(leftmargin + col * colwidth + 5.9, row * rowheight - 4, result)
            [hour,minute] = converttimetztolocalclock(raceevent.starttime)
            strhour = str(hour)
            if len(strhour) == 1:
                strhour = "0" + strhour
            strminute = str(minute)
            if len(strminute) == 1:
                strminute = "0" + strminute
            startevent = strhour + ":" + strminute
            my_canvas.drawString(leftmargin + col * colwidth + 105.9, row * rowheight - 4, startevent)
            i = i + 1
            raceevent = raceevents[i] 
            result = raceevent.summary.split("(")
            result = result[0][:-1]
            my_canvas.drawString(leftmargin + col * colwidth + 5.9, row * rowheight - 15, result)
            [hour,minute] = converttimetztolocalclock(raceevent.starttime)
            strhour = "{:02d}".format(hour)
            strminute = "{:02d}".format(minute)
            startevent = strhour + ":" + strminute
            my_canvas.drawString(leftmargin + col * colwidth + 105.9, row * rowheight - 15, startevent)
            i = i + 1
            raceevent = raceevents[i]
            result = raceevent.summary.split("(")
            result = result[0][:-1]
            my_canvas.drawString(leftmargin + col * colwidth + 5.9, row * rowheight - 34, result)
            [hour,minute] = converttimetztolocalclock(raceevent.starttime)
            strhour = "{:02d}".format(hour)
            strminute = "{:02d}".format(minute)
            startevent = strhour + ":" + strminute
            my_canvas.drawString(leftmargin + col * colwidth + 105.9, row * rowheight - 34, startevent)
            i = i + 1
            raceevent = raceevents[i]
            result = raceevent.summary.split("(")
            result = result[0][:-1]
            my_canvas.drawString(leftmargin + col * colwidth + 5.9, row * rowheight - 45, result)
            [hour,minute] = converttimetztolocalclock(raceevent.starttime)
            strhour = "{:02d}".format(hour)
            strminute = "{:02d}".format(minute)
            startevent = strhour + ":" + strminute
            my_canvas.drawString(leftmargin + col * colwidth + 105.9, row * rowheight - 45, startevent)
            i = i + 1
            raceevent = raceevents[i]
            result = raceevent.summary.split("(")
            result = result[1][:-1]
            result = result[14:]
            my_canvas.setFont(calfont, 12)
            my_canvas.drawString(leftmargin + col * colwidth + 5.9, row * rowheight - 75, result)
            [hour,minute] = converttimetztolocalclock(raceevent.starttime)
            strhour = str(hour)
            if len(strhour) == 1:
                strhour = "0" + strhour
            renderPDF.draw(scaleSVG("Clocks/" + strhour + "00" + "tw.svg", 0.5), my_canvas, leftmargin + clockoffsetx + col * colwidth, clockoffsety + row * rowheight - 75)
            my_canvas.setFont(calfont, 8)
            my_canvas.setFillColor(HexColor("#ffffff"))
            my_canvas.drawString(leftmargin + caloffsetx + 3.5 + col * colwidth, caloffsety + 16.2 + row * rowheight, monthnames[raceevent.month - 1])
            my_canvas.setFillColor(HexColor(text2))
            my_canvas.setFont(calfont, 11)
            my_canvas.drawString(leftmargin + col * colwidth + 5.9, row * rowheight - 65, raceevent.location)
            my_canvas.setFillColor(HexColor(text1))
            my_canvas.setFont(calfont, 14)
            my_canvas.drawString(leftmargin + caloffsetx + 1.8 + col * colwidth, caloffsety + 1.5 + row * rowheight, str(raceevent.day))
            col += 1
            if col == 4:
                col = 0
                row = row - 1
                if row < 0:
                    break
my_canvas.save()
key = input("Wait")
