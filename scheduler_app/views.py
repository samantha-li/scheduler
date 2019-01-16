from django.http import HttpResponse, HttpResponseRedirect
from django.template import Template, loader
from django.conf import settings
import requests
import os
import calendar
from collections import defaultdict
import yaml

from .models import Greeting, Shift, Schedule, Availability
import django
django.setup()

month_mapping = {1: "January", 2: "February", 3: "March", 4: "April",
                5: "May", 6: "June", 7: "July", 8: "August", 9: "September",
                10: "October", 11: "November", 12: "December"}

month = 11 # placeholder
year = 2018 # placeholder
shifts = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
shifts[2018][11][2].append("19:00-21:00") # for testing purposes
shifts[2018][11][2].append("21:00-23:00") # for testing purposes
pick_shifts = yaml.load("""
- {day: Monday, start_time: '19:00', end_time: '21:00'}
- {day: Monday, start_time: '21:00', end_time: '23:00'}
- {day: Tuesday, start_time: '19:00', end_time: '21:00'}
- {day: Tuesday, start_time: '21:00', end_time: '23:00'}
- {day: Wednesday, start_time: '19:00', end_time: '21:00'}
- {day: Wednesday, start_time: '21:00', end_time: '23:00'}
- {day: Thursday, start_time: '19:00', end_time: '21:00'}
- {day: Thursday, start_time: '21:00', end_time: '23:00'}
- {day: Friday, start_time: '19:00', end_time: '21:00'}
- {day: Friday, start_time: '21:00', end_time: '23:00'}
- {day: Saturday, start_time: '15:00', end_time: '17:00'}
- {day: Saturday, start_time: '16:00', end_time: '18:00'}
- {day: Saturday, start_time: '17:00', end_time: '19:00'}
- {day: Sunday, start_time: '17:00', end_time: '19:00'}
- {day: Sunday, start_time: '18:00', end_time: '20:00'}
- {day: Sunday, start_time: '19:00', end_time: '21:00'}
- {day: Sunday, start_time: '20:00', end_time: '22:00'}
- {day: Sunday, start_time: '21:00', end_time: '23:00'}
""")
# when need to migrate DB, comment out below
# START OF CODE BLOCK ---------------------------------------------------------
try:
    schedule = Schedule.objects.get(user='admin')
except Schedule.DoesNotExist:
    schedule = Schedule.objects.create(user="admin")
except Schedule.MultipleObjectsReturned: # should never happen
    schedule = Schedule.objects.filter(user="admin")[0]

for s in pick_shifts:
    try:
        tmp = Shift.objects.get(weekday=s["day"], start_time=s["start_time"], end_time=s["end_time"])
    except Shift.DoesNotExist:
        tmp = Shift.objects.create(weekday=s["day"], start_time=s["start_time"], end_time=s["end_time"])
    schedule.shifts.add(tmp)
# END OF CODE BLOCK  ---------------------------------------------------------

shifts_by_day = defaultdict(list)
indexed_shifts = []
i = 0

# when need to migrate DB, comment out below
# START OF CODE BLOCK ---------------------------------------------------------
for s in schedule.shifts.all():
    shifts_by_day[s.weekday].append((i, "{:s}-{:s}".format(s.start_time, s.end_time)))
    indexed_shifts.append({"weekday": s.weekday, "start_time": s.start_time, "end_time":s.end_time})
    i += 1
# END OF CODE BLOCK ---------------------------------------------------------
for s in pick_shifts:
    shifts_by_day[s["day"]].append((i, "{:s}-{:s}".format(s["start_time"], s["end_time"])))
    indexed_shifts.append(s)
    i += 1

def index(request):
    template = loader.get_template('calendar.html')
    calMatrix = calendar.monthcalendar(year, month)
    shifts_this_month = shifts[year][month]

    current_user = request.user
    context = {"title": "{:s} {:d}".format(month_mapping[month], year),
                "monthCal": calMatrix,
                "shifts": shifts_this_month,
                "user_id": current_user
              }
    return HttpResponse(template.render(context, request))

def select_shifts(request):
    current_user = request.user
    if request.method == "GET":
        params = request.GET
    else:
        params = request.POST
    template = loader.get_template('shift-selection.html')
    context = { "shifts_by_day": shifts_by_day,
                "weekdays": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                "params": params,
                "user_id": current_user,
              }
    return HttpResponse(template.render(context, request))

def change_availability(request):
    current_user = request.user
    if request.method == "GET":
        params = request.GET
    else:
        params = request.POST
    template = loader.get_template('change-availability.html')
    context = { "shifts_by_day": shifts_by_day,
                "weekdays": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                "params": params,
                "user_id": current_user,
              }
    return HttpResponse(template.render(context, request))

def set_availability(request):
    myshifts = defaultdict(list)
    current_user = request.user
    try:
        user_schedule = Availability.objects.get(user=(current_user))
    except Availability.DoesNotExist:
        user_schedule = Availability.objects.create(user=current_user)
    i = 0
    template = loader.get_template('set-availability.html')
    context = { "shifts_by_day": myshifts,
                "weekdays": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
              }
    for s in indexed_shifts:
        checked = request.POST.get(str(i))
        if checked:
            try:
                tmp = Shift.objects.get(weekday=s["weekday"], start_time=s["start_time"], end_time=s["end_time"])
            except Shift.DoesNotExist:
                tmp = None
            if tmp != None:
                user_schedule.shifts.add(tmp)
        i += 1
    for s in user_schedule.shifts.all():
        myshifts[s.weekday].append((s.start_time, s.end_time))
    return HttpResponse(template.render(context, request))

def see_availability(request):
    myshifts = defaultdict(list)
    current_user = request.user
    try:
        user_schedule = Availability.objects.get(user=(current_user))
    except Availability.DoesNotExist:
        user_schedule = Availability.objects.create(user=current_user)
    for s in user_schedule.shifts.all():
        myshifts[s.weekday].append((s.start_time, s.end_time))
    template = loader.get_template('set-availability.html')
    context = { "shifts_by_day": myshifts,
                "weekdays": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
              }
    return HttpResponse(template.render(context, request))

def see_shifts(request):
    myshifts = defaultdict(list)
    current_user = request.user
    try:
        user_schedule = Schedule.objects.get(user=(current_user))
    except Schedule.DoesNotExist:
        user_schedule = Schedule.objects.create(user=current_user)
    for s in user_schedule.shifts.all():
        myshifts[s.weekday].append((s.start_time, s.end_time))
    template = loader.get_template('set-shifts.html')
    context = { "shifts_by_day": myshifts,
                "weekdays": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
              }
    return HttpResponse(template.render(context, request))

def set_shifts(request):
    myshifts = defaultdict(list)
    current_user = request.user
    try:
        user_schedule = Schedule.objects.get(user=current_user)
    except Schedule.DoesNotExist:
        user_schedule = Schedule.objects.create(user=current_user)
    i = 0
    template = loader.get_template('set-shifts.html')
    context = { "shifts_by_day": myshifts,
                "weekdays": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
              }
    for s in indexed_shifts:
        checked = request.POST.get(str(i))
        if checked:
            try:
                tmp = Shift.objects.get(weekday=s["weekday"], start_time=s["start_time"], end_time=s["end_time"])
            except Shift.DoesNotExist:
                tmp = None
            if tmp != None:
                user_schedule.shifts.add(tmp)
        i += 1
    for s in user_schedule.shifts.all():
        myshifts[s.weekday].append((s.start_time, s.end_time))
    return HttpResponse(template.render(context, request))

def select(request):

    return HttpResponse('Nothing here yet')
