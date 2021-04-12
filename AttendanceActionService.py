from LocalDb import LocalDb
from Model.LocalActionResponse import LocalActionResponse

class AttendanceActionService:
    def __init__(self):
        self.db = LocalDb()
    
    def insert_action(self, personnel_id, button_id):
        response = LocalActionResponse()
        if personnel_id is None:
            response.isSuccessful = True
            # response.message = None
            # response.messageCode = None
            return response
        
        