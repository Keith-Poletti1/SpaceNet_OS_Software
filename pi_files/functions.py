from datetime import datetime
import time
import csv
import serial
import os
import RPi.GPIO as GPIO
import logging
import re
import subprocess
#import shutil

#LEDPin=20

def read_flybys(media_location, fname):
    UHFtimes =[] # initalize vars
    Lbandtimes =[]
    #wait_for_media(media_location)
    try:
        print('looking for flybys in ' +media_location+fname)
        with open(media_location+fname, newline = '') as fly_bys:  #open file while lines remain                                                                                        
            reader = csv.reader(fly_bys, delimiter='\t')
            next(reader) # skip header
            for fly_bys in reader:
                UHFtimes.append(datetime.strptime(fly_bys[0], "%m/%d/%Y %H:%M:%S"))
                Lbandtimes.append(datetime.strptime(fly_bys[1], "%m/%d/%Y %H:%M:%S"))
        print('Parsed flybys')
        print('UHF')
        print(UHFtimes)
        print('Lband')
        print(Lbandtimes)

        print('Removing chronologicaly invalid flybys')
        time_cleanup(UHFtimes)
        time_cleanup(Lbandtimes)
        if UHFtimes or Lbandtimes:
            try:
                print('Valid Flybys UHF')
                print(UHFtimes)
                print('Valid Flybys L-Band')
                print(Lbandtimes)
            except RuntimeError:
                pass    


            return UHFtimes, Lbandtimes
        else:
            logging.exception('No passes in file')
            print('No passes in file')

            while True:
                blink(20,.25)   

    except IOError:
        logging.exception('File not found in Media')
        print('File not found in Media')
        while True:
            blink(20, .25)

def update_time(working_dir):
    os.system('cd ' + working_dir + ' && python2 RasPiTimeToUTCNew.py')


def collect_data(band,samprate,recordtime,SwitchPin):
    print('collecting data for ',band)
    numsamps = samprate*recordtime
    if band == 'UHF': 
        freq = 437.25e6
        lnagain = 8
        vgagain = 30
        GPIO.output(SwitchPin, GPIO.HIGH) # when ledstate is True then we will record UHF signals

    elif band == 'Lband':
        freq = 1620e6
        lnagain = 8
        vgagain = 30
        GPIO.output(SwitchPin, GPIO.LOW) # when ledstate is low then we will record L signals

    else:
        logging.exception('No Band Identified')
        while True:
            blink(20, .25)

    GPIO.output(SwitchPin, GPIO.LOW) # when ledstate is low then we will record L signals
    os.system('cd /home/pi/Desktop/ && hackrf_transfer -w -s' + str(samprate) + ' -f ' + str(freq) + ' -l ' + str(lnagain) + ' -g ' + str(vgagain) + ' -n ' + str(int(numsamps)))
    return

def time_cleanup(flybylist):
    print('cleaning flyby times...')
    now = datetime.now() # get current time
    if not flybylist :
        return
    while (flybylist[0] - now).total_seconds() < 0:
        flybylist.pop(0)
        print(flybylist)
        if not flybylist :
            return
    return
    
def move_data(working_dir,media_location):
    #wait_for_media(media_location)
    sourcefiles = os.listdir(working_dir)
    for file in sourcefiles:
        if file.endswith('.wav'):
            os.system('cp '+working_dir+file +' '+media_location + ' && ' + 'rm '+working_dir+file)
            

def wait_for_media(media_location):
    media_name = media_location.split('/')[-1]
    df = subprocess.check_output("lsusb")
    while media_name not in df.decode("utf-8"):
        #device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
        df = subprocess.check_output("lsusb")
        time.sleep(.1)
        print(df)
        #devices = []
        #for i in df.split('\n'):
        #    devices = i
        #    if i:
        #        info = device_re.match(i)
        #        if info:
        #            dinfo = info.groupdict()
        #            dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
        #            devices.append(dinfo)
        #print(devices)

def blink(GPIO_pin, duration):
    GPIO.output(GPIO_pin, GPIO.HIGH) # Turn on indicator LED for data collection
    time.sleep(duration)
    GPIO.output(GPIO_pin, GPIO.LOW) # Turn on indicator LED for data collection
    time.sleep(duration)