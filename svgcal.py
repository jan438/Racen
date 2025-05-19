#!/usr/bin/env python
# -*- coding: utf-8 -*-
# svg year calendar, based calendargen.py [Copyright (c) 2015 Vlad Emelyanov, The MIT License (MIT)]
from __future__ import unicode_literals

__author__ = "Vlad Emelyanov (volshebnyi@gmail.com)"
__modify__ = "zvezdochiot (zvezdochiot@users.sourceforge.net)"
__version__ = "0.20181227"
__date__ = "2018-12-27"
__license__ = "CC-BY"

import datetime
import argparse
import sys


def zfill_list(a):
    max_len = max([len(i) for i in a])
    return [i.zfill(max_len) for i in a]

month_names = [ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' ]
weekdays_names = [ 'Mn', 'Tu', 'Wd', 'Th', 'Fr', 'St', 'Sn' ]

holidays_public = [
        (1, 1), (1, 7),
        (2, 23),
        (3, 8),
        (5, 1), (5, 9),
        (6, 12),
        (11, 4) ]

def is_leap(year):
    try:
        datetime.date(year, 2, 29)
    except ValueError:
        return False

    return True


def get_holidays():
    return holidays_public


def get_specials(year):
    holidays = []

    # last Friday of July is Sysadmin's Day
    d = datetime.date.today()
    holidays.append((d.month, d.day))

    return holidays


class SvgCalendar:
    def __init__(self, year):

        self.year = year

        font = 'Consolas'

        self.style = {
            'units': 'pt',

            'width': 842,
            'height': 595,

            'border-color': '#ccc',

            'year-color': '#666666',
            'year-padding-top': 45,
            'year-padding-left': 18,
            'year-font-family': font,
            'year-font-size': 45,

            'month-width': 204,
            'month-width-rect': 192,
            'month-height': 180,

            'day-width': 188 / 7.0,
            'day-height': 100 / 5.0,

            'month-margin-right': 0,
            'month-margin-bottom': 0,

            'month-font-family': font,
            'month-font-size': 28,
            'month-color': '#FF9525',
            'month-padding-top': 26,

            'month-offset-top': 45,

            'week-padding-top': 54,
            'week-font-family': font,
            'week-font-size': 14,

            'day-padding-top': 54,
            'day-font-family': font,
            'day-font-size': 15,

            'day-color': '#000000',
            'day-holiday-color': '#FF0000',
            'day-special-color': '#007F3F',

            'week-color': '#999',
            'week-holiday-color': '#FF0000',
        }

        self.year_name = str(year)
        self.month_names = month_names
        self.weekdays_names = weekdays_names
        self.days_names = zfill_list([str(i) for i in range(1, 32)])

        # well, actually holidays depend on the production calendar
        self.holidays = get_holidays()
        self.specials = get_specials(year)
        self.not_holidays = []

    def is_holiday(self, month, day, day_of_week):
        if day_of_week in [5, 6]:
            return (month, day) not in self.not_holidays
        return (month, day) in self.holidays

    def is_special(self, month, day, day_of_week):
        return (month, day) in self.specials

    def render_day(self, x, y, month, day, day_of_week):
        svg = ''
        if self.is_special(month, day,  day_of_week):
            color = self.style['day-special-color']
        elif self.is_holiday(month, day,  day_of_week):
            color = self.style['day-holiday-color']
        else:
            color = self.style['day-color']
        svg += '<text x="%spt" y="%spt" font-family="%s" font-size="%spt" fill="%s" text-anchor="middle">' % (
            x + 0.5 * self.style['day-width'],
            y, self.style['day-font-family'],
            self.style['day-font-size'],
            color)
        svg += '%s' % self.days_names[day - 1]
        svg += '</text>'
        return svg

    def render_week(self, x, y):
        svg = ''
        svg += '<g>'
        for i in range(7):
            if i < 5:
                color = self.style['week-color']
            else:
                color = self.style['week-holiday-color']
            svg += (
                '<text x="%spt" y="%spt" font-family="%s" font-size="%spt" '
                'text-anchor="middle" fill="%s">') % (
                x + (i + 0.5) * self.style['day-width'],
                y,
                self.style['week-font-family'],
                self.style['week-font-size'],
                color)
            svg += '%s' % (self.weekdays_names[i])
            svg += '</text>'
        svg += '</g>'
        return svg

    def render_month(self, x, y, month_no):
        svg = ''

        svg += '<g>'
        svg += (
            '<rect x="%spt" y="%spt" width="%spt" height="%spt" style="fill:%s;fill-opacity:1;stroke:%s;stroke-opacity:1;opacity:0.25" />') % (
            x,
            y + self.style['month-padding-top'] * 1.25,
            self.style['month-width-rect'],
            self.style['month-padding-top'],
            self.style['month-color'],
            self.style['month-color'])
        svg += (
            '<text x="%spt" y="%spt" font-family="%s" font-size="%spt" '
            'text-anchor="middle" fill="%s">') % (
            x + self.style['month-width'] / 2,
            y + self.style['month-padding-top'],
            self.style['month-font-family'],
            self.style['month-font-size'],
            self.style['month-color'])
        svg += '%s' % (self.month_names[month_no - 1])
        svg += '</text>'
        svg += self.render_week(x, y + self.style['week-padding-top'])

        day_of_week = -1  # will start from Monday
        week_no = 1

        d = datetime.date(self.year, month_no, 1)
        while d.month == month_no:
            day_no = d.day
            day_of_week = d.weekday()
            d = d + datetime.timedelta(days=1)

            xx = x + self.style['day-width'] * (day_of_week)
            yy = y + self.style['day-padding-top'] + week_no * self.style['day-height']

            svg += self.render_day(xx, yy, month_no, day_no, day_of_week)

            if day_of_week == 6:
                week_no += 1

        svg += '</g>'
        return svg

    def render_year(self, x, y):
        svg = ''
        svg += '<g>'
        svg += (
            '<text x="%spt" y="%spt" font-family="%s" font-size="%spt" '
            'text-anchor="middle" fill="%s">') % (
            x + self.style['width'] / 2,
            y + self.style['year-padding-top'],
            self.style['year-font-family'],
            self.style['year-font-size'],
            self.style['year-color'])
        svg += self.year_name
        svg += '</text>'
        for i in range(12):
            xx = i % 4
            yy = i / 4
            svg += self.render_month(
                x + xx * self.style['month-width'] + xx * self.style['month-margin-right'],
                (
                    y + self.style['month-offset-top']
                    + yy * self.style['month-height']
                    + yy * self.style['month-margin-bottom']),
                i + 1)
        svg += '</g>'
        return svg

    def render(self):
        svg = ''
        svg += (
            '<?xml version="1.0" standalone="no"?>'
            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
            '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">')
        svg += (
            '<svg width="%spt" height="%spt" version="1.1" xmlns='
            '"http://www.w3.org/2000/svg"><desc>Calendar 2012</desc>') % (
            self.style['width'], self.style['height'])
        svg += (
            '<g><rect x="2.5pt" y="2.5pt" width="%spt" height="%spt" rx='
            '"2.5pt"  style="fill:#fff;fill-opacity:1;stroke:%s;storke-width:0.5pt;stroke-opacity:1;opacity:0.25" /></g>') % (
            self.style['width'] - 5,
            self.style['height'] - 5,
            self.style['border-color'])
        svg += self.render_year(self.style['year-padding-left'], 0)
        svg += '</svg>'
        return svg


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calendar generator.')
    parser.add_argument('-o', '--output', metavar='out', type=argparse.FileType('wb'), default=getattr(sys.stdout, "buffer", sys.stdout), help='output file (default: stdout)')
    parser.add_argument('year', type=int, help='year for calendar')
    params = parser.parse_args()
    c = SvgCalendar(params.year)
#    print c.render()
    params.output.write(c.render())

