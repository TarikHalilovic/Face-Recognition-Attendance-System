import cv2
import os
import copy


def delete_from_folder(dir_name):
    for filename in os.listdir(dir_name):
        file_path = os.path.join(dir_name, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
        except Exception as e:
            print('[ERROR] Failed to delete %s. Reason: %s' % (file_path, e))
            return False


def face_image_taker(name, cameraId, scale_factor, minSizeTuple, minNeighbour):
    dirName = './dataset/' + name
    if not os.path.exists(dirName):
        os.makedirs(dirName)
        print('[INFO] Directory for ' + name + '\'s images created.')
    else:
        print('[ERROR] Name already exists.')
        return False

    count = 0

    while True:
        print('Press "t" to take a image.')
        print('Please take at least 1 image with only one face clearly visible.')
        print('Press "q" when you have enough images.')
        faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        video_capture = cv2.VideoCapture(cameraId)
        while True:
            ret, frame = video_capture.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=scale_factor,
                minNeighbors=minNeighbour,
                minSize=minSizeTuple,
                flags=cv2.CASCADE_SCALE_IMAGE
            )

            frameWithFace = copy.deepcopy(frame)
            for (x, y, w, h) in faces:
                frameWithFace = cv2.rectangle(frameWithFace, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Draw number count on frame
            frameWithFaceAndText = cv2.putText(
                frameWithFace,
                str(count),
                (25, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 0),
                2
            )

            # Display the resulting frame
            cv2.imshow('Position for face scanning.', frameWithFaceAndText)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            if key == ord('t'):
                count += 1
                fileName = dirName + "/" + name + str(count) + ".jpg"
                cv2.imwrite(fileName, frame)
        video_capture.release()
        cv2.destroyAllWindows()

        if count < 1:
            print('[ERROR] Deleting directory for ' + name + '. Not enough images taken.')
            delete_from_folder(dirName)
            os.rmdir(dirName)
            return False
        else:
            print('[INFO] Please manually remove images that do not show face properly. At least 1 image is needed.')
            countOfImagesLeft = len([name for name in os.listdir(dirName)])
            redoImageTaking = input('Do you want to redo face image adding process? y/N -> ')
            if redoImageTaking == 'y' or countOfImagesLeft < 3:
                if countOfImagesLeft < 3:
                    print('[INFO] Can not continue, not enough face images.')
                print('[INFO] Deleting images, then redoing image taking process.')
                count = 0
                delete_from_folder(dirName)
            else:
                return True
