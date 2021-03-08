from imutils import paths
import face_recognition
import pickle
import cv2
import os


def train():
    print('[INFO] Beginning training model phase.')
    imagePaths = list(paths.list_images("dataset"))
    knownEncodings = []
    knownNames = []

    # loop over the images
    for (i, imagePath) in enumerate(imagePaths):

        print(f'[INFO] processing image {(i+1)}/{(len(imagePaths))}')
        # extract the person name from the image path
        name = imagePath.split(os.path.sep)[-2]

        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # detect bounding box coordinates of the face
        boxes = face_recognition.face_locations(rgb,
                                                model="hog")

        # compute the facial embeddings
        encodings = face_recognition.face_encodings(rgb, boxes)

        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(name)
    print('[INFO] Writing encoding to file.')
    data = {"encodings": knownEncodings, "names": knownNames}
    with open("encodings.pickle", "wb") as f:
        f.write(pickle.dumps(data))
        f.close()
    print('[INFO] Training model finished.')
