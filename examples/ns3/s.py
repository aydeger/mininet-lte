import socket
import threading
import sys
import time
from Crypto.Cipher import AES

Packet_transmission_time = 0.001	# 0.00001
BUFFER_SIZE = 512

bind_ip = str(sys.argv[1])
bind_port = int(str(sys.argv[2]))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(5)

print "[*] Listening on %s:%d" % (bind_ip, bind_port)

start = time.time()
print (start*1000)
end = time.time()
f = open('workfile' + str(start) + '.txt', 'w+')
def handle_client(client_socket, fileName):
	counter = 0
	#f = open(bind_ip + "from" + fileName + "--" + str(time.time()) + '.txt', 'a')
	while True:	 
		counter = counter + 1
	#	client_socket.send("ACK!")
		start = time.time()
		#print start
		#request = client_socket.recv(1024)
#		print "[*] Received: %s" % request

		request = client_socket.recv(BUFFER_SIZE)
		if not request: break
	#	print "received data:", request
		if request == "STOP":
			break
	#	client_socket.send(request)s
		#print end
		end = time.time()
		endSplitted = str((1000000*end)%10000000000).split(".")
	#	sentTime = str(request).split(":")
		timeDiff1 = int(endSplitted[0])
		strSentTime = ""
	#	print "senttime" + sentTime[1]
		intStarted = False
		counterSTR = 0
		for i, c in enumerate(request):
	#		print i, c
			if counterSTR == 10:
				break
			if int(c) != 0:
				intStarted = True
				strSentTime = strSentTime + c
				counterSTR = counterSTR +1
			elif intStarted == True:
				strSentTime = strSentTime + c
				counterSTR = counterSTR +1
		if strSentTime != "":
			timeDiff2 = int(strSentTime)
		else:
			timeDiff2 = 0
		
		if timeDiff2 == 0:
			continue
		#print "timedif2:" + str(timeDiff2)
		#f.write(str(counter) + " " + str(request) + ": currenttime:" + str(end) + " " + str(1000000 * (end - start - Packet_transmission_time)) + "\n")
		#f.write(str(counter) + " currenttime:" + str(end*1000) + " " + str(1000000 * (end - start - Packet_transmission_time)) + "\n")
		#f.write(str(request) + ": " + str(endSplitted[0]) + "\n")	#written in microsec
		f.write(str(counter) + ": timeSent: " + str(timeDiff2) +  ": currentTime: " + str(endSplitted[0]) + " timeDiff:" + str(timeDiff1 - timeDiff2) + "\n")
		#print request
	#	print end
	#	print (float(end) - float(request))
	print "end"
	#print counter
	#f.write(counter)
	#f.close()
	time.sleep(1)
	server.close()
	f.close()
	client.close()
	sys.exit(0)

while True:
	client, addr = server.accept()
	print "[*] Accepted connection from: %s:%d" % (addr[0], addr[1])
	handle_client(client, addr[0])
	#client_handler = threading.Thread(target = handle_client, args = (client, addr[0],))
	#client_handler.start()

server.close()
client.close()
f.close()
