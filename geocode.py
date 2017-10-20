#!/usr/bin/python

#Convert from the lat/longs in the kml file to google's idea of the names of those addresses, 
# and save the latitude and longitudes as well as the names in a json file

import json
from fastkml import kml
import requests
import my_api_key

#Read the existing all distances file
distance_data = None
with open("all_distances.json", 'r') as jsonFile:
	distance_data = json.loads(jsonFile.read())

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


count = 0
for place in locations.keys():
	url = "https://maps.googleapis.com/maps/api/geocode/json"
	payload = {'latlng':"{0},{1}".format(locations[place][0], locations[place][1]), 'key':my_api_key.API_key}
	
	#Get the result from google
	r = requests.get(url, params=payload)
	if r.status_code == 200:
		reverse_geo = json.loads(r.text)
		reverse_geo["original"] = place
		with open("{0}_rev_geo.json".format(count), 'w') as outFile:
			outFile.write(json.dumps(reverse_geo))
		count += 1
	else:
		print "Got {0} in request status code, expected 200, quitting".format(r.status_code)
		print r.text