import time
import serial
import string
import pynmea2
import datetime
from datetime import timedelta
import operator
import sys
import os


def checksum(sentence):
  sentence = sentence.strip('\n')
  try:
    nmeadata,cksum = sentence.split('*', 1)
    calc_cksum = reduce(operator.xor, (ord(s) for s in nmeadata), 0)
    return nmeadata,int(cksum,16),calc_cksum  
  except ValueError:
    return False

def getGPS():
    fetchDT = 0
    #port = "/dev/ttyS0"
    port = "/dev/ttyAMA0"
    ser = serial.Serial(port, baudrate = 9600, timeout = 5)
    flag = True
    while flag:
        try:
            while(ser.inWaiting() >0):
                data = ser.readline().rstrip()
                if data[0:6] == "$GPRMC":
                    print ("")
                    if checksum(data) != False:
                        splitData = data.split(",")
                        if splitData[2] == 'A': #Valid GPS TIME
        #               print (data)
                            msg = pynmea2.parse(data)
                            dateStr="20"+splitData[9][4:6]+"-"+splitData[9][2:4]+"-"+splitData[9][0:2]
                            dtStr = dateStr + " " + str(msg.timestamp)
                            dt = datetime.datetime.strptime(dtStr, "%Y-%m-%d %H:%M:%S") + timedelta(hours=0)  #OFFSET GMT8
                            os.system("sudo date -s '"+str(dt)+"'")
                            flag = False
    #               print ("GPS TIME: " +str(dt))
    #               now = datetime.datetime.now()
    #               print ("SYS TIME: " +str(now.strftime("%Y-%m-%d %H:%M:%S")))
    #               if dt > now:
    #                 print ("GPS TIME IS NOW AHEAD OF SYS TIME")
    #                 os.system("sudo date -s '"+str(dt)+"'")
    #                 flag = False
    #               else:
    #                 print ("SYS TIME IS NOW AHEAD OF GPS TIME")
    #                 os.system("sudo date -s '"+str(dt)+"'")
    #                 flag = False
    #               if fetchDT >= 60:
    #                 print ("FINISH");
    #                 print (msg.timestamp);
    #                 ser.close()
    #                 sys.exit(0)
    #                 exit();
    #                 quit()
    #               fetchDT+=1;

        except pynmea2.nmea.ChecksumError as e:
          print("No data this time 0")
          ser.close()
          time.sleep(3)
          getGPS()
        except serial.SerialException as e:
          print("No data this time 1")
          ser.close()
          time.sleep(3)
          getGPS()
        except TypeError as e:
          print("No data this time 3")
          ser.close()
          time.sleep(3)
          getGPS()
        except serial.serialutil.SerialException:
          print("No data this time 4")
          ser.close()
          time.sleep(3)
          getGPS()
        except IOError as e:
          #print("No data this time")
          ser.close()
          getGPS()
        except (KeyboardInterrupt, SystemExit):
          print ("Exiting")
          ser.close()
          exit()
        except Exception as e:
          print("No data this time 4")
          ser.close()
          time.sleep(3)
          getGPS()
      
if __name__ == "__main__":
    
    #port = "/dev/ttyS0"
    #port = "/dev/ttyAMA0"
    #fetchDT = 0;
    #now = datetime.datetime.now()  
    getGPS()
