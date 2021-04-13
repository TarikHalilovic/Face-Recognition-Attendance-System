# install opencv-contrib-python, rpi.gpio, dlib, face_recognition, imutils, requests, lcd driver
# run -> python3 main_module.py [-r 1] [-m 0]
# [-r 1] Auto start in recognition mode
# [-m 0] Run without video feedback on display

from add_to_recognizer import adding_to_recognizer
from person_service import edit_person, getPeople, remove_person, list_people
from Trainer import Trainer
from ApiService import ApiService
import recognizer_haar as recognizer
import argparse
import configparser # train

# Preparing arguments
ap = argparse.ArgumentParser()
ap.add_argument("-r", "--run", required=False, help="Add '-r 1' to run in recognition mode")
ap.add_argument("-m", "--mode", required=False, help="Add '-m 0' to run with no camera feed output") # To save resources
ap.add_argument("-i", "--info", required=False, help="Add '-i 1' to run with detailed INFO messages") # More INFO while running
args = vars(ap.parse_args())

print('[INFO] Loading configuration.')
# Config
Config = configparser.ConfigParser()
Config.read("/home/pi/Desktop/face_recognition_for_attendance_rpi/config.ini")

cameraId = int(Config.get('Camera', 'Id'))
scaleFactor = float(Config.get('RecognitionConfig', 'ScaleFactor'))
minSizeTuple = (int(Config.get('RecognitionConfig', 'MinSizeTupleValueOne')), 
                (int(Config.get('RecognitionConfig', 'MinSizeTupleValueTwo'))))
tolerance = float(Config.get('RecognitionConfig', 'Tolerance'))
minNeighbour = int(Config.get('RecognitionConfig', 'MinNeighbour'))
username = Config.get('Server', 'Username')
password = Config.get('Server', 'Password') 
server = Config.get('Server', 'ServerAddr')
            
print('[INFO] Attendance system running.')

# Load up ApiService and get jwt
apiService = ApiService(server, username, password)

# Prepare Trainer so its available
trainer = Trainer(scaleFactor, minNeighbour, minSizeTuple, apiService)

# Additional config
runMode = 1 # 1 - Shows video feedback on desktop, 0 - Does not show
showDetailInfo = False
runWhat = None
if args["run"] is not None:
    runWhat = args["run"]
if args["mode"] is not None:
    runMode = int(args["mode"])
if args["info"] is not None and args["info"] == 1:
    showDetailInfo = True
    
while True:
    print('Please choose: ')
    print('1.) Run face recognition (default)')
    print('2.) Add user')
    print('3.) Edit user')
    print('4.) Remove user')
    print('5.) Retrain model')
    print('6.) Batch add users')
    print('7.) Exit')
    if args["run"] is None:
        runWhat = input()
    if runWhat == '2':
        adding_to_recognizer(cameraId, scaleFactor, minSizeTuple, minNeighbour, apiService, trainer)
    elif runWhat == '3':
        people = getPeople()
        print('Please choose user to edit.')
        list_people(people)
        print(f'{(len(people) + 1)}.) CANCEL (default)')
        choice = int(input())
        if choice - 1 >= len(people):
            continue
        edit_person(people[choice - 1], cameraId, trainer)
    elif runWhat == '4':
        people = getPeople()
        print('Please choose user to remove.')
        list_people(people)
        print(f'{(len(people) + 1)}.) CANCEL (default)')
        choice = int(input())
        if choice - 1 >= len(people):
            continue
        remove_person(people[choice - 1], trainer)
    elif runWhat == '5':
        trainer.train()
    elif runWhat == '6':
        trainer.batch_add_to_system()
    elif runWhat == '7':
        break
    else:
        recognizer.run_recognize(cameraId, scaleFactor, minSizeTuple, tolerance, minNeighbour, apiService, runMode, showDetailInfo)
print('[INFO] Attendance system stopping.')
