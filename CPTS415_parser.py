from arango import ArangoClient
import sys
import time

def main():

    # Initialize the client for ArangoDB.
    client = ArangoClient(hosts="http://localhost:8529")

    # Connect to "test" database as root user.
    db = client.db("test", username="root", password="123")

    #Delete graph so you reset the values
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
    #Create vertex
    videos = graph.create_vertex_collection("videos")


    #Create an edge definition (relation) for the graph.
    # edges = graph.create_edge_definition(
    #     edge_collection="register",
    #     from_vertex_collections=["videos"],
    #     to_vertex_collections=["relatedVideos"]
    # )
    file = open(sys.argv[1], "r")
    for line in file:
        line = line.split()
        #If videos has the key don't insert, else insert
        if len(line) > 3 and not videos.has(line[0]):
            videos.insert({"videoID": line[0],
            "uploader": line[1],
            "age": line[2],
            "category": line[3],
            "length": line[4],
            "views": line[5],
            "rate": line[6],
            "ratings": line[7],
            "comments": line[8],
        # "related IDs ": line[9],
        })

    # inser edges from vides to related videos?.
    # edges.insert({"_from": "students/01", "_to": "lectures/MAT101"})
    # edges.insert({"_from": "students/01", "_to": "lectures/STA101"})
    # edges.insert({"_from": "students/01", "_to": "lectures/CSC101"})
    # edges.insert({"_from": "students/02", "_to": "lectures/MAT101"})
    # edges.insert({"_from": "students/02", "_to": "lectures/STA101"})
    # edges.insert({"_from": "students/03", "_to": "lectures/CSC101"})

    # Traverse the graph in outbound direction, breadth-first.
    # result = graph.traverse(
    #     start_vertex="students/01",
    #     direction="outbound",
    #     strategy="breadthfirst"
    # )

    #print(result)

if __name__ == "__main__":
    main()
