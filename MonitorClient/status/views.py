from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from crontab import CronTab
from .models import Monitor
import netifaces
import os

IP = netifaces.ifaddresses('wlan0')[2][0]['addr']
HDMI = {
    1 : 'TV',
    2 : 'Player'
}

# Create your views here.
def switch_to(id):
    monitor = Monitor.objects.get(id = 1)
    monitor.source = HDMI[id]
    monitor.save()
    if id == 1:
        os.system('echo "tx 4f:82:20:00" | cec-client -s -d 1')
    else:
        os.system('echo "as" | cec-client -s -d 1')
    return "done"

def status(request):
    source = Monitor.objects.get(id = 1).source
    return HttpResponse(source)

def switch(request, id):
    switch_to(id)
    monitor = Monitor.objects.get(id = 1)
    return HttpResponse(monitor.source)

def autoplay(request):
    hour_start      = request.GET['hour_start'] 
    minute_start    = request.GET['minute_start']
    hour_finish     = request.GET['hour_finish'] 
    minute_finish   = request.GET['minute_finish']
    days            = tuple(map(int, request.GET['days'].split(',')))
    playlist        = request.GET['playlist']
    cron = CronTab(user=True)
    playjob = cron.new(command='echo "as" | cec-client -s -d 1; wget http://%s:8000/status/switch/2 --delete-after; DISPLAY=:0.0 vlc http://192.168.1.106:80/Playlists/xspf/%s.xspf --fullscreen --loop' % (IP, playlist))
    play_comment = "PLAY->%s@%s-%s:%s" % (playlist, request.GET['days'], hour_start, minute_start)
    playjob.set_comment(play_comment)
    playjob.minute.on(minute_start)
    playjob.hour.also.on(hour_start)
    for day in days:
        playjob.dow.also.on(day)
    exitjob = cron.new(command='echo "tx 4f:82:20:00" | cec-client -s -d 1; killall -9 vlc; wget http://%s:8000/status/switch/1 --delete-after' % IP)
    exit_comment = "EXIT->%s@%s-%s:%s" % (playlist, request.GET['days'], hour_finish, minute_finish)
    exitjob.set_comment(exit_comment)
    exitjob.minute.on(minute_finish)
    exitjob.hour.also.on(hour_finish)
    for day in days:
        exitjob.dow.also.on(day)
    cron.write()
    return HttpResponse("done")

@csrf_exempt
def autodelete(request):
    cron = CronTab(user=True)
    cron.remove_all(comment=request.POST.get("playcomment"))
    cron.remove_all(comment=request.POST.get("exitcomment"))
    cron.write()
    return HttpResponse("done")

@csrf_exempt
def autopow(request):
    cron = CronTab(user=True)
    if request.method == "GET":
        try:
            onjob = cron.find_comment('on')
            offjob = cron.find_comment('off')
            for i in onjob:
                on_hour = i.hour
                on_minute = i.minute
            for i in offjob:
                off_hour = i.hour
                off_minute = i.minute
            return HttpResponse("%s:%s - %s:%s" % (on_hour, on_minute, off_hour, off_minute))
        except:
            pass
    elif request.method == "POST":      
        try:
            cron.remove_all(comment='on')
            cron.remove_all(comment='off')
        except:
            pass
        on_hour = request.POST.get('on').split(":")[0]
        on_minute = request.POST.get('on').split(":")[1]
        off_hour = request.POST.get('off').split(":")[0]
        off_minute = request.POST.get('off').split(":")[1]
        onjob = cron.new(command = 'echo "on 0" | cec-client -s -d 1; curl http://%s:8000/status/switch/1' % IP, comment = "on")
        onjob.hour.on(on_hour)
        onjob.minute.also.on(on_minute)
        offjob = cron.new(command = 'echo "standby 0" | cec-client -s -d 1; curl http://%s:8000/status/switch/1' % IP, comment = "off")
        offjob.hour.on(off_hour)
        offjob.minute.also.on(off_minute)
        cron.write()
    return HttpResponse("done")