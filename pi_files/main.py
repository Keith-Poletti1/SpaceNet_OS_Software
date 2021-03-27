from functions import *

def main():    
    #############################################################################################################################
    # Configuring GPIO pin to be used to control the current state of the switcher 
    GPIO.setmode(GPIO.BCM)
    SwitchPin = 21
    LEDPin = 20
    GPIO.setup(SwitchPin, GPIO.OUT) # Choosing which physical GPIO will be used on the Raspberry Pi
    GPIO.setup(LEDPin, GPIO.OUT) # Choosing which physical GPIO will be used on the Raspberry Pi

    # SDR params
    #max_its = 500000
    SampleRate =10e6
    recordtime = 0.25*60 # seconds to be recorded 
    FlybyMargin = 10 # margin for when to start data collection in seconds
    UnitSleepTime = FlybyMargin-round(.2*10) # delay between each time check
   
    # Flyby file location
    media_location = '/media/pi/FLASH_DRIVE/'
    startfile = 'auto_update.txt'
    data_output_location = '/media/pi/FLASH_DRIVE/wav_files'
    working_dir = '/home/pi/Desktop/SpaceNet_OS_Software'
    #############################################################################################################################
    #############################################################################################################################
    #############################################################################################################################
    #############################################################################################################################
    # set OS time
    GPIO.output(LEDPin, GPIO.HIGH) # Turn on indicator at start up
    print('Starting up...')

    time.sleep(5) # let the usb ports come online(there is a better way to do this)

    print('Initilize GPS clock...')
    update_time(working_dir)
    now = str(datetime.now())

    if not os.listdir(media_location):
        os.system('rm -rf '+ media_location)
        os.system('sh ' +media_location[:-1]+'1/'+startfile)


    # get list of flybys
    print('Getting list of flybys...')
    Flyby_File_Name = now[5:7] + '_' + now[8:10] + '_Flyby_List.txt'
    UHFtimes, Lbandtimes = read_flybys(media_location, Flyby_File_Name)

    GPIO.output(LEDPin, GPIO.LOW) # Turn off indicator now that setup is complete

    # flash led that set if complete (make isblink forever if somthing foes wrong should be added)
    for i in range(1,6):
        blink(LEDPin,1)   
        
    print('Setup complete')
    #############################################################################################################################
    #############################################################################################################################
    # Enter main loop 

    if UnitSleepTime>FlybyMargin:
        logging.exception('UnitSleepTime is larger than FlybyMargin flybys may be missed!!')

    while UHFtimes or Lbandtimes :
        #############################################################################################################################
        # This sets the system time to the received GPS UTC time
        update_time(working_dir)
        now = datetime.now() # get current time
        print('current updated time:', now) # print debug

        if not (Flyby_File_Name == (str(datetime.now())[5:7] + '_' + str(datetime.now())[8:10] + '_Flyby_List.txt')):
            print('New Day getting new flyby file')
            GPIO.output(LEDPin, GPIO.HIGH) # Turn on indicator at start up
            UHFtimes, Lbandtimes = read_flybys(media_location, Flyby_File_Name)
            GPIO.output(LEDPin, GPIO.LOW) # Turn off indicator now that setup is complete

        # make two time objects that determine the time till next pass
        if UHFtimes:
            UHF_delay_in_seconds = (UHFtimes[0]-now).total_seconds()
        else:
            UHF_delay_in_seconds = 1000
            
        if Lbandtimes:
            Lband_delay_in_seconds = (Lbandtimes[0]-now).total_seconds()
        else:
            Lband_delay_in_seconds = 1000
        #############################################################################################################################
        # determine if the closests pass is within margin if so collect data
        # prioritizes UHF
        if 0 < UHF_delay_in_seconds < FlybyMargin:
            GPIO.output(LEDPin, GPIO.HIGH) # Turn on indicator LED for data collection
            
            print('UHF pass detected') # print debug
            print(UHF_delay_in_seconds) # print debug
            while UHF_delay_in_seconds > .9:
                now = datetime.now()
                UHF_delay_in_seconds = (UHFtimes[0]-now).total_seconds()
               # print(UHF_delay_in_seconds) # print debug

            collect_data('UHF',SampleRate,recordtime,SwitchPin,working_dir) # call function to collect data and do whatever else
            # if UHFtimes:
             #   UHFtimes.pop(0)
            time_cleanup(UHFtimes)
            time_cleanup(Lbandtimes)

            move_data(working_dir,data_output_location) # takes all the recorded satllite data in the source folder and puts them on the USB drive
            GPIO.output(LEDPin, GPIO.LOW) # Turn off indicator LED for data collection
        elif 0< Lband_delay_in_seconds < FlybyMargin:
            GPIO.output(LEDPin, GPIO.HIGH) # Turn on indicator LED for data collection
                        
            print('Lband pass') # print debug
            print(Lband_delay_in_seconds) # print debug
            while Lband_delay_in_seconds > .9:
                now = datetime.now()
                Lband_delay_in_seconds = (Lbandtimes[0]-now).total_seconds()
               # print(Lband_delay_in_seconds) # print debug

            collect_data('Lband',SampleRate,recordtime,SwitchPin,working_dir) # call function to collect data and do whatever else
            #if Lbandtimes:
             #   Lbandtimes.pop(0)
            time_cleanup(UHFtimes)
            time_cleanup(Lbandtimes)

            move_data(working_dir,data_output_location) # takes all the recorded satllite data in the source folder and puts them on the USB drive
            GPIO.output(LEDPin, GPIO.LOW) # Turn off indicator LED for data collection

       # elif 0< Lband_delay_in_seconds < FlybyMargin:
           # if debug_en: print('Lband pass') # print debug
            #if debug_en: print(Lband_delay_in_seconds) # print debug
            #collect_data_LBand('Lband',SampleRate,recordtime) # call function to collect data and do whatever else
            #Lbandtimes.pop(0)
        elif UHF_delay_in_seconds<0:
            logging.exception('Missed UHF fly by')
            print('Missed UHF fly by')
            print(UHFtimes)
            time_cleanup(UHFtimes)


        elif Lband_delay_in_seconds<0:
            logging.exception('Missed Lband fly by')
            print('Missed L-Band fly by')
            print(Lbandtimes)
            time_cleanup(Lbandtimes)

        else:
            print('no near pass') # print debug
        #############################################################################################################################
        time.sleep(UnitSleepTime)

if __name__ == "__main__": # if this file is being executed directly then it is the main else it is not google for more info
    main()