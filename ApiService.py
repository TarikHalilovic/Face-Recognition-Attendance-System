import requests
from Model.ActionResponse import ActionResponse

class ApiService:
    def __init__(self, server, username, password):
        self.server = server
        self.username = username
        self.password = password
        self.get_token()
        

    def post_action(self, userId, buttonId):
        ar = ActionResponse(True, False, 0, None, None, None)
        try:
            response = requests.post(
                url=f'{self.server}/api/attendance/insert',
                json={'personnelId': userId, 'buttonId': buttonId},
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': self.tokenWithBearer
                },
                timeout=3.5
            )
            # serverError, isSuccessful, statusCode, message, fullName, errorCode
            # ActionResponse(True, False, response.status_code, None, None, None)
            ar.statusCode = response.status_code
            if response.status_code != 200:
                if response.status_code == 403:
                    if self.try_to_refresh_creds():
                        ar = self.post_action(userId, buttonId)
                else:
                    print(f'[ERROR] Server error. Status code -> {response.status_code}')
            else:
                data = response.json()
                ar.serverError = False
                ar.isSuccessful = data["isSuccessful"]
                ar.message = data["message"]
                ar.fullName = data["fullName"]
                ar.messageCode = data["messageCode"]
        except requests.exceptions.Timeout:
            print('[ERROR] Api request timed out.')
        except Exception as err:
            print(f'[ERROR] Error message -> {err}') 
        finally:
            return ar


    def add_person_to_external_system(self, firstName, lastName):
        try:
            response = requests.post(url=f'{self.server}/api/personnel',
                                    json={'firstName': firstName, 'lastName': lastName},
                                    headers={
                                        'Content-Type': 'application/json',
                                        'Authorization': self.tokenWithBearer
                                    },
                                    timeout=3.5
            )
            if response.status_code != 201:
                if response.status_code == 403:
                    if self.try_to_refresh_creds():
                        return self.add_person_to_external_system(firstName, lastName)
                print(f'[ERROR] Server error. Status code -> {response.status_code}')
                print('[ERROR] Person has not been added to external database.')
                return 0
            else:
                print('[INFO] Person added to external server database.')
                return int(response.json()["id"])
        except requests.exceptions.Timeout:
            print('[ERROR] Api request timed out.')
            raise Exception('Request timed out exception')
        except Exception as err:
            print(f'[ERROR] Error message -> {err}')
            raise Exception(err)
   
    
    def get_token(self):
        try:
            response = requests.get(url=f'{self.server}/api/account/login',
                                    json={
                                        'username': self.username,
                                        'passwordHash': self.password
                                    },
                                    timeout=3.5
            )
            if response.status_code == 200:
                self.tokenWithBearer = f'Bearer {response.text}'
                print(f'[INFO] Successfully authenticated with server.')
                return True
            elif response.status_code == 403:
                print(f'[ERROR] Wrong username/password, can not connect to server. Status code -> {response.status_code}')
            else:
                print(f'[ERROR] Server error. Not connected to server. Status code -> {response.status_code}')
            return False
        except requests.exceptions.Timeout:
            print('[ERROR] Server error. Not connected to server. API timeout.')
            return False
        except Exception as err:
            print(f'[ERROR] Error message -> {err}')
            return False
            
            
    def try_to_refresh_creds(self):
        result = self.get_token()
        if not result:
            raise Exception('[ERROR] Can not authenticate with server. Invalid credentials.')
        return True
    
