# Matthew R. Jones - SID 11566314
# CptS_415 Final Project Graphical Interface Code
# *_setup.py

from arango import ArangoClient
# *_setup.py contains one class - Setup. This is initialized before the GUI initializes, and is where all
# initial database setup or connection operations should be placed (for instance, logging into the db
# or initializing tables). 
# Should also serve as a container for querying setup states and information (such as) if our database is running or not, and contain
# an appropriate method of tearing itself down.
class Dbase:
	def __init__(self):
		# Initialize the client for ArangoDB.
		self.client = ArangoClient(hosts="http://localhost:8529")
		# Connect to "test" database as root user.
		self.db = self.client.db("_system", username="root", password="123")
		self.populate()
	def teardown(self):
		self.client.close()

	def populate(self, src="0.txt"):
		try:
			file = open(src, "r")
		except:
			print("Unable to open file specified, or '0.txt' if none.")
		else:
			#Initialize the client for ArangoDB.
			client = self.client

			#Connect to the default database as root user.
			db = client.db("_system", username="root", password="123")

			#if test database exists, delete it, and create a new one
			#done for easier testing so you can just keep running script and not worry about duplicate data
			if db.has_database('test'):
				return
			db.create_database('test')

			#Now connect to the newly created database
			db = client.db("test", username="root", password="123")

			#Create the necessary graph for the data.
			graph = db.create_graph('youtube')

			#Create necessary vertex collections for the data.
			videos = graph.create_vertex_collection("videos")
			relatedVideos = graph.create_vertex_collection("relatedVideos")

			#Create an edge definition (relation) for the graph.
			edges = graph.create_edge_definition(
				edge_collection="related",
				from_vertex_collections=["videos"],
				to_vertex_collections=["relatedVideos"]
			)

			#Parse the data into the graph
			for line in file:
				#Traverse each line of the passed file
				line = line.split()

				#If the ID is unique and data is in valid format, insert it.
				if len(line) > 3 and not videos.has(line[0]):
					#Reason for this check and two sections for insertion is because some entries have category such as
					#People & Blogs, and on split, character '&' would represent line[4] hence not being possible to turn to int
					#With this check, all categories in that format are handled
					if line[4] != '&':
						videos.insert({"_key": line[0],
						"uploader": line[1],
						"age": int(line[2]),
						"category": line[3],
						"length": int(line[4]),
						"views": int(line[5]),
						"rate": float(line[6]),
						"ratings": int(line[7]),
						"comments": int(line[8])
						})

							#Traverse each related video for a line
						for related in range (9, len(line)):
							#If the ID is unique, insert it.
							if not relatedVideos.has(line[related]):
								relatedVideos.insert({'_key':line[related]})
							#Create the edge between main video, and current related video    
							edges.insert({"_from": "videos/" + line[0] , "_to": "relatedVideos/" + line[related]})
					
					else:
						videos.insert({"_key": line[0],
						"uploader": line[1],
						"age": int(line[2]),
						"category": line[3] + " " + line[4] + " " + line[5],
						"length": int(line[6]),
						"views": int(line[7]),
						"rate": float(line[8]),
						"ratings": int(line[9]),
						"comments": int(line[10])
						})

						#Traverse each related video for a line
						for related in range (11, len(line)):
							#If the ID is unique, insert it.
							if not relatedVideos.has(line[related]):
								relatedVideos.insert({'_key':line[related]})
							#Create the edge between main video, and current related video    
							edges.insert({"_from": "videos/" + line[0] , "_to": "relatedVideos/" + line[related]})

