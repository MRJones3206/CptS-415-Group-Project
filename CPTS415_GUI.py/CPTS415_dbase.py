# Matthew R. Jones - SID 11566314
# CptS_415 Final Project Graphical Interface Code
# *_setup.py

from arango import ArangoClient
from pathlib import Path
import json
import time
import re
# *_setup.py contains one class - Setup. This is initialized before the GUI initializes, and is where all
# initial database setup or connection operations should be placed (for instance, logging into the db
# or initializing tables). 
# Should also serve as a container for querying setup states and information (such as) if our database is running or not, and contain
# an appropriate method of tearing itself down.
class Dbase:
	def __init__(self, name="test", delete_mode = "nothing",  population_path_count=3):
		# Initialize the client for ArangoDB.
		self.client = ArangoClient(hosts="http://localhost:8529")
		# Connect to "test" database as root user.
		self.root_db = self.client.db("_system", username="root", password="123")
		self.active_db = self.client.db(name, username="root", password="123")
		self.delete_mode = delete_mode
		self.name = name
		self.population_path_count = population_path_count
		self.graph = None
		self.videos = None
		self.relatedVideos = None
		self.edges = None
		self.numberOfNodes = 0
		self.numberOfEdges = 0
		self.maxDegree = 0
		self.lowDegree = 20

		self.generate_db()
	
	def teardown(self):
		self.client.close()

	def generate_db(self):
		print(self.delete_mode)
		if self.delete_mode == 'truncate':
			if not self.root_db.has_database(self.name):
				print("Database does not exist. Cannot truncate creating instead.")
			else:
				print(f"Truncating database: {self.name}")
				self.root_db.delete_database(self.name)

			self.generate_new_db()

		if self.delete_mode == 'delete':
			if not self.root_db.has_database(self.name):
				print("Database does not exist. Cannot delete, exiting instead.")
				return

			self.root_db.delete_database(self.name)

		if self.delete_mode == 'create':
			if self.root_db.has_database(self.name):
				print("Database exists, exiting.")
				return
			
			print(f"Generating a new database: {self.name}")
			self.generate_new_db()
		
		else:
			print(f"User specified to do nothing. Attempting to connect to database: {self.name}")

	def generate_new_db(self):
		self.root_db.create_database(self.name)
		
		self.graph = self.active_db.create_graph('youtube')

		#Create necessary vertex collections for the data.
		self.videos = self.graph.create_vertex_collection("videos")
		self.relatedVideos = self.graph.create_vertex_collection("relatedVideos")

		#Create an edge definition (relation) for the graph.
		self.edges = self.graph.create_edge_definition(
			edge_collection="related",
			from_vertex_collections=["videos"],
			to_vertex_collections=["relatedVideos"]
		)
		self.populate_paths()

	def populate_paths(self):
		path = Path(__file__).parents[1]
		path = path / "YoutubeAnalyzerData"

		paths_to_populate = []
		for dir in path.iterdir():
			m = re.search(r'\d+$', str(dir))
			if m is not None:
				for file in dir.iterdir():
					if not file.stem == "log":
						paths_to_populate.append(file)
		
		self.populate(src=paths_to_populate)
		
	def populate(self, src: list):
		start_time = time.time_ns()
		for i in range(0, int(self.population_path_count)):
			path = src[i]
			with path.open() as f:
				file_parse_time = time.time_ns()
				self.parse_data(f, i=i)
				print(f"Parse Time (microseconds): {( time.time_ns()- file_parse_time ) / 1000.0} ")

		self.set_graph_meta()
		print("Done.")
		print(f"Total Time to parse (microseconds): {( time.time_ns()- start_time ) / 1000.0 }")

	# Function to create database, and parse the passed file into the database
	def parse_data(self, file, i=0):
		
		#Create the necessary graph for the data.
		self.active_db.graphs()
		print(f"Parsing file {i+1} of {int(self.population_path_count)}")
		#Parse the data into the graph
		for line in file:
			#Traverse each line of the passed file
			line = line.split()
			degree = 0
			#If the ID is unique and data is in valid format, insert it.
			if len(line) > 3 and not self.videos.has(line[0]):
				#Reason for this check and two sections for insertion is because some entries have category such as
				#People & Blogs, and on split, character '&' would represent line[4] hence not being possible to turn to int
				#With this check, all categories in that format are handled
				if line[4] != '&':
					self.videos.insert({"_key": line[0],
					"uploader": line[1],
					"age": int(line[2]),
					"category": line[3],
					"length": int(line[4]),
					"views": int(line[5]),
					"rate": float(line[6]),
					"ratings": int(line[7]),
					"comments": int(line[8])
					})
					self.numberOfNodes += 1

					#Traverse each related video for a line
					for related in range (9, len(line)):
						#If the ID is unique, insert it.
						if not self.relatedVideos.has(line[related]):
							self.relatedVideos.insert({'_key':line[related]})
						#Create the edge between main video, and current related video    
						self.edges.insert({"_from": "videos/" + line[0] , "_to": "relatedVideos/" + line[related]})
						self.numberOfEdges += 1
						degree += 1
				
				else:
					self.videos.insert({"_key": line[0],
					"uploader": line[1],
					"age": int(line[2]),
					"category": line[3] + " " + line[4] + " " + line[5],
					"length": int(line[6]),
					"views": int(line[7]),
					"rate": float(line[8]),
					"ratings": int(line[9]),
					"comments": int(line[10])
					})
					self.numberOfNodes += 1

					#Traverse each related video for a line
					for related in range (11, len(line)):
						#If the ID is unique, insert it.
						if not self.relatedVideos.has(line[related]):
							self.relatedVideos.insert({'_key':line[related]})
						#Create the edge between main video, and current related video    
						self.edges.insert({"_from": "videos/" + line[0] , "_to": "relatedVideos/" + line[related]})
						self.numberOfEdges += 1
						degree += 1
			
			#Get the max and low degree for the graph
			if degree > self.maxDegree: self.maxDegree = degree
			if degree < self.lowDegree: self.lowDegree = degree
		

	def set_graph_meta(self):
		averageDegree = round(self.numberOfEdges / self.numberOfNodes, 2)
		graphDensity = round(self.numberOfEdges / (self.numberOfNodes * 20), 2)

		graphData = {"Node Count":self.numberOfNodes, "Edge Count":self.numberOfEdges, 
		"Max Degree":self.maxDegree, "Min Degree":self.lowDegree, "Average Degree":averageDegree, "Graph Density": graphDensity}
		
		#Save the data trelated to the graph
		with open('data.json', 'w', encoding='utf-8') as f:
			json.dump(graphData, f, ensure_ascii=False, indent=4)

	def rank_graph(self):
		pregel = self.active_db.pregel

		job_id = self.active_db.pregel.create_job(
			graph='youtube',
			algorithm='pagerank',
			store=True,
			max_gss=100,
			thread_count=1,
			async_mode=False,
			result_field='rank',
			algorithm_params={'threshold': 0.000001},
			vertexCollections=['videos', 'relatedVideos'],
			edgeCollections=['related']
		)

		
