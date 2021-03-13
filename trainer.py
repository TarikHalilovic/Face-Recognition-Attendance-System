from imutils import paths
from faceSize import getBiggestBoxInList
import face_recognition
import pickle
import cv2
import os


def train(scaleFactor, minNeighbour, minSizeTuple):
    print('[INFO] Beginning training model phase.')
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    imagePaths = list(paths.list_images("dataset"))
    knownEncodings = []
    knownNames = []

    # loop over all images
    for (i, imagePath) in enumerate(imagePaths):

        print(f'[INFO] processing image {(i+1)}/{(len(imagePaths))}')
        # extract the person name and id from path
        name = imagePath.split(os.path.sep)[-2]

        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # detect bounding box coordinates of the face
        
        # Uncomment to use HOG instead of Viola Jones
        #boxes = face_recognition.face_locations(rgb,
        #                                        model="hog")
        rects = detector.detectMultiScale(gray,
                                          scaleFactor=scaleFactor,
                                          minNeighbors=minNeighbour,
                                          minSize=minSizeTuple,
                                          flags=cv2.CASCADE_SCALE_IMAGE)
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
        biggestBoxInList = getBiggestBoxInList(boxes)
        
        # warn if no face found on image while in training
        if len(biggestBoxInList) == 0:
            print(f'[WARNING] No face found on image with path: {imagePath}.')

        # compute encodings
        encodings = face_recognition.face_encodings(rgb, boxes)

        # write encodings to the pickle
        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(name)
    print('[INFO] Writing encodings to the file.')
    data = {"encodings": knownEncodings, "names": knownNames}
    with open("encodings.pickle", "wb") as f:
        f.write(pickle.dumps(data))
        f.close()
    print('[INFO] Training model finished.')
