from imutils import paths
from faceSize import getBiggestBoxInList
from shutil import copyfile
import face_recognition
import pickle
import cv2
import os

class Trainer:
    def __init__(self, scaleFactor, minNeighbour, minSizeTuple, apiService):
            self.scaleFactor = scaleFactor
            self.minNeighbour = minNeighbour
            self.minSizeTuple = minSizeTuple
            self.apiService = apiService
            
            
    def train(self):
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
            #boxes = face_recognition.face_locations(rgb, model="hog")
            rects = detector.detectMultiScale(gray,
                                              scaleFactor=self.scaleFactor,
                                              minNeighbors=self.minNeighbour,
                                              minSize=self.minSizeTuple,
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
                
        self._save_pickle({"encodings": knownEncodings, "names": knownNames}, "encodings.pickle")
        print('[INFO] Training model finished.')
    
    
    def batch_add_to_system(self):
        print('[INFO] Running batch add.')
        print('Please make folder called "batch_dataset" with subfolders name <firstName lastName> which containt images with one face per image of your users. Folder "batch_dataset" should be located in same directory with main_module.py.')
        print('[WARNING] If you don\'t have this folder, exit the script and restart it after you make preparations.')
        print('[WARNING] Script assumes you don\'t have same users in dataset already.')
        print('Continue? (y/N) -> ')
        if input() != 'y': return
        
        detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        imagePaths = list(paths.list_images("batch_dataset"))
        
        print('Do you wish to manually inspect if all images contain face (option 1, default)\n or do you wish to let system attempt simple scan to see if all images contain one face (option 2)?')
        option = input('-> ')
        
        no_image_alerts = []
        
        seenNumberOfImgs = 0
        
        for (i, imagePath) in enumerate(imagePaths):
            print(f'[INFO] processing image {(i+1)}/{(len(imagePaths))}')
            # extract the person name and id from path
            name = imagePath.split(os.path.sep)[-2]
            
            image = cv2.imread(imagePath)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            rects = detector.detectMultiScale(gray,
                                          scaleFactor=self.scaleFactor,
                                          minNeighbors=self.minNeighbour,
                                          minSize=self.minSizeTuple,
                                          flags=cv2.CASCADE_SCALE_IMAGE)
            boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
            biggestBoxInList = getBiggestBoxInList(boxes)
            
            if int(option) == 2:
                if len(biggestBoxInList) == 0:
                    no_image_alerts.append(f'[ERROR] No face found on image with path: {imagePath}.')
            else:
                if seenNumberOfImgs == 5:
                    cv2.waitKey()
                    seenNumberOfImgs = 0
                    cv2.destroyAllWindows()
                for (x, y, w, h) in rects:
                    cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.imshow(imagePath, image)
                seenNumberOfImgs+=1
        if int(option) == 2:
            if len(no_image_alerts)>0:
                for alert in no_image_alerts:
                    print(alert)
                print('[INFO] Aborting script. Please fix errors above then rerun.')
                return
        else:
            cv2.waitKey()
            cv2.destroyAllWindows()
            if input('If all images contained exactly one face press y/N to continue.') != 'y': return
        # now add new users and get id, then copy images
        users = []
        ids = []
        for (i, imagePath) in enumerate(imagePaths):
            name = imagePath.split(os.path.sep)[-2]
            imgName = imagePath.split(os.path.sep)[-1]
            if not name in users:
                splitName = name.split(' ', 2)
                id = self.apiService.add_person_to_external_system(splitName[0], splitName[1])
                if id == 0:
                    print('[ERROR] Failed to add user to external system.')
                    raise Exception('Failed to add user to external system.')
                users.append(name)
                ids.append(id)
                
                dir_path = f'dataset/{id} {name}'
                self._create_dir(dir_path)
                self._copy_file(imagePath, f'{dir_path}/{imgName}')
            else:
                dir_path = f'dataset/{ids[users.index(name)]} {name}'
                self._copy_file(imagePath, f'{dir_path}/{imgName}')
        # finish with train
        self.train()
                

    def _save_pickle(self, data, pickle_name):
        print('[INFO] Writing encodings to the file.')
        with open("encodings.pickle", "wb") as f:
            f.write(pickle.dumps(data))
            f.close()
    
    
    def _create_dir(self, path):
        try:
            os.mkdir(path)
        except OSError:
            print (f"[ERROR] Creation of the directory {path} failed.")
            raise Exception("Creation of the directory {path} failed.")
        else:
            print (f"[INFO] Successfully created the directory with path {path}")
            
            
    def _copy_file(self, file_path, copy_to_path):
        try:
            copyfile(file_path, copy_to_path)
        except OSError:
            print (f"[ERROR] Failed to copy image with path {file_path}.")
            raise Exception(f"Failed to copy image with path {file_path}.")
        
        