class roommateRequest:
   
    def __init__(self, sender_id, receiver1_id, receiver2_id=None, receiver3_id=None):
        self.sender_id = sender_id
        self.receiver_ids = [r_id for r_id in [receiver1_id, receiver2_id, receiver3_id] if r_id is not None]
        self.responses = {r_id: None for r_id in self.receiver_ids}
        self.accepted = None
        self.request_id = id(self)

    def accept_request(self, r_id):
        self.responses[r_id] = True
        self.updateStatus()

    def reject_request(self, r_id):
        self.responses[r_id] = False
        self.updateStatus()

    def updateStatus(self):
        #checks if everyone has responded
        if all(response == True for response in self.responses.values()):
            self.accepted = True
        elif any(response == False for response in self.responses.values()):
            self.accepted = False
        else:
            self.accepted = None
    
    def getSenderId(self):
        return self.sender_id
    
    def getReceiverIds(self):
        return self.receiver_ids

    def isAccepted(self):
        return self.accepted