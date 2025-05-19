import os
import calendar
import datetime
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
def lookupraceevent(month, day):
    raceevent = None
    for i in range(len(raceevents)):
        if raceevents[i].month == month and raceevents[i].day == day:
            raceevent = raceevents[i]
    return raceevent
def generate_calendar_svg(year=None, month=None, start_day=0, file_name="calendar.svg", as_text=False):
    output_dir = "SVG"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, file_name)
    today = datetime.date.today()
    year = year or today.year
    month = month or today.month
    cal = calendar.Calendar(firstweekday=start_day)
    month_days = cal.monthdayscalendar(year, month)
    month_name = calendar.month_name[month]
    cell_width = 60
    cell_height = 40
    header_font_size = 58
    line_spacing = 60
    day_font_size = 32
    width = cell_width * 7
    height = cell_height * (len(month_days) + 2) + line_spacing + 20
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
    y_offset = line_y + 20
    for week in month_days:
        for i, day in enumerate(week):
            if day != 0:
                if day == 31 and month == 8:
                    print("day", monthnames[month - 1], day)
                
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
    descriptioneventpos = alleventslines[i].find("DESCRIPTION")
    locationeventpos = alleventslines[i].find("LOCATION")
    categorieseventpos = alleventslines[i].find("CATEGORIES")
    geoeventpos = alleventslines[i].find("GEO")
    dtstarteventpos = alleventslines[i].find("DTSTART")
    dtendeventpos = alleventslines[i].find("DTEND")
    endeventpos = alleventslines[i].find("END:VEVENT")
    if neweventpos == 0:
        found = 0
        day = 0
        eventlocation = ""
        starttime = 0
        endtime = 0
        month = 0
        eventcategories = ""
        sequence = ""
    if dtstarteventpos == 0:
        eventdtstartstr = alleventslines[i][8:]
        datevaluepos = alleventslines[i].find("VALUE=DATE:")
        if datevaluepos == 8:
            eventdtstartstr = alleventslines[i][19:]
        year = int(eventdtstartstr[:4])
        month = int(eventdtstartstr[4:6])
        day = int(eventdtstartstr[6:8])
        starttime = eventdtstartstr[9:11] + ':' + eventdtstartstr[11:13]
        found += 1
    if dtendeventpos == 0:
        eventdtendstr = alleventslines[i][6:]
        endtime = eventdtendstr[9:11] + ':' + eventdtendstr[11:13]
        found += 1
    if summaryeventpos == 0:
        eventsummary = alleventslines[i][8:]
    if categorieseventpos == 0:
        categories = alleventslines[i][11:]
        print("Categoreies", categories)
    if geoeventpos == 0:
        geo = alleventslines[i][5:]
        print("GEO", geo)
    if endeventpos == 0:
        raceevents.append(RaceEvent(eventcategories, eventsummary, day, eventlocation, starttime, endtime, month, geo))
print("Count race events", len(raceevents))
for i in range(len(raceevents)):
    print(i, raceevents[i].summary, raceevents[i].month, raceevents[i].day, raceevents[i].starttime)
raceevent = lookupraceevent(8, 31)
if raceevent is not None:
    print(raceevent.summary)
else:
    print("Not found")
for i in range(12):
    file_path = generate_calendar_svg(2025, i + 1, 0, monthnames[i] + ".svg", False)
key = input("Wait")
