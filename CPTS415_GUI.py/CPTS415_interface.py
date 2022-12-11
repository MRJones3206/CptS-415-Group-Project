#!/usr/bin/env python3

from arango import ArangoClient
import sys
import json

#Load in the data related to the graph
def get_stats():
	with open('data.json', 'r', encoding='utf-8') as f:
		data = json.load(f)
	return data

#Function that performs top version of search
def search_top(count, category, filterSign, value):

	#Connect to the already created database
	client = ArangoClient(hosts="http://localhost:8529")
	db = client.db("test", username="root", password="123")

	#Create the query based on passed arguments and execute it
	query = 'FOR doc IN videos FILTER doc.' + category + ' ' + filterSign + ' @value LIMIT ' + str(count) + ' RETURN doc'
	cursor = db.aql.execute(query, bind_vars={'value': value})

	#turn the retrieved data into the iterable list
	test = cursor.batch()
	lst = list(test)

	#sort the list based on the specified category
	lst.sort(key=lambda x: x[category], reverse=True)

	return lst


#Function that performs range version of search
def search_range(category, lowRange, highRange):

	#Connect to the already created database
	client = ArangoClient(hosts="http://localhost:8529")
	db = client.db("test", username="root", password="123")

	#Create the query based on passed arguments and execute it
	query = 'FOR doc IN videos FILTER doc.' + category + ' >= @lowrange AND doc.' + category + ' <= @highrange LIMIT 10  RETURN doc'
	cursor = db.aql.execute(query, bind_vars={'lowrange': lowRange,'highrange': highRange})

	#turn the retrieved data into the iterable list
	test = cursor.batch()
	lst = list(test)

	#sort the list based on the specified category
	lst.sort(key=lambda x: x[category], reverse=True)

	return lst

def pagerank():
	client = ArangoClient(hosts="http://localhost:8529")
	db = client.db('test', username='root', password="123")

	query = "FOR rv in relatedVideos FOR v in videos FILTER rv._key == v._key SORT rv.rank DESC LIMIT 10 RETURN {key: rv._key, uploader: v.uploader, rank: rv.rank, views: v.views, ratings: v.ratings, category: v.category, length: v.length, comments: v.comments}"
	cursor = db.aql.execute(query)
	
	top = cursor.batch()
	lst = list(top)

	return lst
	
def main():
	
	global numberOfNodes
	global numberOfEdges

	#If no argument was specified, print the error to the user.
	if len(sys.argv) <= 1: print("Needed argument is 'parse' or 'search'.")

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
	
	#if we want to provide statistics about the database
	elif sys.argv[1] == "statistics":
		get_stats()
	
if __name__ == "__main__":
    main()
