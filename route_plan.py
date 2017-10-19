#!/usr/bin/python

#Read a load of json files from google's distancematrix api, and load them all into 
#a single networkx network, and then figure out an approximation of the Traveling 
#Salesman problem to get the approximate shortest route between the points. 

import networkx
import json
import random

#Empty graph, using a simple graph because I'm making the simplifying assumption 
#that going from one place to another is not significantly different from going back. 
G = networkx.Graph()

#TSP makes the assumption that you can get to any city from any other city
#My data set doesn't make that assumption, since it just has the distances to the 10 closest cities
#As a consequence the greedy algorithm paints itself into corners easily
def greedy_route(graph, startCity):
	unvisited = list(graph.nodes())
	#Remove the start city and add it to the route
	unvisited.remove(startCity)
	route = [startCity]

	#Initialize the total length
	totalLength = 0

	while len(unvisited) > 0:
		#Get the minimum weight edge (to the next closest city)
		neighbors = graph.adj[startCity]
		minDist = float('inf')
		closest = None

		#Sort the neghbors by distance
		proxNeighbors = sorted(neighbors.iteritems(), key=lambda (x,y):y['dist'])
		#Get the closest unvisited neighbor
		for n in proxNeighbors:
			if n[0] in unvisited:
				startCity = n[0]
				route.append(n[0])
				unvisited.remove(n[0])
				totalLength += n[1]['dist']
				print len(unvisited)

	#Now we're done, and have an ordered list of cities, plus the total distance
	print route
	print totalLength

			
def two_opt_route(graph):
	#Pick a totally stupid random route
	route = list(G.nodes())
	random.shuffle(cities)

	#Again, this fails because I don't have the data to get the distances for all pairs of cities. 


#This is stupid, but I know how many files I have...
for ii in range(66):
	filename = "{0}_distances.json".format(ii)
	with open(filename, 'r') as jsonFile:
		data = json.loads(jsonFile.read())

		#Should be one
		origin = data['origin_addresses'][0]

		#Zip the destination address and information about getting there
		trips = zip(data['destination_addresses'], data['rows'][0]['elements'])

		#Now add them to my big graph
		for trip in trips:
			#Add an edge between the origin and each destination
			#The values are duration in seconds and distance in meters
			G.add_edge(origin, trip[0], duration = trip[1]['duration']['value'], dist = trip[1]['distance']['value'])


networkx.write_dot(G, "trip.dot")

#Pick a random start city and do a greedy search
#According to wikipedia, this averages a path 25% longer than the shortest possible,
#but certain pathological arrangements can cause it to pick the worst route. 
#I somehow doubt that Mr Toth set me up like that. 
#cities = list(G.nodes())
#random.shuffle(cities)
#start = cities.pop()
#greedy_route(G, start)


