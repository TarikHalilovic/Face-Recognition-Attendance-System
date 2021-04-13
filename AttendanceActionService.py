from LocalDb import LocalDb
from Model.LocalActionResponse import LocalActionResponse
from time import time as getCurrentTime
from Model.EventEnum import Event
from Model.ActionDBEnum import ActionDB

class AttendanceActionService:
    def __init__(self):
        self.db = LocalDb()
    
    def insert_action(self, personnel_id, button_id, name = None, time = getCurrentTime()):
        response = LocalActionResponse()
        if personnel_id is None:
            response.isSuccessful = True
            # response.message = None
            # response.messageCode = None
            return response
        
        startIndex = 0
        hitBreak = False
        
        if button_id <= 1:
            last_entries = self.db.get_last_n_actions(1, personnel_id)
            if len(last_entries) == 0 or last_entries[0][ActionDB.EVENT.value] == Event.WORK_END.value:
                self.db.add_action(Event.WORK_START.value, personnel_id, getCurrentTime())
                response.message = f"Welcome {name}."
                response.isSuccessful = True
                response.messageCode = 4
            else:
                response.message = f"{name}, you have already started your shift."
                response.messageCode = 1
        elif button_id == 2:
            last_entries = self.db.get_last_n_actions(8, personnel_id)
            if len(last_entries) == 0:
                response.message = f"{name}, you haven't started your shift yet."
                response.messageCode = 2
            else:
                while(True):
                    for item in last_entries:
                        if item[ActionDB.EVENT.value] == Event.BREAK_START.value:
                            self.db.add_action(Event.BREAK_END.value, personnel_id, getCurrentTime())
                            response.message = f"Welcome back {name}."
                            response.messageCode = 8
                            response.isSuccessful = True
                            hitBreak = True
                            break
                        elif item[ActionDB.EVENT.value] == Event.WORK_START.value or item[ActionDB.EVENT.value] == Event.BREAK_END.value:
                            self.db.add_action(Event.BREAK_START.value, personnel_id, getCurrentTime())
                            response.message = f"Have fun {name}."
                            response.messageCode = 5
                            response.isSuccessful = True
                            hitBreak = True
                            break
                        elif item[ActionDB.EVENT.value] == Event.WORK_END.value:
                            response.message = f"{name}, you haven't started your shift yet."
                            response.messageCode = 2
                            hitBreak = True
                            break
                    if hitBreak:
                        break
                    startIndex+=8
                    last_entries = self.db.get_last_n_actions(8, personnel_id, startIndex)
        elif button_id == 3:
            last_entries = self.db.get_last_n_actions(8, personnel_id)
            if len(last_entries) == 0:
                response.message = f"{name}, you haven't started your shift yet."
                response.messageCode = 2
            else:
                while(True):
                    for item in last_entries:
                        if item[ActionDB.EVENT.value] == Event.OFFICIAL_START.value:
                            self.db.add_action(Event.OFFICIAL_END.value, personnel_id, getCurrentTime())
                            response.message = f"Welcome back {name}."
                            response.messageCode = 8
                            response.isSuccessful = True
                            hitBreak = True
                            break
                        elif item[ActionDB.EVENT.value] == Event.WORK_START.value or item[ActionDB.EVENT.value] == Event.OFFICIAL_END.value:
                            self.db.add_action(Event.OFFICIAL_START.value, personnel_id, getCurrentTime())
                            response.message = f"Stay safe {name}."
                            response.messageCode = 6
                            response.isSuccessful = True
                            hitBreak = True
                            break
                        elif item[ActionDB.EVENT.value] == Event.WORK_END.value:
                            response.message = f"{name}, you haven't started your shift yet."
                            response.messageCode = 2
                            hitBreak = True
                            break
                    if hitBreak: 
                        break
                    startIndex+=8
                    last_entries = self.db.get_last_n_actions(8, personnel_id, startIndex)
        elif button_id >= 4:
            last_entries = self.db.get_last_n_actions(8, personnel_id)
            if len(last_entries) == 0:
                response.message = f"{name}, you haven't started your shift yet."
                response.messageCode = 2
            else:
                hasOpenBreak = False
                hasOpenOfficial = False
                while(True):
                    for item in last_entries:
                        if item[ActionDB.EVENT.value] == Event.OFFICIAL_START.value or item[ActionDB.EVENT.value] == Event.OFFICIAL_END.value:
                            hasOpenOfficial = not hasOpenOfficial
                        elif item[ActionDB.EVENT.value] == Event.BREAK_START.value or item[ActionDB.EVENT.value] == Event.BREAK_END.value:
                            hasOpenBreak = not hasOpenBreak
                        elif item[ActionDB.EVENT.value] == Event.WORK_START.value:
                            if not hasOpenBreak and not hasOpenOfficial:
                                self.db.add_action(Event.WORK_END.value, personnel_id, getCurrentTime())
                                response.message = f"Goodbye and see you soon {name}."
                                response.messageCode = 7
                                response.isSuccessful = True
                            hitBreak = True
                            break
                        elif item[ActionDB.EVENT.value] == Event.WORK_END.value:
                            response.messageCode = 2
                            response.message = f"{name}, you haven't started your shift yet."
                            hitBreak = True
                            break
                    if hitBreak:
                        if hasOpenBreak:
                            response.messageCode = 3
                            response.message = f"{name}, you haven't closed your Break."
                        elif hasOpenOfficial:
                            response.messageCode = 9
                            response.message = f"{name}, you haven't closed your Official Absence."
                        break
                    else:
                        startIndex+=8
                        last_entries
                        last_entries = self.db.get_last_n_actions(8, personnel_id, startIndex)
        return response