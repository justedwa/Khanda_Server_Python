import khandaServer,khanda_structs,time

testServer = khandaServer.khandaServer()
testServer.connect()
testServer.set_MSGLEN(512)
testServer.startWorkers()
while True:
    continue
