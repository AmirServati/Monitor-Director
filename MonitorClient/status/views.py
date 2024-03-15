from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import cec
from crontab import CronTab

destination = cec.CECDEVICE_BROADCAST
opcode = cec.CEC_OPCODE_ACTIVE_SOURCE
HDMI = {
    1 : b'\x10\x00',
    2 : b'\x20\x00',
    3 : b'\x30\x00',
    4 : b'\x40\x00'
}

# Create your views here.
def status(request):
    f = open("./static/status", "r")
    source = f.readline()
    return HttpResponse(source)

def switch(request, id):
    cec.init()
    return HttpResponse(cec.transmit(destination, opcode, HDMI[id]))

def autoplay(request):
    hour_start      = request.GET['hour_start'] 
    minute_start    = request.GET['minute_start']
    hour_finish     = request.GET['hour_finish'] 
    minute_finish   = request.GET['minute_finish']
    days            = tuple(map(int, request.GET['days'].split(',')))
    playlist        = request.GET['playlist']
    cron = CronTab(user=True)
    playjob = cron.new(command='echo "as" | cec-client -s -d 1; DISPLAY=:0.0 vlc http://192.168.5.58:80/Playlists/xspf/%s.xspf --fullscreen --loop' % playlist)
    play_comment = "PLAY->%s@%s-%s:%s" % (playlist, request.GET['days'], hour_start, minute_start)
    playjob.set_comment(play_comment)
    playjob.minute.on(minute_start)
    playjob.hour.also.on(hour_start)
    for day in days:
        playjob.dow.also.on(day)
    exitjob = cron.new(command='echo "tx 4f:82:20:00" | cec-client -s -d 1; killall -9 vlc')
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