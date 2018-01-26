from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import uuid
from Cookie import Cookie
from time import time

class S(BaseHTTPRequestHandler):

	sessioncookies = {}  
	sessionMap={}
	sessionidmorsel=None
  
	def _session_cookie(self,forcenew=False):  
		print "headers = "+str(self.headers)
		if (not(self.headers.has_key("Cookie"))):
			forcenew=True
			cookiestring=""
			print "cookie value not found"
		else:
			forcenew=False
			cookiestring=self.headers["Cookie"]
			print "cookie value found"
		print "cookiestring "+cookiestring
		cookiestring = cookiestring
		c = Cookie(cookiestring)
			 
		try:  
			print "forcenew "+str(forcenew)
			print "str(c['session_id'].value) "+str((c.items()))
			if forcenew or self.sessioncookies[str(c['session_id'].value)]-time() > 3600:  
				raise ValueError('new cookie needed')  
		except:  
			print "setting session id..."
			c['session_id']=str(uuid.uuid4().hex)
			print "session id set to "+str(c['session_id'].value)
			self.sessionMap[c['session_id'].value]={}
			 
		for m in c:  
			if m=='session_id':  
				self.sessioncookies[str(c['session_id'].value)] = time()  
				c[m]["httponly"] = True  
				c[m]["max-age"] = 3600  
				c[m]["expires"] = self.date_time_string(time()+3600)  
				self.sessionidmorsel = c[m]  
				print "session cookies: "+str(self.sessioncookies)
				break  



	def do_GET(self):
		global desc
		self._session_cookie()
		print "session id = "+self.sessionidmorsel.value
		smap=self.sessionMap[self.sessionidmorsel.value]
		if (smap.has_key("message")):
			messagg=smap["message"]
		else:
			messagg=""
		smap["message"]="saasd" 
		
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		if not (self.sessionidmorsel is None):  
			self.send_header('Set-Cookie',self.sessionidmorsel.OutputString())  
		self.send_header('Content-type','text/html')
		self.end_headers()
		self.wfile.write("\n\n<html><body><h1>aw man "+desc+" "+messagg+"!</h1></body></html>")

	def do_HEAD(self):
		self._set_headers()
        
	def do_POST(self):
	# Doesn't do anything with posted data
		self._session_cookie()
		self._set_headers(sessionidmorsel)
		self.wfile.write("<html><body><h1>aw post man</h1></body></html>")
        
def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 3:
      desc=argv[2]
      run(port=int(argv[1]))
    elif len(argv) == 2:
      desc="A"
      run(port=int(argv[1]))
    else:
      desc="A"
      run()
