#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import icalendar
import requests
from datetime import datetime, timedelta
from calendar import monthrange
from scripts.person import PersonSummary

employees = ['andrzej.urban@ocado.com', 'marcin.czapla@ocado.com', 's.surovikin@ocado.com', 'alexey.eraskin@ocado.com',
             'jakub.czuchaj@ocado.com', 'pawel.rybialek@ocado.com', 'evgeni.belchev@ocado.com']
holidays = ['1/1', '6/1', '4/4', '5/4', '3/5', '4/5', '23/5', '3/6',
            '15/8', '1/11', '11/11', '24/12', '25/12', '26/12']
HOLIDAY_SUFFIX = '/2020'
DATE_FORMAT = "%d/%m/%Y"
REPORT_DATE = datetime.today()
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
    firstDayDate = datetime(today.year, today.month, 1)
    lastDayDate = datetime(today.year, today.month, monthrange(today.year, today.month)[1], 23, 59, 59)
    return (day_checked >= firstDayDate) & (day_checked <= lastDayDate)


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
    'https://ocado-tech-osp.pagerduty.com/private/c24f7099aece486ec80efc7fca6480ca6c5635ae23830da75d564516c5efc067'
    '/feed/PS0X7ZR')
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

for event in single_day_events:
    eventDate = event['start']
    email = event['person']

    if email not in summaries:
        summaries[email] = PersonSummary(email, 0, 0, 0)

    person = summaries[email]

    if to_holiday_format(eventDate) in holidays:
        person.holidays += 1
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
    print("Holiday: {0} \n".format(summary.holidays) if summary.holidays > 0 else '')
