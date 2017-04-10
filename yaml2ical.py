#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from datetime import datetime
import argparse

from icalendar import (
    Calendar,
    Event,
    vRecur,
)
import pytz
import yaml


def main():
    parser = argparse.ArgumentParser(
        description='Convert schedule.yaml to ical.')
    parser.add_argument('yaml', type=argparse.FileType('r'),
                        help='YAML file that explains the schedule.')
    parser.add_argument('-o', '--out', type=argparse.FileType('wb'),
                        help='Output iCal file.')

    args = parser.parse_args()
    schedule = Schedule(args.yaml)

    if args.out is None:
        in_fname = args.yaml.name
        fname = re.sub('\.[^.]+?$', '.ics', in_fname)
        out = open(fname, 'wb')
        schedule.to_ical(out)
    else:
        schedule.to_ical(args.out)


class Schedule:

    def __init__(self, f):
        schedule = yaml.load(f)
        self.ical = Calendar()

        # fill out info
        self.fill_meta(schedule)
        self.fill_term(schedule, 'first')
        self.fill_term(schedule, 'second')

    def fill_meta(self, schedule):
        self.ical.add('version', '2.0')
        self.ical.add('prodid', '-//kamilab calendar//yaml2ical.py//')
        self.ical.add('attendee', 'MAILTO:'+schedule['mailto'])

    def fill_term(self, schedule, term):
        parser = PeriodParser(schedule['year'], term)

        for evt in schedule[term]:
            vevt = Event()
            dtstart, dtend = parser.parse(evt)
            vevt.add('dtstart', dtstart)
            vevt.add('dtend', dtend)

            # set info
            vevt.add('summary', evt['summary'])
            vevt.add('description', evt['description'])

            # set RRULE
            rec = vRecur()
            rec['FREQ'] = 'WEEKLY'
            rec['BYDAY'] = evt['weekday']
            rec['UNTIL'] = parser.eot
            vevt.add('RRULE', rec)

            self.ical.add_component(vevt)

    def to_ical(self, out):
        out.write(self.ical.to_ical())
        out.close()


class PeriodParser:

    PERIODS = [
        ((9, 30), (11, 0)),
        ((11, 10), (12, 40)),
        ((13, 30), (15, 0)),
        ((15, 10), (16, 40)),
        ((16, 50), (18, 20)),
    ]

    END_OF_TERM = {
        'first': lambda y: datetime(y, 7, 31),
        'second': lambda y: datetime(y+1, 3, 31),
    }

    def __init__(self, year, term, tz='Asia/Tokyo'):
        if term == 'first':
            self.date = 4, 1
        else:
            self.date = 9, 1

        self.year = year
        self.eot = self.END_OF_TERM[term](year)
        self.tz = pytz.timezone(tz)
        self.time_pattern = re.compile('\d+(?:\:\d+)?')
        self.num_pattern = re.compile('\d+')

    def parse_clock(self, clock):
        clocks = self.num_pattern.findall(str(clock))

        # only hour is set
        if len(clocks) < 2:
            h = int(clocks[0])
            return h, 0

        # h:m is set
        else:
            return map(int, clocks)

    def parse_time(self, time):
        clocks = self.time_pattern.findall(str(time))

        # single time is set
        if len(clocks) < 2:
            h, m = self.parse_clock(clocks[0])
            return (h, m), (h+1, m)

        # duration is set
        else:
            return map(self.parse_clock, clocks)

    def parse_period(self, period):
        periods = self.num_pattern.findall(str(period))

        # single period is set
        if len(periods) < 2:
            s = int(periods[0])
            return self.PERIODS[s-1]

        # duration is set
        else:
            s, e = map(int, periods)
            start = self.PERIODS[s-1][0]
            end = self.PERIODS[e-1][1]
            return start, end

    def parse(self, schedule):
        if 'time' in schedule:
            time = schedule['time']
            start, end = self.parse_time(time)
        elif 'period' in schedule:
            period = schedule['period']
            start, end = self.parse_period(period)
        else:
            msg = """\
            Time or Period was not defined on <summary: {summary}>
            """.format(**schedule)
            raise KeyError(msg)

        dtstart = datetime(self.year, *self.date, *start, tzinfo=self.tz)
        dtend = datetime(self.year, *self.date, *end, tzinfo=self.tz)

        return dtstart, dtend


if __name__ == '__main__':
    main()
