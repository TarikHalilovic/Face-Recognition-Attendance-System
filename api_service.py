import requests
from requests.auth import HTTPBasicAuth
from ActionResponse import ActionResponse

def post_action(userId, buttonId, serverUrl, username, password):
    response = requests.post(
        url=serverUrl + '/api/attendance/insert',
        json={'personnelId': userId, 'buttonId': buttonId},
        headers={'Content-Type': 'application/json'},
        auth=HTTPBasicAuth(username, password)
    )
    #               serverError, isSuccessful, statusCode, message, fullName, errorCode
    ar = ActionResponse(True, False, response.status_code, None, None, None)
    if response.status_code != 200:
        print('[ERROR] Server error. Status code -> ' + response.status_code)
    else:
        data = response.json()
        ar.serverError = False
        ar.isSuccessful = data["isSuccessful"]
        ar.message = data["message"]
        ar.fullName = data["fullName"]
        ar.messageCode = data["messageCode"]
    return ar

def add_person_to_external_system(firstName, lastName, serverUrl, username, password):
    response = requests.post(url=serverUrl + '/api/personnel',
                             json={'firstName': firstName, 'lastName': lastName},
                             headers={'Content-Type': 'application/json'},
                             auth=HTTPBasicAuth(username, password)
                             )
    if response.status_code != 201:
        print('[ERROR] Server error. Status code -> ' + response.status_code)
        print('[ERROR] Person has not been added to external database.')
        return 0
    else:
        print('[INFO] Person added to external server database.')
        return int(response.json()["id"])
