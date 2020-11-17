# install opencv-contrib-python, rpi.gpio, dlib, face_recognition, imutils, requests, lcd driver
# run -> python main.module.py

from add_to_recognizer import adding_to_recognizer
from person_service import edit_person, getPeople, remove_person, list_people
from trainer import train
import recognizer

cameraId = 0
scaleFactor = 1.2
minSizeTuple = (50, 50)
tolerance = 0.45 # Lower is more strict
minNeighbour = 6
username = 'Administrator'
password = 'qawsed21'
serverUrl = 'http://192.168.137.1:8080'
print('[INFO] Attendance system running.')
while True:
    print('Please choose: ')
    print('1. Run face recognition (default)')
    print('2. Add person')
    print('3. Edit person')
    print('4. Remove person')
    print('5. Retrain model')
    print('6. Exit')
    runWhat = input()
    if runWhat == '2':
        adding_to_recognizer(cameraId, scaleFactor, minSizeTuple, minNeighbour, serverUrl, username, password)
    elif runWhat == '3':
        people = getPeople()
        print('Please choose person to edit.')
        list_people(people)
        print(str(len(people) + 1) + ". CANCEL (default)")
        choice = int(input())
        if choice - 1 >= len(people):
            continue
        edit_person(people[choice - 1], cameraId, scaleFactor, minSizeTuple, minNeighbour)
    elif runWhat == '4':
        people = getPeople()
        print('Please choose person to remove.')
        list_people(people)
        print(str(len(people) + 1) + ". CANCEL (default)")
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
                                 password)
print('[INFO] Attendance system stopping.')
