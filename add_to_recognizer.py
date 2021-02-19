from take_image_with_face import face_image_taker
from trainer import train
from api_service import add_person_to_external_system


def adding_to_recognizer(cameraId, scale_factor, minSizeTuple, minNeighbour, serverUrl, username, password):
    print('[INFO] Adding new person')
    firstName = input('First name -> ')
    lastName = input('Last name -> ')
    existingId = input('Person Id (Only if already in system, otherwise skip) -> ')
    user_id = None
    if existingId != '':
        user_id = existingId
    else:
        user_id = add_person_to_external_system(firstName, lastName, serverUrl, username, password)
    success = face_image_taker(str(user_id) + ' ' + firstName + ' ' + lastName,
                               cameraId, scale_factor, minSizeTuple, minNeighbour)

    if not success:
        print('[INFO] No new additions to the face recognition model.')
    else:
        train()
