from imutils.video import VideoStream
import face_recognition
import imutils
import pickle
from time import sleep, time as getCurrentTime
import cv2
from api_service import post_action
import RPi.GPIO as GPIO
from Lcd import lcddriver

from Model.LastPersonEntry import LastPersonEntry

currentPerson = ""
currentStatus = 0 # 0 = No face; -1 = Unknown; 1 = Known
currentTime = getCurrentTime()
userLocked = False
timeOfLock = None
whoIsLocked = None
inActionLock = False
statusForInLock = 0
lastPersonEntry = None # Could be 'Unknown' user as well


def getBoxArea(aBox):
    return (aBox[1] - aBox[3]) * (aBox[2] - aBox[0])


def getBiggestBoxInList(allBoxes):
    biggestBoxInAList = []
    if len(allBoxes) == 0:
        return biggestBoxInAList
    elif len(allBoxes) == 1:
        return allBoxes
    currentBiggest = allBoxes[0]
    currentBiggestArea = getBoxArea(currentBiggest)
    for i in range(1, len(allBoxes)):
        areaOfABox = getBoxArea(allBoxes[i])
        if currentBiggestArea < areaOfABox:
            currentBiggestArea = areaOfABox
            currentBiggest = allBoxes[i]
    biggestBoxInAList.append(currentBiggest)
    return biggestBoxInAList


def buzzer_ok(buzzer, dutyCycle):
    buzzer.ChangeFrequency(600)
    buzzer.start(dutyCycle)
    sleep(0.7)
    buzzer.stop()


def buzzer_error(buzzer, dutyCycle):
    buzzer.ChangeFrequency(1200)
    buzzer.start(dutyCycle)
    sleep(0.3)
    buzzer.stop()
    sleep(0.3)
    buzzer.start(dutyCycle)
    sleep(0.3)
    buzzer.stop()
    sleep(0.3)
    buzzer.start(dutyCycle)
    sleep(0.3)
    buzzer.stop()


def run_recognize(cameraId, scaleFactor, minSizeTuple, tolerance, minNeighbour, serverUrl
                  , username, password, runMode):
    global currentPerson, currentStatus, userLocked, timeOfLock, whoIsLocked, inActionLock, statusForInLock
    alpha = 1.20 # Contrast control (1.0-3.0) #1.2
    beta = 20 # Brightness control (0-100) #17

    # Buttons to GPIO pins (physical numbering)
    buttonStart = 19
    buttonEnd = 24
    buttonBreak = 21
    buttonTask = 22
    buzzerPin = 13

    bounceTime = 230 # Used when setting up events as bounce prevent time
    buzzerDutyCycle = 0.7
    display = lcddriver.lcd() # My display has 16 characters maximum; 2 lines

    GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
    GPIO.setup(buttonStart, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(buttonEnd, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(buttonBreak, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(buttonTask, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(buzzerPin, GPIO.OUT)
    buzzer = GPIO.PWM(buzzerPin, 1200)

    def map_button_to_eventId(button):
        eventId = None
        if button == buttonStart:
            eventId = 1
        elif button == buttonBreak:
            eventId = 2
        elif button == buttonTask:
            eventId = 3
        elif button == buttonEnd:
            eventId = 4
        else:
            raise Exception('Button was not mapped to event. Unknown button: ' + str(button))
        return eventId

    def event_callback(button):
        # Setting up globals
        global currentTime, whoIsLocked, inActionLock, statusForInLock, lastPersonEntry
        
        # To prevent button bouncing
        if currentTime+3.3 > getCurrentTime():
            print('[INFO] Bounce prevented by time')
            return

        if whoIsLocked is None or inActionLock == True:
            print('[INFO] Action prevented, nobody in lock or ongoing action')
            return

        # If check below needs personId, eventId and currentTime
        personId = None
        eventId = map_button_to_eventId(button)
        currentTime = getCurrentTime()
        if statusForInLock == 1:
            personId = int(whoIsLocked.split(' ',1)[0])
        # Prevent bouncing if last person = current person in ~15 seconds timeframe
        if (lastPersonEntry is not None and
                lastPersonEntry.personId == personId and
                lastPersonEntry.eventId == eventId and
                currentTime < lastPersonEntry.time + 15):
            print('[INFO] Action prevented. Same person, same action, minimum time has not passed.')
            return

        inActionLock = True # Running the command, no interrupts
        display.lcd_clear()

        lastPersonEntry = LastPersonEntry(currentTime, eventId, None) # This is new last person

        if statusForInLock == -1:
            print('Person not recognized, please look at camera and try again.')
            post_action(None, eventId, serverUrl, username, password) # note: not checking for errors
            display.lcd_display_string("Not recognized", 1)
            display.lcd_display_string("Please try again", 2)
            buzzer_error(buzzer, buzzerDutyCycle)
        else: # statusForInLock is 1
            lastPersonEntry.personId = personId # Id was None, now update it
            
            response = post_action(personId, eventId, serverUrl, username, password)
            print('[INFO] Person logged with id -> ' + str(personId))
            if not response.serverError:
                if response.message is not None: 
                    print('Message -> ' + response.message)
                    if response.messageCode == 1:
                        display.lcd_display_string("  Work already", 1)
                        display.lcd_display_string("    started", 2)
                        buzzer_error(buzzer, buzzerDutyCycle)
                    elif response.messageCode == 2:
                        display.lcd_display_string("    Work not", 1)
                        display.lcd_display_string("    started", 2)
                        buzzer_error(buzzer, buzzerDutyCycle)
                    elif response.messageCode == 3:
                        display.lcd_display_string("  Actions not", 1)
                        display.lcd_display_string("    finished", 2)
                        buzzer_error(buzzer, buzzerDutyCycle)
                    elif response.messageCode == 4:
                        display.lcd_display_string("Welcome", 1)
                        display.lcd_display_string(response.fullName, 2)
                        buzzer_ok(buzzer, buzzerDutyCycle)
                    elif response.messageCode == 5:
                        display.lcd_display_string("Have fun", 1)
                        display.lcd_display_string(response.fullName, 2)
                        buzzer_ok(buzzer, buzzerDutyCycle)
                    elif response.messageCode == 6:
                        display.lcd_display_string("Stay safe", 1)
                        display.lcd_display_string(response.fullName, 2)
                        buzzer_ok(buzzer, buzzerDutyCycle)
                    elif response.messageCode == 7:
                        display.lcd_display_string("Goodbye", 1)
                        display.lcd_display_string(response.fullName, 2)
                        buzzer_ok(buzzer, buzzerDutyCycle)
                    elif response.messageCode == 8:
                        display.lcd_display_string("Welcome back", 1)
                        display.lcd_display_string(response.fullName, 2)
                        buzzer_ok(buzzer, buzzerDutyCycle)
                    else:
                        display.lcd_display_string("Unknown message", 1)
                        display.lcd_display_string("      code",2)
            else:
                display.lcd_display_string("  Server error", 1)
                buzzer_error(buzzer, buzzerDutyCycle)
        sleep(5) # Shows lcd text and locks actions for time
        display.lcd_clear()
        inActionLock = False

    GPIO.add_event_detect(buttonStart, GPIO.RISING, callback=lambda x: event_callback(buttonStart), bouncetime=bounceTime)
    GPIO.add_event_detect(buttonEnd, GPIO.RISING, callback=lambda x: event_callback(buttonEnd), bouncetime=bounceTime)
    GPIO.add_event_detect(buttonBreak, GPIO.RISING, callback=lambda x: event_callback(buttonBreak), bouncetime=bounceTime)
    GPIO.add_event_detect(buttonTask, GPIO.RISING, callback=lambda x: event_callback(buttonTask), bouncetime=bounceTime)

    print('[INFO] Loading encodings from file.')
    try:
        # Using absolute path, take caution
        data = pickle.loads(open('/home/pi/Desktop/face_recognition_for_attendance_rpi/encodings.pickle', 'rb').read())
    except Exception as e:
        print('[ERROR] No faces in the model. Error: ', e)
        raise Exception('Error on loading pickle.')

    detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    print('[INFO] Starting video stream, press "q" to exit.')
    vs = VideoStream(src=cameraId).start()
    sleep(1.3) # Warm up
    
    while True:
        frame = vs.read()
        # resize for performance
        frame = imutils.resize(frame, width=650)
        # increase brightness and contrast for a bit
        frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

        # 1) BGR to grayscale: for face detection
        # 2) BGR to RGB: for face recognition
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # grayscale frame
        rects = detector.detectMultiScale(gray,
                                          scaleFactor=scaleFactor,
                                          minNeighbors=minNeighbour,
                                          minSize=minSizeTuple,
                                          flags=cv2.CASCADE_SCALE_IMAGE)

        # box coordinates are in (x, y, w, h) order; change order
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

        # get biggest box
        biggestBoxInList = getBiggestBoxInList(boxes)

        encodings = face_recognition.face_encodings(rgb, biggestBoxInList)
        names = []
        currentStatus = 0 # If it doesnt change - means no users/unknowns
        for encoding in encodings:
            matches = face_recognition.compare_faces(data['encodings'],
                                                     encoding,
                                                     tolerance=tolerance)
            name = 'Unknown'
            currentStatus = -1 # If it doesnt change - means we have an unknown
            if True in matches:
                currentStatus = 1 # Means you have a recognized user
                
                matchedIds = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                for i in matchedIds:
                    name = data['names'][i]
                    counts[name] = counts.get(name, 0) + 1

                name = max(counts, key=counts.get)
            names.append(name)

        if len(names) > 0:
            currentPerson = names[0]
            
            if userLocked == False and inActionLock == False:
                    userLocked = True
                    timeOfLock = getCurrentTime()
                    display.lcd_display_string("Choose input", 1)
                    if currentStatus == 1:
                        statusForInLock = 1
                        display.lcd_display_string(names[0].split(' ', 1)[1], 2) # names[0] is formatted as "[id] [name]"
                    else:
                        statusForInLock = -1
                        display.lcd_display_string(names[0], 2)
                    whoIsLocked = currentPerson
        else:
            currentPerson = ""

        if userLocked == True and inActionLock == False:
            # Check if user was locked for time, then unlock
            # Second check is to switch from Unknown to real user if he was not recognized and then recognized
            if timeOfLock+6 < getCurrentTime() or (statusForInLock == -1 and currentStatus == 1):
                userLocked = False
                display.lcd_clear()
                whoIsLocked = None
                statusForInLock = 0

        # This is for drawing on screen and can be disabled if no display
        if runMode == 1:
            for ((top, right, bottom, left), name) in zip(biggestBoxInList, names):
                cv2.rectangle(frame, (left, top), (right, bottom),
                              (0, 255, 0), 2)
                y = top - 15 if top - 15 > 15 else top + 15
                if currentStatus == 1:
                    name = name.split(' ', 1)[1]
                cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                            0.75, (0, 255, 0), 2)
            # display video
            cv2.imshow('Camera', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    # cleanup
    cv2.destroyAllWindows()
    vs.stop()
    buzzer.stop()
    display.lcd_clear()
    GPIO.cleanup()
    print('[INFO] Recognizer finished.')
