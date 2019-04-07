import socket,time
UDP_IP = "10.0.0.239"
UDP_PORT = 5007
MESSAGE = "Some data"

print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)
print(MESSAGE)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
while True:
    x = raw_input("Message to send:")
    MESSAGE = x
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    time.sleep(5)
