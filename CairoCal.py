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
file_path = generate_calendar_svg(2025, 5, 1, "May2025.svg", False)
key = input("Wait")
