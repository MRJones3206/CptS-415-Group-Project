# Matthew R. Jones - SID 11566314
# CptS_415 Final Project Graphical Interface Code
# *_setup.py

from arango import ArangoClient
# *_setup.py contains one class - Setup. This is initialized before the GUI initializes, and is where all
# initial database setup or connection operations should be placed (for instance, logging into the db
# or initializing tables). 
# Should also serve as a container for querying setup states and information (such as) if our database is running or not, and contain
# an appropriate method of tearing itself down.
class Setup:
	def __init__(self):
		# Initialize the client for ArangoDB.
		self.client = ArangoClient(hosts="http://localhost:8529")
		# Connect to "test" database as root user.
		self.db = self.client.db("test", username="root", password="123")
	def teardown(self):
		self.client.close()

