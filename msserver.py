#!/usr/bin/python

import socket 
import signal
import time
import pymysql

import argparse
import json
import pprint
import sys
import urllib
import urllib.error
from urllib.request import urlopen
import oauth2


API_HOST = 'api.yelp.com'
DEFAULT_TERM = 'food'
DEFAULT_LOCATION = 'New York, NY'
SEARCH_LIMIT = 8
SEARCH_PATH = '/v2/search'
BUSINESS_PATH = '/v2/business/'

CONSUMER_KEY = 'sJ0lvOVobPrGJf3KAK66HQ'
CONSUMER_SECRET = 'iEeQSreY1LzdAVcWwIaC4kF7MrI'
TOKEN = 'AY119OXUsggGnJZEIzXet8ODOOoTZ2sL'
TOKEN_SECRET = 'wvkIJFlGr1VbFBaN1vBtFmTgPJM'

server_type = 1

class Server:

	

	def __init__(self,port = 8000):		

		if server_type==0:		
			self.host = '128.122.238.51'			
			self.databaseHost = 'websys3.stern.nyu.edu'
			self.user = 'websysF15GB7'
			self.password = 'websysF15GB7!!'
			self.database = "websysF15GB7"

		else:
			self.host = '127.0.0.1'
			self.databaseHost ='localhost'		
			self.user = 'root'
			self.password = '111314'
			self.database = 'mobile'

		self.port = port
		self.databasePort = 3306
		self.www_dir = 'www'

	def activate_server(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			print ("Launching HTTP server on ", self.host, ":", self.port)
			self.socket.bind((self.host, self.port))

		except Exception as e:
			print("Warning: Could not acquite port:", self.port, "\n")
			print("I will try a higher port")
			user_port = self.port
			self.port = 7007

			try:
				print("Launching HTTP server on ", self.host, ":", self.port)
				self.socket.bind((self.host, self.port))

			except Exception as e:
				print("ERROR: Failed to acquire sockets for ports ", user_port, " and 7007")
				print("Try running the Server in a privileged user mode.")
				self.shutdown()
				import sys
				sys.exit(1)
		print ("Server successfully acquired the socket with port:", self.port)
		print ("Press Ctrl+C to shut down the server and exit.")
		self._wait_for_connections()

	def shutdown(self):
		try:
			print("Shutting down the server")
			s.socket.shutdown(socket.SHUT_RDWR)

		except Exception as e:
			print("Warning: could not shut down the socket. Maybe it was already closed?", e)

	def _gen_headers(self, code):
		h = ''
		if (code == 200):
			h = 'HTTP/1.1 200 OK\n'
		elif(code == 404):
			h = 'HTTP/1.1 404 Not Found\n'

		current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
		h += 'Date: ' + current_date + '\n'
		h += 'Server: TaoDong-WebSite-Server\n'
		h += 'Connection: close\n\n'
		return h

	def _wait_for_connections(self):
		while True:
			print ("Awaiting New connection")
			self.socket.listen(20)
			conn, addr = self.socket.accept()

			print ("Got connection from: ", addr)

			data = conn.recv(1024)
			string = bytes.decode(data)

			request_method = string.split(' ')[0]
			print("Method: ", request_method)
			print("Request body: ", string)

			if (request_method == 'GET') | (request_method == 'HEAD'):
				file_requested = string.split(' ')
				file_requested = file_requested[1][1:]
				file_requested = file_requested.split('?')[0]

				if(file_requested == ''):
					file_requested = 'home.html'
				try:
					file_handler = open(file_requested,'rb')
					if (request_method == 'GET'):
						response_content = file_handler.read()
					file_handler.close()
					response_headers = self._gen_headers( 200)

				except Exception as e:
					print("Warning, file not found. Serving response code 404\n", e)
					response_headers = self._gen_headers( 404)
					if (request_method == 'GET'):
						response_content = b"<html><body><p>Error 404: File not found</p><p>TaoDong-WebSite-Server</p></body></html>"

				server_response = response_headers.encode()

				if (request_method == 'GET'):
					server_response += response_content

				conn.send(server_response)
				print ("File "+file_requested+" sent successfully!")
				print ("Closing connection with client")
				conn.close()

			elif (request_method == 'SIGNUP'):
				file_requested = string.split(' ')
				file_requested = file_requested[1][1:]
				username = file_requested.split('?')[0]
				password = file_requested.split('?')[1]

				if username=="" or password=="":
					print("none none!")
					message = bytes('{"status":"none"}','UTF-8')
				else:
					conndb = pymysql.connect(host=self.databaseHost, port=self.databasePort, user=self.user, passwd=self.password, db=self.database)
					cur = conndb.cursor()
					cur.execute("select * from client where id=%s", (username))
					data = cur.fetchall()
					print("data: ", data)

					if len(data)==0:
						cur.execute("insert into client (id, password) values(%s,%s)",(username,password))                    
						message = bytes('{"status":"success","userName":"' + username +'"}','UTF-8')

					else:
						message = bytes('{"status":"failure"}','UTF-8')

					cur.close()
					conndb.commit()
					conndb.close()
				response_headers = self._gen_headers( 200)
				server_response = response_headers.encode()
				server_response += message
				conn.send(server_response)
				print ("Closing connection with client")
				conn.close()

			elif (request_method == 'LOGIN'):
				file_requested = string.split(' ')
				file_requested = file_requested[1][1:]
				username = file_requested.split('?')[0]
				password = file_requested.split('?')[1]

				if username=="" or password=="":
					print("none none!")
					message = bytes('{"status":"failure"}','UTF-8')

				else:
					conndb = pymysql.connect(host=self.databaseHost, port=self.databasePort, user=self.user, passwd=self.password, db=self.database)
					cur = conndb.cursor()
					cur.execute("select distinct * from client where id=%s and password=%s", (username,password))
					data = cur.fetchall()
					print("data: ", data)

					if (len(data)==0) :                   
						message = bytes('{"status":"failure"}','UTF-8')

					elif (data[0][1]!=password) :                   
						message = bytes('{"status":"failure"}','UTF-8')

					else:					
						message = bytes('{"status":"success","userName":"' + username +'"}','UTF-8')

					cur.close()
					conndb.commit()
					conndb.close()
				response_headers = self._gen_headers( 200)
				server_response = response_headers.encode()
				server_response += message
				conn.send(server_response)
				print ("Closing connection with client")
				conn.close()

			elif request_method == 'HISTORY':
				conndb = pymysql.connect(host=self.databaseHost, port=self.databasePort, user=self.user, passwd=self.password, db=self.database)
				cur = conndb.cursor()
				cur.execute("select distinct location, item from incident where id=%s", (username))
				data = cur.fetchall()
				cur.close()
				conndb.commit()
				conndb.close()
				length = len(data)
				string = ""
				if length>0:
					string += "["
					for i in range(0,length):
						string += '{"location":"'+data[i][0]+'", "item":"'+data[i][1]+'"},';
						if i==length-1:
							string = string[:-1]
							string += "]"
				message = bytes(string, 'UTF-8')
				response_headers = self._gen_headers( 200)
				server_response = response_headers.encode()
				server_response += message
				conn.send(server_response)
				print("Closing connection with client")
				conn.close()

				print(message)


			elif (request_method == 'SEARCH'):
				file_requested = string.split(' ')
				file_requested = file_requested[1][1:]
				location = file_requested.split('?')[0]
				item = file_requested.split('?')[1]


				if username=="" or password=="":
					print("none none!")
					string = '{"name":"failure"}'

				else:
					parser = argparse.ArgumentParser()

					parser.add_argument('-q', '--term', dest='term', default=item, type=str, help='Search term (default: %(default)s)')

					parser.add_argument('-l', '--location', dest='location', default=location, type=str, help='Search location (default: %(default)s)')

					input_values = parser.parse_args()

					result = query_api(input_values.term,input_values.location)

					pprint.pprint(result)

					if result!=None and result!=[]:
						conndb = pymysql.connect(host=self.databaseHost, port=self.databasePort, user=self.user, passwd=self.password, db=self.database)
						cur = conndb.cursor()
						cur.execute("insert incident values(%s,%s,%s,curdate())",(username,location,item))
						cur.close()
						conndb.commit()
						conndb.close()
						string = '['
						for i in range(len(result)):
							categories = result[i].get('categories')
							if categories == None:
								string += '{"categories":" "'
							else:
								length = len(categories)
								string += '{"categories":"'
								for j in range(length):
									string += categories[j][0] + ", "
									if j==length-1:
										string = string[:-2]
										string += '"'
							location = result[i].get('location')

							listAddress = location.get('address')
							if len(listAddress)>0:
								address = listAddress[0]
							else:
								address = ""

							phonenumber = result[i].get('display_phone')
							if phonenumber!=None:
								if len(phonenumber)>0:
									phonenumber = phonenumber
								else:
									phonenumber = ""
							else:
								phonenumber = ""
							coordinate = location.get('coordinate')
							latitude = coordinate.get('latitude')
							longitude = coordinate.get('longitude')
							name = result[i].get('name')
							latitude = str(latitude)
							longitude = str(longitude)
							name = str(name)
							string += ',"name":"' + name +'", "address":"' + address + '", "phonenumber":"' + phonenumber + '", "latitude":"'+ latitude + '", "longitude":"' + longitude + '"},'
							if(i==len(result)-1):
								string = string[:-1]
								string += ']'
					else:
						string = '{"name":"failure"}'

				response_headers = self._gen_headers( 200)
				server_response = response_headers.encode()
				message = bytes(string, 'UTF-8')
				server_response += message
				conn.send(server_response)
				print (string)
				print ("Closing connection with client")
				conn.close()


				#pprint.pprint(result[0])
				#pprint.pprint(result[0].get('location'))
				#pprint.pprint(result[0].get('name'))

			else:
				print("Unknown HTTP request method: ", request_method)

def query_api(item, location):
	response = search(item, location)

	businesses = response.get('businesses')


	# if not businesses:
	# 	#print (u'No businesses for {0} in {1} found.'.format(item, location))
	# 	return 

	#business_id = businesses[0]['id']


	#print (u'{0} businesses found, querying business info for the top result "{1}" ...'.format(len(businesses), business_id))
	#response = get_business(business_id)

	#print(u'Result for business "{0}" found:'.format(business_id))


	return businesses;

def search(item, location):
	url_params = {
		'term': item.replace('%20', '+'),
		'location': location.replace('%20', '+'),
		'limit': SEARCH_LIMIT
	}
	return request(API_HOST, SEARCH_PATH, url_params=url_params)

def get_business(business_id):
	business_path = BUSINESS_PATH +business_id
	return request(API_HOST, business_path)

def request(host, path, url_params=None):
	url_params = url_params or {}
	url = 'http://{0}{1}?'.format(host,urllib.parse.quote(path.encode('utf8')))
	consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
	oauth_request = oauth2.Request(
		method="GET", url=url, parameters=url_params)

	oauth_request.update(
		{
			'oauth_nonce': oauth2.generate_nonce(),
			'oauth_timestamp': oauth2.generate_timestamp(),
			'oauth_token': TOKEN,
			'oauth_consumer_key': CONSUMER_KEY
		}
	)
	token = oauth2.Token(TOKEN, TOKEN_SECRET)
	oauth_request.sign_request(
		oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
	signed_url = oauth_request.to_url()
	try:
		conn = urlopen(signed_url,None)
	except urllib.error.HTTPError as error:
		response = json.loads('{"status":"failure"}')
		return response
	try:
		response = json.loads(conn.read().decode('utf-8'))
	finally:
		conn.close()
	return response

def graceful_shutdown(sig, dummy):
	s.shutdown()
	import sys
	sys.exit()

signal.signal(signal.SIGINT, graceful_shutdown)

print ("Starting web server")
s = Server()
s.activate_server()


