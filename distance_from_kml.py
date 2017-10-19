#!/usr/bin/python

from fastkml import kml
from math import acos, cos, sin, pi
import json
import requests
import time 
import my_api_key

# Reads a KML file and extracts all the location coordinates, then does Google maps API queries to 
# get the driving distance between all locations. This can then be used to calculate an order for the 
# points that minimizes the total driving distance, using any of the approaches used for the Traveling
# Salesman problem. 


#Free API limits it to 25 origins or 25 destinations per request, and 100 elements per request
# "Note: each query sent to the Distance Matrix service is limited by the number of allowed 
# elements, where the number of origins times the number of destinations defines the number of elements."
#So that's 10 sources and 10 destinations per request, and will require a lot of weird breaking up 
#and throttling of the requests. 
# "2,500 free elements per day..." I have about 50-60 locations, so 2500 to 3600 elements total. 
# One way to limit this is to use the straight-line distance between the locations first, to find 
# neighbor sets for each location, and then only consider perhaps the 10 closest instead of all 
# of the possible sets. This may hamstring TSP. 

#Also, the points located in Canada, Hawaii, and Alaska are special cases, and can be ignored 
#for planning a trip over the lower 48 states. 

#Distance is on a sphere(ish), not a plane. Fite me, Euclid. 
def distance(pA, pB):
	#Have decimal degrees, want radians
	conv = pi/180
	pA = (pA[0] * conv, pA[1] * conv)
	pB = (pB[0] * conv, pB[1] * conv)
	#From spherical law of cosines, should work for distances greater than a few meters
	dAngle = acos(sin(pA[0]) * sin(pB[0]) + cos(pA[0]) * cos(pB[0]) * cos(abs(pA[1]-pB[1])))
	return dAngle * 3959 #Earth's radius, in miles (actually 3,949.9028 to 3,963.1906, depending on location)

#Data structure for storing the points
locations = {}

#Read the KML file
with open("./Locations_of_Whispering_Giants_Sculptures.kml", "rt") as kmlFile:
	fKml = kml.KML()
	fKml.from_string(kmlFile.read())

	#This is just magic numbers, because fastKML is... rough for getting stuff out of
	#Get the first level of features, there's one, it's the whole document
	fl = list(fKml.features())
	#Get the next level of features, this one happens to be the folders
	fl2 = list(fl[0].features())
	#The first folder is the accessible giants, so get the actual placemarks out of it
	points = list(fl2[0].features())

	#Store just the location coordinates and name from the map
	for point in points:
		#NOTE: it is y, then x, not the other way around. Latitude, then Longitude.
		locations[point.name.strip()] = (point.geometry.y, point.geometry.x)
	
#Now we have locations, filter out the ones in Alaska and Canada
remove = ["Winnipeg Beach", "North Bay", "59-254 Kamehameha Hwy", "Likely location of #40", "Prince William Sound College"]
for key in locations.keys():
	if key in remove:
		del locations[key]
		print "Removed {0}".format(key)

distances = {}

#For every location...
for startLoc in locations.keys():
	#...to every other location...
	endDistances = {}
	for endLoc in locations.keys():
		if startLoc != endLoc:
			#They're not the same, so calculate the distance
			endDistances[endLoc] = distance(locations[startLoc], locations[endLoc])
	distances[startLoc] = endDistances

with open("all_distances.json", 'w') as outFile:
	outFile.write(json.dumps(distances))

#For each starting location, get the ten closest locations
trimmedDistances = {}
for startLoc in distances.keys():
	closest = sorted(distances[startLoc].iteritems(), key=lambda(k,v):(v,k))[:10]
	trimmedDistances[startLoc] = closest

#Save that too
with open("closest_points.json", 'w') as outFile:
	outFile.write(json.dumps(trimmedDistances))

#NOW WE ROCK. For every point, get the driving distance to the ten closest points via google API
count = 0
for startLoc in trimmedDistances.keys():
	
	#set up the strings for the URL
	#The origin is just two coordinates seperated by a comma (and no space)
	originCoords = "{0},{1}".format(locations[startLoc][0], locations[startLoc][1])
	#Destinations are a list of coordinates, seperated by a comma and no space, delimited by a vertical bar
	#This nested list comprehension is a vile one-liner. I can write perl in any language. 
	destCoords = "|".join(["{0},{1}".format(x[0], x[1]) for x in [locations[k[0]] for k in trimmedDistances[startLoc]]])

	API_key = my_api_key.API_key
	url = "https://maps.googleapis.com/maps/api/distancematrix/json"
	#Combine the parameters, the requests package takes care of URL encoding
	payload = {'key':API_key, 'units':'imperial', 'destinations':destCoords, 'origins':originCoords}

	#Fire the request
	r = requests.get(url, params=payload)

	if r.status_code == 200:
		with open("{0}_distances.json".format(count), 'w') as outFile:
			outFile.write(r.text)
		count += 1
	else:
		print "Got {0} in request status code, expected 200, quitting".format(r.status_code)
		break

	#Rate limiting for broke hackers
	time.sleep(5)