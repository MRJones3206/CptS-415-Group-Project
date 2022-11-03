from arango import ArangoClient
import sys
import time
    

def main():

    # Initialize the client for ArangoDB.
    client = ArangoClient(hosts="http://localhost:8529")

    # Connect to "test" database as root user.
    db = client.db("test", username="root", password="123")

    #Delete graph so you reset the values in it
    db.delete_graph("youtube")

    #If graph exists, connect to it, otherwise create it
    if db.has_graph('youtube'):
        graph = db.graph('youtube')
    else:
        graph = db.create_graph('youtube')


    #If vertex collection exists, connect to it, otherwise create it
    # if graph.has_vertex_collection("videos"): 
    #     videos = graph.vertex_collection("videos")
    # else:

    #Create necessary vertices
    videos = graph.create_vertex_collection("videos")
    relatedVideos = graph.create_vertex_collection("relatedVideos")

    #Create an edge definition (relation) for the graph.
    edges = graph.create_edge_definition(
        edge_collection="related",
        from_vertex_collections=["videos"],
        to_vertex_collections=["relatedVideos"]
    )

    file = open(sys.argv[1], "r")
    for line in file:
        #Traverse each line
        line = line.split()
        #If the ID is unique, insert it.
        if len(line) > 3 and not videos.has(line[0]):
            videos.insert({"_key": line[0],
            "uploader": line[1],
            "age": line[2],
            "category": line[3],
            "length": line[4],
            "views": line[5],
            "rate": line[6],
            "ratings": line[7],
            "comments": line[8]
            })

            #Traverse each related video for a line
            for related in range (9, len(line)):
                #If the ID is unique, insert it.
                if not relatedVideos.has(line[related]):
                    relatedVideos.insert({'_key':line[related]})
                #Create the edge between main video, and current related video    
                edges.insert({"_from": "videos/" + line[0] , "_to": "relatedVideos/" + line[related]})

    # Traverse the graph in outbound direction, breadth-first.
    # result = graph.traverse(
    #     start_vertex="videos/LKh7zAJ4nwo",
    #     direction="outbound",
    #     strategy="breadthfirst"
    # )

    #print(result)

if __name__ == "__main__":
    main()
