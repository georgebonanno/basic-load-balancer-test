import select
import socket
import sys
import Queue

PORT=8005
HOST=''

multEndpoints=[('10.16.0.157',8006),('10.16.0.157',8007)]

def connectToSock(address):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setblocking(0)
	print 'attempting to connect to ',str(address[0]),' ',str(address[1])
	s.connect((address[0], address[1]))
	return s

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
multEndpointsSock=map(connectToSock,multEndpoints)

try:
	server.setblocking(0)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	server.bind((HOST,PORT))
	server.listen(5)

	inputs=[ server ]
	outputs= []
	responder=multEndpointsSock[0]
	connectors=[]
	dataOut=None
	response=None
	notifiers=0

	while inputs:
		readable, writable, exceptional = select.select(inputs, outputs, inputs)

		for s in readable:

			if s is server:
				# A "readable" server socket is ready to accept a connection
				connection, client_address = s.accept()
				print >>sys.stderr, 'new connection from', client_address
				connection.setblocking(0)
				inputs.append(connection)

				if (connection.getpeername() not in multEndpoints):
					connectors.append(connection)

				# Give the connection a queue for data we want to send
			else:
				print "to read ..." +str(s.getpeername()) + " " + str(multEndpoints)
				data = s.recv(1024)
				print "data = "+data
				if data:
					if responder == s:
						response=data
						outputs=outputs+connectors
					elif not(s.getpeername() in multEndpoints):
						# A readable client socket has data
						print 'received "%s" from %s' % (data, s.getpeername())
						dataOut=data
						print "set dataout to "+dataOut
						for m in multEndpointsSock:
							if m not in outputs:
								outputs.append(m)
						notifiers=len(multEndpointsSock)
						# Add output channel for response
					else:
						print 'response from remotes: %s -> %s' % (data, s.getpeername())
						response=data

					if s not in outputs:
						outputs.append(s)  
					inputs.remove(s)
				else:
					# Interpret empty result as closed connection
					print >>sys.stderr, 'closing', client_address, 'after reading no data'
					# Stop listening for input on the connection
					if s in outputs:
						outputs.remove(s)
					inputs.remove(s)
					s.close()

		# Handle outputs
		for s in writable:
			print "to write "+str(s.getpeername())
			print str(s.getpeername()) + " " + str(multEndpoints)+" "+str(dataOut)
			next_msg=dataOut
			if s.getpeername() in multEndpoints and dataOut != None:
				print >>sys.stderr, 'sending "%s" to %s' % (next_msg, s.getpeername())
				s.send(dataOut)
				notifiers=notifiers-1;

			elif s.getpeername() not in multEndpoints and response != None:
				s.send(response)
				response=None

			if s not in inputs:
				inputs.append(s)
			outputs.remove(s)
		if (notifiers <= 0):
			dataOut=None
		

		# Handle "exceptional conditions"
		for s in exceptional:
			print >>sys.stderr, 'handling exceptional condition for', s.getpeername()
			# Stop listening for input on the connection
			inputs.remove(s)
			if s in outputs:
				outputs.remove(s)
			s.close()


finally:
	print "closing connection"
	server.close()
	for i in multEndpointsSock:
		print "closing %s %s" % (i.getpeername())
		i.close()
