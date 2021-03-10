# install opencv-contrib-python, rpi.gpio, dlib, face_recognition, imutils, requests, lcd driver
# run -> python3 main_module.py [-r 1] [-m 0]
# [-r 1] Auto start in recognition mode
# [-m 0] Run without video feedback on display

from add_to_recognizer import adding_to_recognizer
from person_service import edit_person, getPeople, remove_person, list_people
from trainer import train
from api_service import server_connection_test
import recognizer_haar as recognizer
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-r", "--run", required=False, help="Add '-r 1' to run in recognition mode")
ap.add_argument("-m", "--mode", required=False, help="Add '-m 0' to run with no camera feed output") # To save resources
args = vars(ap.parse_args())

cameraId = 0
scaleFactor = 1.2
minSizeTuple = (90, 90)
tolerance = 0.52 # Lower is more strict
minNeighbour = 6
runMode = 1 # 1 - Shows video feedback on desktop, 0 - Does not show
username = 'Admin'
password = 'a'
serverUrl = 'http://192.168.137.1:8080'
print('[INFO] Attendance system running.')

# Check if you can reach server
server_connection_test(serverUrl, username, password)

runWhat = None
if args["run"] is not None:
    runWhat = args["run"]
if args["mode"] is not None:
    runMode = int(args["mode"])

while True:
    print('Please choose: ')
    print('1.) Run face recognition (default)')
    print('2.) Add user')
    print('3.) Edit user')
    print('4.) Remove user')
    print('5.) Retrain model')
    print('6.) Exit')
    if args["run"] is None:
        runWhat = input()
    if runWhat == '2':
        adding_to_recognizer(cameraId, scaleFactor, minSizeTuple, minNeighbour, serverUrl, username, password)
    elif runWhat == '3':
        people = getPeople()
        print('Please choose user to edit.')
        list_people(people)
        print(f'{(len(people) + 1)}.) CANCEL (default)')
        choice = int(input())
        if choice - 1 >= len(people):
            continue
        edit_person(people[choice - 1], cameraId, scaleFactor, minSizeTuple, minNeighbour)
    elif runWhat == '4':
        people = getPeople()
        print('Please choose user to remove.')
        list_people(people)
        print(f'{(len(people) + 1)}.) CANCEL (default)')
        choice = int(input())
        if choice - 1 >= len(people):
            continue
        remove_person(people[choice - 1])
    elif runWhat == '5':
        train()
    elif runWhat == '6':
        break
    else:
        recognizer.run_recognize(cameraId, scaleFactor, minSizeTuple, tolerance, minNeighbour, serverUrl, username,
                                 password, runMode)
print('[INFO] Attendance system stopping.')
