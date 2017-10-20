#!/usr/bin/python

#Read a load of json files from google's distancematrix api, and load them all into 
#a single networkx network, and then figure out an approximation of the Traveling 
#Salesman problem to get the approximate shortest route between the points. 

import networkx
import json
import random
from math import pi, acos, sin, cos

#Empty graph, using a simple graph because I'm making the simplifying assumption 
#that going from one place to another is not significantly different from going back. 
G = networkx.Graph()

#Distance is on a sphere(ish), not a plane. Fite me, Euclid. 
def distance(pA, pB):
	#Have decimal degrees, want radians
	conv = pi/180
	pA = (pA[0] * conv, pA[1] * conv)
	pB = (pB[0] * conv, pB[1] * conv)
	#From spherical law of cosines, should work for distances greater than a few meters
	dAngle = acos(sin(pA[0]) * sin(pB[0]) + cos(pA[0]) * cos(pB[0]) * cos(abs(pA[1]-pB[1])))
	return dAngle * 3959 #Earth's radius, in miles (actually 3,949.9028 to 3,963.1906, depending on location)

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
	return totalLength, route
			
def two_opt_route(graph):
	#Pick a totally stupid random route
	route = list(G.nodes())
	random.shuffle(cities)

	#Again, this fails because I don't have the data to get the distances for all pairs of cities. 


#Locations to coordinates
allLocations = {}

#This is stupid, but I know how many files I have...
for ii in range(66):
	filename = "{0}_rev_geo.json".format(ii)
	with open(filename, 'r') as jsonFile:
		data = json.loads(jsonFile.read())

		#Reverse geocode files have locations as well as names of places
		coords = (data['results'][0]['geometry']['location']['lat'], data['results'][0]['geometry']['location']['lat'])
		allLocations[data['results'][0]['formatted_address']] = coords

#Now add them to my big graph
for start in allLocations.keys():
	startCoords = allLocations[start]
	for end in allLocations.keys():
		if start == end:
			#No self-connections
			continue 
		else:
			#Add an edge between the origin and each destination
			#The values are duration in seconds and distance in meters
			endCoords = allLocations[end]
			G.add_edge(start, end, dist = distance(startCoords, endCoords))


networkx.write_dot(G, "trip.dot")

#Pick a random start city and do a greedy search
#According to wikipedia, this averages a path 25% longer than the shortest possible,
#but certain pathological arrangements can cause it to pick the worst route. 
#I somehow doubt that Mr Toth set me up like that. 
#cities = list(G.nodes())
#random.shuffle(cities)
#start = cities.pop()
#greedy_route(G, start)

#For each start city, pick a greedy route and see how long it is
max_len = float('inf')
best_route = None
count = 0
totalLen = 0

for start_city in list(G.nodes()):
	length, route = greedy_route(G, start_city)
	#For calculating the average greedy route
	totalLen += length
	count += 1
	#Save the best
	if length < max_len:
		max_len = length
		best_route = route

print max_len
print route
print "Average greedy route {0}".format(totalLen/count)
	
