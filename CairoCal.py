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
from svgwrite import Drawing
import cairosvg
from ics import Calendar, Event

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
            break
    return raceevent
def generate_calendar_svg(year, month, start_day=0, file_name="calendar.svg", as_text=False):
    output_dir = "SVG"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, file_name)
    year = year
    month = month
    cal = calendar.Calendar(firstweekday=start_day)
    month_days = cal.monthdayscalendar(year, month)
    month_name = calendar.month_name[month]
    cell_width = 60
    cell_height = 50
    header_font_size = 45
    line_spacing = 60
    day_font_size = 32
    width = cell_width * 7
    height = cell_height * (6 + 2) + line_spacing + 20
    dwg = Drawing(file_path, size=(width, height))
    y_offset = 10
    add_text(
        dwg,
        month_name,
        (width / 2, y_offset + header_font_size),
        font_size=header_font_size,
        font_family="serif",
        text_anchor="middle",
        as_text=as_text,
    )
    y_offset += header_font_size + line_spacing
    days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
    if start_day != 0:
        days = days[start_day:] + days[:start_day]
    for i, day in enumerate(days):
        add_text(
            dwg,
            day,
            (i * cell_width + cell_width / 2, y_offset),
            font_size=day_font_size,
            font_family="sans-serif",
            text_anchor="middle",
            as_text=as_text,
        )
    line_y = y_offset + day_font_size + -20
    dwg.add(dwg.line(
        start=(0, line_y),
        end=(width, line_y),
        stroke="black",
        stroke_width=1
    ))
    countweeks = 0
    y_offset = line_y + 20
    for week in month_days:
        for i, day in enumerate(week):
            if day != 0:
                raceevent = lookupraceevent(month, day)
                if raceevent is not None and raceevent.categories == "Grand Prix,F1":
                    print("raceevent on these day", month, day, raceevent.categories)  
                elif raceevent is not None and raceevent.categories == "Sprint,F1":
                    print("sprintevent on these day", month, day, raceevent.categories)
                elif raceevent is not None and raceevent.categories == "Vrije Training 1,F1":
                    print("traing1event on these day", month, day, raceevent.categories)
                elif raceevent is not None and raceevent.categories == "Vrije Training 3,F1":
                    print("traing3event on these day", month, day, raceevent.categories)
                else:
                    add_text(
                        dwg,
                        str(day),
                        (i * cell_width + cell_width / 2, y_offset + cell_height / 2),
                        font_size=day_font_size,
                        font_family="sans-serif",
                        font_weight="300",
                        text_anchor="middle",
                        as_text=as_text,
                    )
        y_offset += cell_height
        countweeks = countweeks + 1
    if countweeks == 5:
        print(month_name, countweeks)
    dwg.save()
    if not as_text:
        convert_text_to_paths(file_path)
    return file_path
def add_text(dwg, text, insert, font_size=16, font_family="sans-serif", font_weight="normal", text_anchor="start", as_text=True):
    dwg.add(dwg.text(
        text,
        insert=insert,
        font_size=font_size,
        font_family=font_family,
        font_weight=font_weight,
        text_anchor=text_anchor,
    ))
def convert_text_to_paths(svg_path):
    path_svg_path = svg_path
    cairosvg.svg2svg(url=svg_path, write_to=path_svg_path)
    print(f"Text converted to paths.")

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
for i in range(12):
    file_path = generate_calendar_svg(2025, i + 1, 0, monthnames[i] + ".svg", False)
key = input("Wait")
