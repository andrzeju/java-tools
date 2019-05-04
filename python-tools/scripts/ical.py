#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import icalendar
import requests
from datetime import datetime, timedelta
from calendar import monthrange

employees = ['andrzej.urban@ocado.com', 'marcin.czapla@ocado.com', 's.surovikin@ocado.com', 'alexey.eraskin@ocado.com']
holidays = ['22/04', '1/05', '3/05', '9/06', '20/06', '15/08', '1/11', '11/11', '25/12', '26/12']  # TODO 9/06 is sunday
HOLIDAY_SUFFIX = '/2019 11:00'
DATE_FORMAT = "%d/%m/%Y %H:%M"
REPORT_DATE = datetime.today()
events = []


def dataart_employee(shift):
    return shift.get('ATTENDEE') in employees


def to_date(date):
    return datetime.strptime(date, DATE_FORMAT)


def day_in_current_month(day_checked):
    today = REPORT_DATE
    firstDayDate = datetime(today.year, today.month, 1)
    lastDayDate = datetime(today.year, today.month, monthrange(today.year, today.month)[1], 23, 59, 59)
    return (day_checked > firstDayDate) & (day_checked <= lastDayDate)


def current_month(shift):
    event_date_start = to_date(shift['start'])
    event_date_end = to_date(shift['end'])

    startedThisMonth = day_in_current_month(event_date_start)
    finishedThisMonth = day_in_current_month(event_date_end)
    return startedThisMonth | finishedThisMonth


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

for event in events:
    if current_month(event):
        holiday = 0
        for day in holidays:
            if (to_date(day + HOLIDAY_SUFFIX) > to_date(event['start'])) & (
                    to_date(day + HOLIDAY_SUFFIX) < to_date(event['end'])):
                holiday = holiday + 1

        eventDateStart = to_date(event['start'])
        eventDateEnd = to_date(event['end'])
        delta = eventDateEnd - eventDateStart
        daygen = (eventDateStart + timedelta(x) for x in range((eventDateEnd - eventDateStart).days))
        sum_workday = sum(1 for day in daygen if (day.weekday() < 4) & day_in_current_month(day))
        daygen = (eventDateStart + timedelta(x) for x in range((eventDateEnd - eventDateStart).days))
        sum_weekends = sum(1 for day in daygen if (day.weekday() >= 4) & day_in_current_month(day))

        print("{0} - {1} {2}".format(event['start'], event['end'], event['person'].split('@')[0]))
        print("Mon-Thru: {0}".format(sum_workday))
        print("Fri-Sun: {0}".format(sum_weekends))
        print("Holiday: {0} \n".format(holiday) if holiday > 0 else '')
