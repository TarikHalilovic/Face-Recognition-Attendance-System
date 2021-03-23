from imutils.video import VideoStream
from imutils import resize
from time import sleep, strftime, time as getCurrentTime, localtime as getLocalTime
from api_service import post_action
from Lcd import lcddriver
from Model.LastPersonEntry import LastPersonEntry
from faceSize import getBiggestBoxInList
import face_recognition
import pickle
import cv2
import RPi.GPIO as GPIO

whoIsLocked = None
inActionLock = False
lastPersonEntry = None

def buzzer_quick_alert(buzzer, dutyCycle):
    buzzer.ChangeFrequency(600)
    buzzer.start(dutyCycle)
    sleep(0.15)
    buzzer.stop()


def buzzer_ok(buzzer, dutyCycle):
    buzzer.ChangeFrequency(600)
    buzzer.start(dutyCycle)
    sleep(0.5)
    buzzer.stop()


def buzzer_error(buzzer, dutyCycle):
    buzzer.ChangeFrequency(1200)
    buzzer.start(dutyCycle)
    sleep(0.25)
    buzzer.stop()
    sleep(0.25)
    buzzer.start(dutyCycle)
    sleep(0.25)
    buzzer.stop()
    sleep(0.25)
    buzzer.start(dutyCycle)
    sleep(0.25)
    buzzer.stop()


def run_recognize(cameraId, scaleFactor, minSizeTuple, tolerance, minNeighbour, serverUrl
                  ,token, runMode, showDetailInfo):
    try:
        global whoIsLocked, inActionLock
        timeOfLock = None
        currentPerson = None
        alpha = 1.20 # Contrast control (1.0-3.0)
        beta = 21 # Brightness control (0-100)

        # Buttons to GPIO pins (physical numbering)
        buttonStart = 11
        buttonBreak = 21
        buttonTask = 22
        buttonEnd = 24
        buzzerPin = 13

        bounceTime = 230 # Used when setting up events as bounce prevent time
        buzzerDutyCycle = 0.7
        lockInTime = 6.5 # How much time user has to choose action
        
        display = lcddriver.lcd() # My display has 16 characters maximum; 2 lines

        GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
        GPIO.setup(buttonStart, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(buttonEnd, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(buttonBreak, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(buttonTask, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(buzzerPin, GPIO.OUT)
        buzzer = GPIO.PWM(buzzerPin, 1200)

        def map_button_to_eventId(button):
            if button == buttonStart:
                return 1
            elif button == buttonBreak:
                return 2
            elif button == buttonTask:
                return 3
            elif button == buttonEnd:
                return 4
            else:
                raise Exception(f'Button not mapped to any event. GPIO pin: {button}')


        def event_callback(button):
            # Setting up globals
            global whoIsLocked, inActionLock, lastPersonEntry
            
            if inActionLock:
                buzzer_quick_alert(buzzer, buzzerDutyCycle)
                print(f'[INFO] [{strftime("%m-%d %H:%M:%S", getLocalTime())}] Action prevented, ongoing action.')
                return
            if whoIsLocked is None:
                buzzer_quick_alert(buzzer, buzzerDutyCycle)
                print(f'[INFO] [{strftime("%m-%d %H:%M:%S", getLocalTime())}] Action prevented, nobody in lock.')
                return
                
            actionTime = getCurrentTime()
            
            # To prevent button bouncing
            #if (lastPersonEntry is not None and 
            #    lastPersonEntry.time+9 > actionTime):
            #    # remove print in final version
            #    if showDetailInfo:
            #        print('[INFO] Bounce prevented (not enough time passed between actions.')
            #    return
            
            eventId = map_button_to_eventId(button)
            
            # Prevent bouncing if last person = current person in X seconds timeframe
            if (lastPersonEntry is not None and
                    lastPersonEntry.personId == whoIsLocked[0] and
                    lastPersonEntry.eventId == eventId and
                    actionTime < lastPersonEntry.time + 20):
                if showDetailInfo:
                    print(f'[INFO] [{strftime("%m-%d %H:%M:%S", getLocalTime())}] Action prevented. Same person, same action. Minimum time has not passed. Time remaining is {(round(lastPersonEntry.time+20 - actionTime, 1))}s.')
                return

            inActionLock = True # Running the command, no interrupts
            display.lcd_clear()

            # This is new last person
            lastPersonEntry = LastPersonEntry(actionTime, eventId, whoIsLocked[0]) 

            if whoIsLocked[0] is None: # id is None which means user is Unknown
                print(f'[{strftime("%m-%d %H:%M:%S", getLocalTime())}] Message -> Person not recognized, please look at camera and try again.')
                response = post_action(None, eventId, serverUrl, token)
                if response.serverError:
                    print(f'[{strftime("%m-%d %H:%M:%S", getLocalTime())}] [ERROR] Server error.')
                display.lcd_display_string("Not recognized", 1)
                display.lcd_display_string("Please try again", 2)
                buzzer_error(buzzer, buzzerDutyCycle)
            else: # User is known
                response = post_action(whoIsLocked[0], eventId, serverUrl, token)
                if showDetailInfo:
                    print(f'[INFO] [{strftime("%m-%d %H:%M:%S", getLocalTime())}] User logged with id -> {whoIsLocked[0]}')
                if not response.serverError:
                    if response.message is not None: 
                        print(f'Message -> {response.message}')
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
                            display.lcd_display_string(whoIsLocked[1], 2)
                            buzzer_ok(buzzer, buzzerDutyCycle)
                        elif response.messageCode == 5:
                            display.lcd_display_string("Have fun", 1)
                            display.lcd_display_string(whoIsLocked[1], 2)
                            buzzer_ok(buzzer, buzzerDutyCycle)
                        elif response.messageCode == 6:
                            display.lcd_display_string("Stay safe", 1)
                            display.lcd_display_string(whoIsLocked[1], 2)
                            buzzer_ok(buzzer, buzzerDutyCycle)
                        elif response.messageCode == 7:
                            display.lcd_display_string("Goodbye", 1)
                            display.lcd_display_string(whoIsLocked[1], 2)
                            buzzer_ok(buzzer, buzzerDutyCycle)
                        elif response.messageCode == 8:
                            display.lcd_display_string("Welcome back", 1)
                            display.lcd_display_string(whoIsLocked[1], 2)
                            buzzer_ok(buzzer, buzzerDutyCycle)
                        elif response.messageCode == 9:
                            display.lcd_display_string("Not recognized", 1)
                            display.lcd_display_string("Please try again", 2)
                            buzzer_ok(buzzer, buzzerDutyCycle)
                            if showDetailInfo:
                                print('[WARNING] Message code 9 appeared.')
                        else:
                            display.lcd_display_string("Unknown message", 1)
                            display.lcd_display_string("      code",2)
                else:
                    display.lcd_display_string("  Server error", 1)
                    buzzer_error(buzzer, buzzerDutyCycle)
            sleep(3.9) # Shows lcd text and locks actions for time
            display.lcd_clear()
            inActionLock = False


        GPIO.add_event_detect(buttonStart, GPIO.RISING, callback=lambda x: event_callback(buttonStart), bouncetime=bounceTime)
        GPIO.add_event_detect(buttonEnd, GPIO.RISING, callback=lambda x: event_callback(buttonEnd), bouncetime=bounceTime)
        GPIO.add_event_detect(buttonBreak, GPIO.RISING, callback=lambda x: event_callback(buttonBreak), bouncetime=bounceTime)
        GPIO.add_event_detect(buttonTask, GPIO.RISING, callback=lambda x: event_callback(buttonTask), bouncetime=bounceTime)

        print(f'[INFO] [{strftime("%m-%d %H:%M:%S", getLocalTime())}] Loading encodings from file.')
        try:
            # Using absolute path, take caution
            data = pickle.loads(open('/home/pi/Desktop/face_recognition_for_attendance_rpi/encodings.pickle', 'rb').read())
        except Exception as e:
            print(f'[ERROR] No faces in the model. Error: {e}')
            raise Exception('Error on loading pickle file.')

        detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        print(f'[INFO] [{strftime("%m-%d %H:%M:%S", getLocalTime())}] Starting video stream, press "q" to exit.')
        vs = VideoStream(src=cameraId).start()
        sleep(1.3) # Warm up
        
        while True:
            thisFrameTime = getCurrentTime()
            
            frame = vs.read()
            # choose lower width for performance
            frame = resize(frame, width=700)
            # increase brightness and contrast for a bit
            frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

            # 1) BGR to grayscale: for face detection
            # 2) BGR to RGB: for face recognition
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # grayscale frame
            # detectMultiScale autoconverts to greyscale if not in greyscale
            rects = detector.detectMultiScale(gray,
                                              scaleFactor=scaleFactor,
                                              minNeighbors=minNeighbour,
                                              minSize=minSizeTuple,
                                              flags=cv2.CASCADE_SCALE_IMAGE)

            # prepare coordinates for face_recognition function
            boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

            # get biggest box
            biggestBoxInList = getBiggestBoxInList(boxes)

            encodings = face_recognition.face_encodings(rgb, biggestBoxInList)
            names = []
            for encoding in encodings:
                matches = face_recognition.compare_faces(data['encodings'],
                                                         encoding,
                                                         tolerance=tolerance)
                name = (None, 'Unknown')
                if True in matches:
                    matchedIds = [i for (i, b) in enumerate(matches) if b]
                    counts = {}
                    for i in matchedIds:
                        name = data['names'][i]
                        counts[name] = counts.get(name, 0) + 1
                    name = max(counts, key=counts.get)
                    
                    # split id and name
                    splitName = name.split(' ', 1)
                    # set name to tuple (id, user)
                    name = (splitName[0], splitName[1])
                names.append(name)

            if len(names) > 0:
                currentPerson = names[0] # Pick first and only from array
                
                if whoIsLocked is None and inActionLock == False:
                        # perpare name because display has 16 chars max
                        if (currentPerson[0] is not None and len(currentPerson[1]) > 16):
                            currentPerson = (currentPerson[0] ,currentPerson[1][0:16])
                
                        display.lcd_clear()
                        display.lcd_display_string("Choose input", 1)
                        display.lcd_display_string(currentPerson[1], 2)
                        timeOfLock = thisFrameTime
                        # Setting variable to tuple (id/None,user/Unknown)   
                        whoIsLocked = currentPerson
            else:
                currentPerson = None

            if whoIsLocked is not None and inActionLock == False:
                # first check: if initial lock-on was on Unknown but now we have real user, if that happens lock in on real user
                # second check is to give user enough time to choose input
                if (whoIsLocked[0] is None and currentPerson is not None and
                    currentPerson[0] is not None):
                    whoIsLocked = None
                    display.lcd_clear()
                    timeOfLock = thisFrameTime # refresh time of lock
                    display.lcd_display_string("Choose input", 1)
                    display.lcd_display_string(currentPerson[1], 2)
                    sleep(0.1) # delay a bit to let display fully load characters
                    whoIsLocked = currentPerson
                elif timeOfLock+lockInTime < thisFrameTime:
                    whoIsLocked = None
                    display.lcd_clear()
                    
            # This is used just to show who is locked in on video feedback
            if runMode == 1 and whoIsLocked is not None:
                timeLeft = round(timeOfLock+lockInTime - thisFrameTime,1)
                if timeLeft > 0: # Countdown goes on if action ran
                    # WhoIsLocked[1] is name/Unknown
                    cv2.putText(frame, f'{whoIsLocked[1]} ({timeLeft}s)', (38, 38), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

            # This is for drawing on screen and can be disabled if no display
            if runMode == 1:
                for ((top, right, bottom, left), name) in zip(biggestBoxInList, names):
                    cv2.rectangle(frame, (left, top), (right, bottom),
                                  (0, 255, 0), 2)
                    y = top - 15 if top - 15 > 15 else top + 15
                    cv2.putText(frame, currentPerson[1], (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 255, 0), 2)
                # display video
                cv2.imshow('Camera', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
        
    finally:
        # cleanup
        cv2.destroyAllWindows()
        vs.stop()
        buzzer.stop()
        display.lcd_clear()
        GPIO.cleanup()
        print(f'[INFO] [{strftime("%m-%d %H:%M:%S", getLocalTime())}] Recognizer finished.')
