from take_image_with_face import face_image_taker
from trainer import train
from api_service import add_person_to_external_system


def adding_to_recognizer(cameraId, scaleFactor, minSizeTuple, minNeighbour, serverUrl,token):
    print('[INFO] Adding new user.')
    firstName = input('First name -> ')
    lastName = input('Last name -> ')
    existingId = input('User Id (Only if already in system, otherwise skip) -> ')
    user_id = None
    if existingId != '':
        user_id = existingId
    else:
        try:
            user_id = add_person_to_external_system(firstName, lastName, serverUrl, token)
        except Exception:
            print('[WARNING] No new additions to the recognition system.')
            return
    success = face_image_taker(f'{user_id} {firstName} {lastName}',
                               cameraId, scaleFactor, minSizeTuple, minNeighbour)

    if not success:
        print('[INFO] No new additions to the recognition system.')
    else:
        train(scaleFactor, minNeighbour, minSizeTuple)
