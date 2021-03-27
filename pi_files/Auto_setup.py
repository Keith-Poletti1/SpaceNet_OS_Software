import shutil
import os

def main():
    #move files to desktop
    for filename in os.listdir(os.path.dirname(os.path.realpath(__file__))):
        if (filename.endswith(".log") or filename.endswith(".py")) and not filename==__file__: 
            dst = '/home/pi/Desktop/'+filename
            print(filename+ ' goes to '+dst)
            os.system('sudo cp '+filename +' '+dst)

        elif filename.endswith(".service"):
            dst = '/lib/systemd/system/'+filename
            print(filename+ ' goes to '+dst)
            os.system('sudo cp '+filename +' '+dst)
            #shutil.copy(filename,dst)
            # complies and enable service
            os.system('sudo systemctl daemon-reload')
            os.system('sudo systemctl enable '+filename)
        else:
            pass

    # Install packages
    os.system('sudo apt-get install hackrf libhackrf-dev libhackrf0')
    os.system('sudo pip install pynmea2')
    os.system('sudo apt-get install python-serial')
    os.system('sudo apt-get update')
    os.system('sudo apt-get install')

    #turn on VNC????`

if __name__ =='__main__':
    main()
