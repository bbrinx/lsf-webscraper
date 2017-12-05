""" Module that takes a room number as input and checks for its availability """

import sys
import datetime
from icalendar import Calendar
from bs4 import BeautifulSoup
import requests
import re
from dateutil import rrule

def main():
    """main class, gets calendar, takes arguments and passes them on"""
    # room_nr = sys.argv[1]
    room_nr = 'C 158'
    now = datetime.datetime.now()
    print(get_room_id(room_nr))
    cal = get_calendar(room_nr, now)
    print(is_occupied(now, cal))

def get_room_id(room_nr):
    link_text = " Wilhelminenhof Gebäude {} - Wilhelminenhof Gebäude C ".format(room_nr)
    url = "https://lsf.htw-berlin.de/qisserver/rds?state=change&type=6&moduleParameter=raumSelect&nextdir=change&next=SearchSelect.vm&target=raumSearch&subdir=raum&init=y&source=state%3Dchange%26type%3D5%26moduleParameter%3DraumSearch%26nextdir%3Dchange%26next%3Dsearch.vm%26subdir%3Draum%26_form%3Ddisplay%26topitem%3Dfacilities%26subitem%3Dsearch%26function%3Dnologgedin%26field%3Ddtxt&targetfield=dtxt&_form=display"
    room_list = requests.get(url)
    soup = BeautifulSoup(room_list.text, "html.parser")

    rooms = soup.find_all("a", "regular")
    room = rooms.find_all('a', href=True, string=link_text)
    print('room: {}').format(room)
    regex_anchor = re.compile('{}(.*){}'.format(re.escape('rgid='), re.escape('&idcol')))
    anchor = room['href'].encode('ASCII', 'ignore')
    room_id = regex_anchor.find(anchor)
    print(room_id)

def get_calendar(room_id, now):
    """ Scrapes the HTW roomplan to get the ical
    for the specific room for a specific week

    :param room_nr: An int, specified as commandline arguments
    :param now: A Datetime, the current date
    """
    week = now.date().isocalendar()[1]
    year = now.date().isocalendar()[2]
    url = "https://lsf.htw-berlin.de/qisserver/rds?state=wplan&raum.rgid={}&week={}_{}&act=Raum&pool=Raum&show=plan&P.vx=kurz&P.subc=plan".format(room_id, week, year)
    room_plan = requests.get(url)
    soup = BeautifulSoup(room_plan.text, "html.parser")
    ical_link = soup.select_one("a[href*=iCalendarPlan]")['href'].encode('ASCII', 'ignore')
    return Calendar.from_ical(requests.get(ical_link).text)

def create_rrule(rule):
    """parses a rule and creates an rrule out of it

    :param rule: A vRecur, the rule of the calendar event
    """
    weekdays = {'MO': rrule.MO, 'TU': rrule.TU, 'WE': rrule.WE,
                'TH': rrule.TH, 'FR': rrule.FR}
    freqs = {'YEARLY': rrule.YEARLY, 'MONTHLY': rrule.MONTHLY,
             'WEEKLY': rrule.WEEKLY, 'DAILY': rrule.DAILY}

    _freq = str(rule.get('FREQ')[0])
    freq = freqs[_freq]
    until = rule.get('UNTIL')[0].replace(tzinfo=None)
    byday = rule.get('BYDAY')
    byweekday = []
    for day in byday:
        byweekday.append(weekdays[day])
    return rrule.rrule(freq=freq, until=until, interval=1, byweekday=byweekday)


def is_occupied(now, cal):
    """iterates through the calendar events and
    checks if the room is occupied at the current time

    :param now: A Datetime, the current date
    :param cal: A Calendar, from the roomplan website with the current week
    """
    for component in cal.walk('VEVENT'):
        rule = create_rrule(component.get('RRULE'))
        start = component.get('DTSTART').dt.time()
        end = component.get('DTEND').dt.time()

        for date in rule:
            if now.date() == date.date():
                if start <= now.time() <= end:
                    return True

    return False

if __name__ == "__main__":
    main()
