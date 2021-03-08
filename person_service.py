import os
from trainer import train
from take_image_with_face import delete_from_folder
from take_image_with_face import face_image_taker


def edit_person(fullName, cameraId, scale_factor, minSizeTuple, minNeighbour):
    print(f'[INFO] Editing -> {fullName}')
    print('Please choose: ')
    print('1.) Rename')  # change folder name, retrain
    print('2.) Retake facial data')  # delete folder, retake images, retrain
    print('3.) Cancel (default)')
    choice = input()

    if choice == '1':
        newFirstName = input('First name -> ')
        newLastName = input('Last name -> ')
        current_id = fullName.split(' ', 1)
        print('[INFO] Renaming directory.')
        os.rename(f'./dataset/{fullName}', f'./dataset/{current_id[0]} {newFirstName} {newLastName}')
        train()
    elif choice == '2':
        print('[INFO] Deleting all images from directory and directory itself.')
        delete_from_folder(f'./dataset/{fullName}')
        os.rmdir(f'./dataset/{fullName}')
        success = face_image_taker(fullName, cameraId, scale_factor, minSizeTuple, minNeighbour)
        if not success:
            print('[INFO] Removing person from recognition model.')
        train()
    else:
        print('[INFO] Editing canceled.')

def getPeople():
    return [f.name for f in os.scandir('./dataset') if f.is_dir()]

def remove_person(fullName):
    print('[INFO] Removing all images for person and deleting directory.')
    delete_from_folder(f'./dataset/{fullName}')
    os.rmdir(f'./dataset/{fullName}')
    train()
    
def list_people(people):
    for p in people:
        print(f'{(people.index(p) + 1)}.) {(p.split(" ", 1)[1])}')
    
