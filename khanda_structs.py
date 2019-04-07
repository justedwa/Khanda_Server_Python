#System Imports
import json

class khanda_message(object):
    def __init__(self,type,payload,recipient,timestamp):
        """Initializes the khanda_message object
        Args:
            type : string, type of packet (CMD,HEARTBEAT,EVENT,LED,etc.)
            payload : string, packet data
            recipient : string, destination of packet
            timestamp : string, timestamp appended by sender
        Returns:
            None
        Raises:
            None
        """
        self.type = type
        self.payload = payload
        self.recipient = recipient
        self.timestamp = timestamp
    def __json__(self):
        """object JSON serialization function
        Args:
            None
        Returns:
            JSON serialized Python Object
        Raises:
            None
        """
        return {"type" : self.type,"payload" : self.payload,"recipient" : self.recipient,
                "timestamp" : self.timestamp}


class khanda_TxWrapper:
    def __init__(self,recipient,JSONMSG):
        self.recipient = recipient
        self.data = JSONMSG

class JSONEncoder(json.JSONEncoder):
    """Serializes object into JSON format, if object has __json__ function invoke that function for encoding
    Args:
        None
    Returns:
        None
    Raises:
        Error if object does not follow expected JSON formatting
    """
    def default(self,obj):
        """Serializes object into JSON format, if object has __json__ function invoke that function for encoding
        Args:
            None
        Returns:
            None
        Raises:
            Error if object does not follow expected JSON formatting
        """
        if hasattr(obj,'__json__'):
            return obj.__json__()
        return json.JSONEncoder.default(self,obj)

def KhandaMSGDecoder(obj):
    """JSON deserializer function, converts raw JSON into khanda_message object
    Args:
        None
    Returns:
        None
    Raises:
        Error if data is not in proper JSON format
    """
    return khanda_message(obj['type'],obj['payload'],
                         obj['recipient'],obj['timestamp'])
