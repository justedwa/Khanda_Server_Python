#System Imports
import socket
import time
import threading
import select
import json
import struct
import re
from Queue import *
#3rd Party Imports
import serial
#Local Imports
from khanda_structs import *

class khandaServer:
    """
    This is a class for creating a khanda server to service data collection system

    Attributes:
        MSGLEN (int): packet message size in bytes
        RxQueue (Queue): Queue containing decoded packets from serial and UDP port
        TxQueue (Queue): Queue containing serialized packets to be sent
        CmdQueue (Queue): Queue containing khanda_message objects to be parsed
        threads (thread list): list of current running threads
        serialPorts (serial list): list of currently opened serial ports
        globalTimeWatchdog (int): timer watchdog for device communications
        port (int): UDP port number
        host (string): UDP port address
        sock (socket): UDP socket object
        logfile (FILE): Output logfile
    Methods:
        __init__: Creates khanda_server object and Initializes Attributes
        serial_start: creates serial port connection
        connect: binds UDP socket
        startWorkers: starts all worker functions in seperate threads
        stopWorkers: stops all currently running worker threads
        set_MSGLEN: set packet data size
        QueueCommand: Place command in TxQueue
        SerialRxWorker: Worker thread for retrieving data from serial ports, placed in RxQueue
        RxWorker: Worker thread for retrieving data from the UDP socket, placed in RxQueue
        TxWorker: Worker thread for transmitting data contained in the TxQueue
        CMDWorker: Worker thread for parsing data from the RxQueue
    """
    def __init__(self,MCAST_GRP=None,MCAST_PORT=None,sock=None):
        """Intialize the KhandaServer Object.
        Args:
            MCAST_GRP: Slave device multicast group
            MCAST_PORT: Port for server to listen on
            sock: socket object to use, default value generates socket object
            SerialPT: Optional serial port to listen on for slave devices communicating over serial
        """
        self.MSGLEN = 512
        self.RxQueue =  Queue()
        self.TxQueue =  Queue()
        self.CmdQueue = Queue()
        self.threads = []
        self.serialPorts = []
        self.globalTimeWatchdog = 0
        if MCAST_PORT is None:
            self.port = 5007
        else:
            self.port = MCAST_PORT
        if MCAST_GRP is None:
            self.host = "224.1.1.1"
        else:
            self.host = MCAST_GRP
        if sock is None:
            self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP)
            self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)




    def serial_start(self,SERIAL_PORT,BAUD=9600):
        """Initializes serial port and starts the serial recieve thread
        Args:
            SERIAL_PORT: string, address of the serial port (COMx /dev/ttyUSBx)
            BAUD: int, baud rate of the attached device, default: 9600
        Returns:
            None
        Raises:
            Error if serial parameters are invalid
        """
        try:
            port = serial.Serial(SERIAL_PORT,BAUD,timeout=0)
            self.serialPorts.append(port)
        except:
            print("Invalid Serial port parameters")

    def connect(self):
        """Binds Khanda Server to UDP socket and listens
        Args:
            Self
        Returns:
            None
        Raises:
            Network Error if connection fails
        """
        try:
            self.sock.bind(('',self.port))
            mreq = struct.pack("4sl", socket.inet_aton(self.host), socket.INADDR_ANY)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        except:
            print("Error Binding Socket!")


    def startWorkers(self):
        """Starts worker threads (Network Transmit,Network Receive,Command Worker,Serial Recieve)
        Args:
            Self
        Returns:
            None
        Raises:
            System Error if threads cannot be created
        """
        try:
            t = threading.Thread(target=self.RxWorker)
            self.threads.append(t)
            t.start()
            t = threading.Thread(target=self.TxWorker)
            self.threads.append(t)
            t.start()
            t = threading.Thread(target=self.CMDWorker)
            self.threads.append(t)
            t.start()
            if len(self.serialPorts):
                t = threading.Thread(target=self.SerialRxWorker)
                self.threads.append(t)
                t.start()
            else:
                continue
        except:
            print("Unable to start worker threads!")


    def stopWorkers(self):
        """Stops all running threads associated with the server
        Args:
            Self
        Returns:
            None
        Raises:
            System Error if threads cannot be stopped
            System Error if logfile cannot be closed
        """
        try:
            for worker in self.threads:
                worker.stop()
            for port in self.serialPorts:
                port.close()
        except:
            print("Unable to stop working threads!")
        try:
            self.logfile.close()
        except:
            print("Unable to close logfile!")

    def set_MSGLEN(self,length):
        """Sets message length for khanda packets
        Args:
            length: size of packets in bytes
        Returns:
            None
        Raises:
            None
        """
        self.MSGLEN = length

    def QueueCommand(self,CMD):
        """Place command in the Tx Queue of the khanda server
        Args:
            CMD: string, Command packet payload
        Returns:
            0: On successful command queue
            -1: On failure
        Raises:
            Error if command is unable to be processed
        """
        try:
            newCommand = khanda_message("CMD",CMD,"224.1.1.1","1") #Placeholder Timestamp
            newCommand_wrapper = khanda_TxWrapper("224.1.1.1",json.dumps(khanda_Resp,cls=JSONEncoder))
            self.TxQueue.put(newCommand_wrapper)
            return 0
        except:
            print("Unable to Process Command")
            return -1

    def SerialRxWorker(self):
        """Worker thread function that retrieves data from serial devices,places decoded JSON object into RxQueue
        Args:
            None
        Returns:
            None
        Raises:
            Error if serial data is not in proper JSON format
        """
        while True:
            for port in self.serialPorts:
                if port.in_waiting >= 128:
                    try:
                        raw_khanda_packet = port.readline()
                        re.sub(r"\s+$","",raw_khanda_packet)
                        raw_khanda_packet = raw_khanda_packet.replace('\t','')
                        raw_khanda_packet = raw_khanda_packet.replace('\r','')
                        raw_khanda_packet = raw_khanda_packet.replace('\n','')
                        raw_khanda_packet = raw_khanda_packet.replace('\0','')
                        raw_khanda_packet = raw_khanda_packet.replace('\'','\"')
                        if raw_khanda_packet:
                            print(str(raw_khanda_packet))
                        try:
                            khanda_packet = json.loads(raw_khanda_packet,object_hook=KhandaMSGDecoder,strict=False)
                            if khanda_packet.recipient == "224.1.1.1": # and khanda_packet.timestamp == 1:
                                self.RxQueue.put(khanda_packet)
                            else:
                                del khanda_packet
                        except:
                            print("Invalid Packet Structure")
                    except:
                        return

    def RxWorker(self):
        """Worker thread function that retrieves data from UDP port, places decoded JSON object into RxQueue
        Args:
            None
        Returns:
            None
        Raises:
            Error if Network data is not in proper JSON format
        """
        while True:
            readable = [self.sock]
            read,write,exception = select.select(readable,[],[],0)
            for readable_socket in read:
                raw_khanda_packet = readable_socket.recv(512)
                re.sub(r"\s+$","",raw_khanda_packet)
                raw_khanda_packet = raw_khanda_packet.replace('\t','')
                raw_khanda_packet = raw_khanda_packet.replace('\r','')
                raw_khanda_packet = raw_khanda_packet.replace('\n','')
                raw_khanda_packet = raw_khanda_packet.replace('\0','')
                print(raw_khanda_packet)
                try:
                    khanda_packet = json.loads(raw_khanda_packet,object_hook=KhandaMSGDecoder,strict=False)
                    if khanda_packet.recipient == "224.1.1.1": # and khanda_packet.timestamp == 1:
                        self.RxQueue.put(khanda_packet)
                    else:
                        del khanda_packet
                except:
                    print("Invalid Packet Structure")
            continue

    def TxWorker(self):
        """Worker thread function that retrieves data from the Tx message queue and sends the packet via a UDP socket
        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        while True:
            writeable = [self.sock]
            read,write,exception = select.select([],writeable,[],0)
            for writeable_socket in write:
                if self.TxQueue.empty() is False:
                    Txpacket = self.TxQueue.get()
                    self.sock.sendto(Txpacket.data,(Txpacket.recipient,self.port))
                    self.TxQueue.task_done()
        #Add serial tranmission here!
    def CMDWorker(self):
        """Worker thread function that retrieves data from the Rx message queue and performs specified operation
        Args:
            Parser : function, custom parser function that decodes khanda_packet and performs operations based on content
        Returns:
            data : results of custom parser function
        Raises:
            None
        """
        while True:
            if self.RxQueue.empty() is False:
                RxPacket = self.RxQueue.get()
                if RxPacket.type == "EVENT":
                    """Place Event in Event file/queue"""
                    print("Event Detected")
                    logfile = open("logfile.txt","a")
                    FileWrite_Buff = str(RxPacket.type) + "," + str(RxPacket.payload) + "," + str(RxPacket.timestamp) + "\r\n"
                    logfile.write(str(FileWrite_Buff))
                    logfile.close()
                if RxPacket.type == "LED":
                    if RxPacket.payload == "RED" or RxPacket.payload == "REDOFF":
                        khanda_Resp = khanda_message("CMD","LED+RED","224.1.1.1",str(time.time()))
                        khanda_resp_wrapper = khanda_TxWrapper("10.0.0.120",json.dumps(khanda_Resp,cls=JSONEncoder))
                    elif RxPacket.payload == "GREEN" or RxPacket.payload == "GREENOFF":
                        khanda_Resp = khanda_message("CMD","LED+GREEN","224.1.1.1",str(time.time()))
                        khanda_resp_wrapper = khanda_TxWrapper("10.0.0.120",json.dumps(khanda_Resp,cls=JSONEncoder))
                    elif RxPacket.payload == "BLUE" or RxPacket.payload == "BLUEOFF":
                        khanda_Resp = khanda_message("CMD","LED+BLUE","224.1.1.1",str(time.time()))
                        khanda_resp_wrapper = khanda_TxWrapper("10.0.0.120",json.dumps(khanda_Resp,cls=JSONEncoder))
                    self.TxQueue.put(khanda_resp_wrapper)
                    logfile = open("logfile.txt","a")
                    FileWrite_Buff = str(RxPacket.type) + "," + str(RxPacket.payload) + "," + str(RxPacket.timestamp) + "\r\n"
                    logfile.write(str(FileWrite_Buff))
                    logfile.close()
                if RxPacket.type == "HEALTH":
                    if RxPacket.payload == "UNHEALTHY":
                        print("DEVICE ERROR RESTART\n")
                self.RxQueue.task_done()
            else:
                continue
