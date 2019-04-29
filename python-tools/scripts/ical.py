#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import icalendar
import requests
from datetime import datetime
from calendar import monthrange

employees = ['andrzej.urban@ocado.com', 'marcin.czapla@ocado.com', 's.surovikin@ocado.com', 'alexey.eraskin@ocado.com']
holidays = ['22/04/2019 11:00']
events = []
dateformat = "%d/%m/%Y %H:%M"


def dataart_employee(event):
    return event.get('ATTENDEE') in employees

def to_date(date):
    return datetime.strptime(date, dateformat)

def current_month(event):
    today = datetime.today()
    eventDateStart = to_date(event['start'])
    eventDateEnd = to_date(event['end'])
    firstDayDate = datetime(today.year, today.month, 1)
    lastDayDate = datetime(today.year, today.month, monthrange(today.year, today.month)[1])

    startedThisMonth = (eventDateStart > firstDayDate) & (eventDateStart < lastDayDate)
    finishedThisMonth = (eventDateEnd > firstDayDate) & (eventDateEnd < lastDayDate)
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
            'start': component.get('dtstart').dt.strftime(dateformat),
            'end': component.get('dtend').dt.strftime(dateformat)
        })

for event in events:
    if current_month(event):
        print("{0} - {1} {2}".format(event['start'], event['end'], event['person'].split('@')[0]))
        print("Mon-Thru: 4")
        print("Fri-Sun: 3")
        holiday = 0
        for day in holidays:
            if (to_date(day) > to_date(event['start'])) & (to_date(day) < to_date(event['end'])):
                holiday = holiday+1
        print("Holiday: {0}".format(holiday))
        # eventDateStart = to_date(event['start'])
        # eventDateEnd = to_date(event['end'])
        # delta = eventDateEnd - eventDateStart
        # print("dd: {0}".format(delta.days))
