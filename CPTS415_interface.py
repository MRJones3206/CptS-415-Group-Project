#!/usr/bin/env python3

from arango import ArangoClient
import sys

#Function to create database, and parse the passed file into the database
def parse_data(file):
	#Initialize the client for ArangoDB.
	client = ArangoClient(hosts="http://localhost:8529")

	#Connect to the default database as root user.
	db = client.db("_system", username="root", password="")

	#if test database exists, delete it, and create a new one
	#done for easier testing so you can just keep running script and not worry about duplicate data
	if db.has_database('test'):
		db.delete_database('test')
	db.create_database('test')

	#Now connect to the newly created database
	db = client.db("test", username="root", password="")

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


#Function that performs top version of search
def search_top(count, category, filterSign, value):

	#Connect to the already created database
	client = ArangoClient(hosts="http://localhost:8529")
	db = client.db("test", username="root", password="")

	#Create the query based on passed arguments and execute it
	query = 'FOR doc IN videos FILTER doc.' + category + ' ' + filterSign + ' @value RETURN doc'
	cursor = db.aql.execute(query, bind_vars={'value': value})

	#turn the retrieved data into the iterable list
	test = cursor.batch()
	lst = list(test)

	#sort the list based on the specified category
	lst.sort(key=lambda x: x[category], reverse=True)

	#if there are less entries than specified by count, print that many entries
	#else print the passed number of entries
	#example - we want 3 things printed, but the list only has 1 entry, need a check for this.
	if count > len(lst):
		for x in lst:
			print(x[category], x['_key'])
	else:
		for x in range(0, count):
			print(lst[x][category],lst[x]['_key'])

        

#Function that performs range version of search
def search_range(category, lowRange, highRange):

	#Connect to the already created database
	client = ArangoClient(hosts="http://localhost:8529")
	db = client.db("test", username="root", password="")

	#Create the query based on passed arguments and execute it
	query = 'FOR doc IN videos FILTER doc.' + category + ' >= @lowrange AND doc.' + category + ' <= @highrange RETURN doc'
	cursor = db.aql.execute(query, bind_vars={'lowrange': lowRange,'highrange': highRange})

	#turn the retrieved data into the iterable list
	test = cursor.batch()
	lst = list(test)

	#sort the list based on the specified category
	lst.sort(key=lambda x: x[category], reverse=True)

	#Print the retrieved values matcing the filtered range including the video key
	for x in lst:
		print(x[category], x['_key'])


def main():
	#If no argument was specified, print the error to the user.
	if len(sys.argv) <= 1: print("Needed argument is 'top' or 'range'.")

	#If the first agument is search, provide second argument of top or range and execute search
	elif sys.argv[1] == "search":
		#If less or more arguments than needed, print the instruction.
		if len(sys.argv) <= 2 or len(sys.argv) > 3: print("Use the search argument with one additional 'top' or 'range' argument.") 
		#If second argument is top, execute specified top search
		elif sys.argv[2] == "top": search_top(3, 'age', '<=', 538)
		#If second argument is range, execute specified range search
		elif sys.argv[2] == "range": search_range('length', 400, 500)
		#If second argument is not valid, let the user know
		else: print("Unrecognized search argument, please use 'top' or 'range' as the search argument.")
			

	#If the first argument is parse, parse in the necessary data, second argument is needed which is a file to parse
	elif sys.argv[1] == "parse":
		#If less or more arguments than needed, print the instruction.
		if len(sys.argv) <= 2 or len(sys.argv) > 3: print("Use the parse argument with one additional argument - name of the file to parse.")
		else:
			#Try opening the file if it exists
			try: 
				file = open(sys.argv[2], "r")
				parse_data(file)
			#Otherwise print the error
			except: print("Please provide a valid file.")
	
	#If first argument is invalid, let the user know wht arguments are supported
	else: print("Invalid first argument. Supported arguments are 'parse' and 'search'.")
	
if __name__ == "__main__":
    main()
