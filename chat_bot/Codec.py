from enum import Enum 

class m_type(Enum):
    REGISTER = 1
    APPROVED = 2
    FAILED = 3 
    DISCONNECT = 4
    NEWUSER = 5
    BROADCAST = 6
    IND = 7
    
class message: 
    def __init__(self, type, data):
        self.type = type
        self.data = data

class codec:
    def encode (type, data) -> str:
        msg = message(type, data)
        return f"{msg.type.value} {msg.data}"

    def decode(str_data) -> message:
        type_value, data = str_data.split(' ', 1)
        msg_type = m_type(int(type_value))
        return message(msg_type, data)
