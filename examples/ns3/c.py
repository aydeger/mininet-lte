import socket
import sys
import time

EXPERIMENT_TIME = 60 	#SECONDS
Packet_transmission_time = 0.04		#seconds 0.00001
BUFFER_SIZE = 512

target_host = str(sys.argv[1])
target_port = int(str(sys.argv[2]))
MESSAGE = "ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZ123456789012" 
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((target_host, target_port))

experiment_start = time.time()
#print (experiment_start*1000)
#f = open('workfile' + str(experiment_start) + '.txt', 'w+')
start = time.time()
#print (experiment_start*1000)
#f = open('workfile' + str(experiment_start) + '.txt', 'w+')
print 'packets dst:' + target_host
counter = 0
while ((float(start - experiment_start)) < EXPERIMENT_TIME):	
	#response = client.recv(4096)
	counter = counter + 1
#	end = time.time()
#	fileWrite = time.time()
#	f.write(str(end - start) + "\n")
#	print (time.time() - fileWrite)
#	print (end - start)
#	print response
#	print (start - experiment_start)
	
#	start = time.time()
#	client.send(str(start))

	start = time.time()
#	print "start:" + str(start)
	startSplitted = str((1000000*start)%10000000000).split(".")
#	print "startSpltteD:" + startSplitted[0]
	#intStartSplitted = float(startSplitted[0])
	sentTime = startSplitted[0].zfill(512)
#	print "before:" + sentTime
#	strSentTime = ""
#	intStarted = False
#	for i, c in enumerate(sentTime):
#		print i, c
#		if int(c) != 0:
#			intStarted = True
#			strSentTime = strSentTime + c
#		elif intStarted == True:
#			strSentTime = strSentTime + c
		
#	print "after:" + strSentTime
	#client.send(str(counter).zfill(7) + ". Start:" + str(intStartSplitted).zfill(16))
	#client.send(startSplitted[0].zfill(16) + ",")
	client.send(sentTime)
	#print start
	#time.sleep(3)
	#data = client.recv(BUFFER_SIZE)
	#print data
	#time.sleep(3)
	#end = time.time()
	#print (end - start)
	#time.sleep(3)
	#f.write(str(start) + ": " + str(1000000 * (end - start)/2) + "\n")

	time.sleep( Packet_transmission_time )
#	print (start)

print "Sending STOP!"
client.send("STOP")
time.sleep(1)
#f.close()
client.close()
sys.exit(0)

#((float(start - experiment_start)) < 1.0)
