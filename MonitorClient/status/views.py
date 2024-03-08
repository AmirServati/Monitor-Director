from django.shortcuts import render
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
def index(request):
    #status = os.system("echo 'scan' | cec-client -s -d 1")
    #print(status)
    cec.init()
    devices = cec.list_devices()
    status = ""
    for device in devices.values():
        status += device.osd_string + " (" + device.vendor + "): " + device.physical_address + "\n"
    return HttpResponse(status)

def switch(request, id):
    cec.init()
    return HttpResponse(cec.transmit(destination, opcode, HDMI[id]))

def autoplay(request):
    minute      = request.GET['minute'] 
    hour        = request.GET['hour']
    day_month   = request.GET['day_month'] 
    month       = request.GET['month']
    day_week    = request.GET['day_week'] 
    playlist    = request.GET['playlist']
    cron = CronTab(user=True)
    job = cron.new(command='vlc http://192.168.5.70:80/%s.xspf' % playlist)
    if minute != -1:
        job.minute.on(minute)
    if hour != -1:
        job.hour.also.on(hour)
    if day_month != -1:
        job.day.also.on(day_month)
    if month != -1:
        job.month.also.on(month)
    if day_week != -1:
        job.dow.also.on(day_week)
    cron.write()
    return HttpResponse("done")