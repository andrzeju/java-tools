#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import icalendar
import requests
from datetime import datetime, timedelta
from calendar import monthrange
from scripts.person import PersonSummary

employees = ['c.v@xyz.com', 'd.e@ox.com', 's.se@odd.com', 'dd.e@ccd.com',
             'd.e@fddd.com', 'e.n@d.com', 'r.l@oeo.com']
holidays = ['1/1', '6/1', '4/4', '5/4', '3/5', '4/5', '23/5', '3/6',
            '15/8', '1/11', '11/11', '24/12', '25/12', '26/12']
holidays_bg = ['1/1', '3/3', '30/4', '3/5', '4/5', '6/5', '24/5',
               '6/9', '22/9', '24/12', '25/12', '26/12', '27/12', '28/12']
HOLIDAY_SUFFIX = '/2020'
DATE_FORMAT = "%d/%m/%Y"
REPORT_DATE = datetime.today()  # + timedelta(days=30)
events = []
single_day_events = []
summaries = {}


def dataart_employee(shift):
    return shift.get('ATTENDEE') in employees


def to_date(date):
    return datetime.strptime(date, DATE_FORMAT)


def to_holiday_format(date):
    return str(date.day) + '/' + str(date.month)


def day_in_current_month(day_checked):
    today = REPORT_DATE
    first_day_date = datetime(today.year, today.month, 1)
    last_day_date = datetime(today.year, today.month, monthrange(today.year, today.month)[1], 23, 59, 59)
    return (day_checked >= first_day_date) & (day_checked <= last_day_date)


def current_month(shift):
    event_date_start = shift['start']

    started_this_month = day_in_current_month(event_date_start)
    return started_this_month


def separate_into_days_this_month(multi_day_events):
    separate_days = []
    for multi_day_event in multi_day_events:
        start_date = to_date(multi_day_event['start'])
        end_date = to_date(multi_day_event['end'])
        event_delta = end_date - start_date

        for i in range(0, event_delta.days):
            multi_day_event['start'] = start_date + timedelta(days=i)
            multi_day_event['end'] = start_date + timedelta(days=i)
            if current_month(multi_day_event):
                separate_days.append(multi_day_event.copy())

    return separate_days


r = requests.get(
    'https://oxo-tech-osp.pagerduty.com/private/sdf37sdui8je'
    '/feed/PS0X7VVVZR')
icalfile = r.text

gcal = icalendar.Calendar.from_ical(icalfile)
for component in gcal.walk():
    if (component.name == "VEVENT") & dataart_employee(component):
        events.append({
            'summary': component.get('summary'),
            'person': component.get('ATTENDEE'),
            'start': component.get('dtstart').dt.strftime(DATE_FORMAT),
            'end': component.get('dtend').dt.strftime(DATE_FORMAT)
        })

single_day_events = separate_into_days_this_month(events)


def get_holidays_by_person(person_email):
    if person_email == 's.e@xxc.com':
        return holidays_bg
    return holidays


for event in single_day_events:
    eventDate = event['start']
    email = event['person']

    if email not in summaries:
        summaries[email] = PersonSummary(email, 0, 0, 0, '')

    person = summaries[email]

    if to_holiday_format(eventDate) in get_holidays_by_person(email):
        person.holidays += 1
        person.holiday_list += to_holiday_format(eventDate) + ','
    else:
        if eventDate.weekday() < 4:
            person.business_days += 1
        else:
            person.weekends += 1

for email in summaries:

    summary = summaries[email]

    print(summary.name.split('@')[0])
    print("Mon-Thru: {0}".format(summary.business_days))
    print("Fri-Sun: {0}".format(summary.weekends))
    print("Holiday: {0} ({1})\n".format(summary.holidays, summary.holiday_list) if summary.holidays > 0 else '')
