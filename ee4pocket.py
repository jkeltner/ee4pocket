import logging
import urllib
import urllib2

from urllib2 import urlopen, HTTPError
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db


class PocketUser(db.Model):
	userID = db.StringProperty()
	password = db.StringProperty()


class Execute(webapp.RequestHandler):
	def get(self):
		f = open('apikey', 'r')
		apikey = f.read()
		pocketUsers = db.GqlQuery("SELECT * FROM PocketUser")

		# need to add a limit to this and a reload for extra users

		for pocketUser in pocketUsers:
			try:
				response = urllib2.urlopen("https://readitlaterlist.com/v2/add?username="+pocketUser.userID+"&password="+pocketUser.password+"&apikey="+apikey+"&url=http://evening-edition.com")
			except HTTPError, e:	
				logging.error("Error saving for "+pocketUser.userID+". Code: "+str(e.code))
				#if e.code == 401:
				# remove the user!
			else:
				logging.info("Saved to Pocket for %s" % pocketUser.userID)

class Add(webapp.RequestHandler):
	def get(self):
		self.response.out.write("""
					<html>
						<body>
							<form action="/" method="post">
								<div style="font-weight:bold;">Evening-Edition for Pocket</div>
								<div style="width:800px;">I found <a href="http://evening-edition.com">Evening Edition</a> recently and loved it.  I also love <a href="http://www.getpocket.com">Pocket.</a>  So, I decided to bring them together.  If you input your Pocket username and password below, every evening at 5:10 I will add the current version of Evening Edition to your pocket account.  If you need to update your password, just come back and re-enter your credentials.  You can also <a href="/remove">remove your account</a>.  Hope you enjoy.  If you have comments, please send them to <a href="mailto:jkeltner@gmail.com">jkeltner@gmail.com</a></div>
								<div style="font-weight:bold; margin-top:25px;">Add a user</div>
								<div>Pocket username: <input type="text" name="userID" size="20" /></div>
								<div>Pocket password: <input type="password" name="password" size="20" /></div>
								<div><input type="submit" value="Add My Pocket ID" /></div>
							</form>
						</body>
					</html>""")

	def post(self):
		# remove any existing users with the same username
		existingUsers = db.GqlQuery("SELECT * FROM PocketUser WHERE userID = '%s'" % self.request.get("userID"))
		for existingUser in existingUsers:
			existingUser.delete()
			logging.info("Pocket user "+existingUser.userID+ "already exists. Removing and adding new version.")
		newUser = PocketUser()
		newUser.userID = self.request.get('userID')
		newUser.password = self.request.get('password')
		newUser.put()
		self.response.out.write("""
					<html>
						<body>
							<div>User %s was added to EE4Pocket.</div>
						</body>
					</html>""" % newUser.userID)
		logging.info("Added Pocket user "+newUser.userID+" to ee4Pocket")


class Remove(webapp.RequestHandler):
	def get(self):
		self.response.out.write("""
					<html>
						<body>
							<form action="/remove" method="post">
								<div>Pocket username: <input type="text" name="userID" size="20" /></div>
								<div><input type="submit" value="Remove Pocket ID" /></div>
							</form>
						</body>
					</html>""")

	def post(self):
		pocketUsers = db.GqlQuery("SELECT * FROM PocketUser WHERE userID = '%s'" % self.request.get("userID"))
		for pocketUser in pocketUsers: #using a loop just in case we get multiple users
			pocketUser.delete()
		self.response.out.write("""
					<html>
						<body>
							<div>Pocket user %s was removed</div>
						</body>
					</html>""" % self.request.get("userID"))
		logging.info("Removed user "+self.request.get("userID")+" to ee4pocket.")


application = webapp.WSGIApplication(
	[('/', Add),
	('/remove', Remove),
	('/execute', Execute)],
		debug=True)

def main():
		run_wsgi_app(application)

if __name__ == "__main__":
		main()