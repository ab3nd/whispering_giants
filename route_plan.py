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


#Plot a route on a map
def plotRoute(locations, route):
	from mpl_toolkits.basemap import Basemap
	import numpy as np
	import matplotlib.pyplot as plt

	fig = plt.figure()
	#Lower left and upper right corners of the lower 48
	#23.555074, -123.837324
	#50.670481, -66.303429
	m = Basemap(llcrnrlon=-127.837324,llcrnrlat=23.555074,urcrnrlon=-66.303429,urcrnrlat=50.670481,\
            rsphere=(6378137.00,6356752.3142), resolution='l',projection='merc',lat_ts=50.)

	m.drawcoastlines()
	m.fillcontinents()

	#For each city and the next one in the route
	for start, end in zip(route[:-1], route[1:]):
		sLat, sLong = locations[start]
		eLat, eLong = locations[end]
		m.drawgreatcircle(sLong, sLat, eLong, eLat, linewidth=2, color='b')
	
	plt.show()
	plt.clf()

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
				
	#Now we're done, and have an ordered list of cities, plus the total distance
	#print route
	#print totalLength
	return totalLength, route
			

def getLength(route, locations):
	totalLen = 0
	#for each pair in the ordred list, add the distance between them to the total distance
	for start, end in zip(route[:-1], route[1:]):
		totalLen += distance(locations[start], locations[end])

	return totalLen

def inner_two_opt(route, locations):
	length = getLength(route, locations)

	for ii, start in enumerate(route):
		for kk in range(ii+1, len(route)):
			#Do the two-opt swap
			newRoute = route[:ii]
			newRoute.extend(list(reversed(route[ii:kk])))
			newRoute.extend(route[kk:])

			#Make sure I didn't screw up my indices
			assert len(newRoute) == len(route)
			
			# check if we made the route any shorter
			newLength = getLength(newRoute, locations)
			#print newLength
			if newLength < length:
				improvement = length - newLength
				return improvement, newRoute

	#Got through the whole route without improving it
	return 0, route

def two_opt_route(route, locations):
	#Given a route, ideally one picked by the greedy algorithm, remove two edges and replace them with 
	#two different edges. If that gets us a shorter route, keep it. 
	
	improvement, newRoute = inner_two_opt(route, locations)
	while improvement > 0:
		print improvement
		improvement, newRoute = inner_two_opt(newRoute, locations)

	return newRoute

#Locations to coordinates
allLocations = {}

#This is stupid, but I know how many files I have...
for ii in range(66):
	filename = "{0}_rev_geo.json".format(ii)
	with open(filename, 'r') as jsonFile:
		data = json.loads(jsonFile.read())

		#Reverse geocode files have locations as well as names of places
		coords = (data['results'][0]['geometry']['location']['lat'], data['results'][0]['geometry']['location']['lng'])
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
lengths  = []

for start_city in list(G.nodes()):
	length, route = greedy_route(G, start_city)
	#For calculating the average greedy route
	totalLen += length
	count += 1
	#Save the best
	if length < max_len:
		max_len = length
		best_route = route
	#save all the lengths
	lengths.append(length)

print route
print "Average greedy route {0}, this route {1}".format(totalLen/count, max_len)
#print sorted(lengths)

#plotRoute(allLocations, route)
	
route = two_opt_route(route, allLocations)

#Get the two-opt route based on the greedy one
print "Two-opt route length: {0}".format(getLength(route, allLocations))
print route
plotRoute(allLocations, route)