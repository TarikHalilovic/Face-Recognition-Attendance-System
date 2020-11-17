from imutils import paths
import face_recognition
import pickle
import cv2
import os


def train():
    print('[INFO] Beginning training model phase.')
    print("[INFO] Quantifying faces...")
    imagePaths = list(paths.list_images("dataset"))
    knownEncodings = []
    knownNames = []

    # loop over the image paths
    for (i, imagePath) in enumerate(imagePaths):
        # extract the person name from the image path
        print("[INFO] processing image {}/{}".format(i + 1,
                                                     len(imagePaths)))
        name = imagePath.split(os.path.sep)[-2]

        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # detect the (x, y)-coordinates of the bounding boxes
        # corresponding to each face in the input image
        boxes = face_recognition.face_locations(rgb,
                                                model="hog")

        # compute the facial embedding for the face
        encodings = face_recognition.face_encodings(rgb, boxes)

        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(name)
    print('[INFO] Serializing encodings.')
    data = {"encodings": knownEncodings, "names": knownNames}
    with open("encodings.pickle", "wb") as f:
        f.write(pickle.dumps(data))
        f.close()
    print('[INFO] Training model finished.')
