from django.shortcuts import render
from django.http import HttpResponse
import os, subprocess, cec

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