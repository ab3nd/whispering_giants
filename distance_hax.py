#!/usr/bin/python

# Load all the json files to get google's estimated driving distances between the cities
# From those driving distances, get a rough calculation of time/distance (average of all times/distances)
# From those driving distances, also estimate the correction factor for converting straight line to 
# expected driving time/distance. This may not be linear, but I'm going to guess as if it is. 
# Fill in any unknown distance pairs with the estimated conversion of straight line to driving. 

import json

#Map cities to distances to all other cities
all_pairs_distances = {}

#Map city locations to coordinates
locations = {}

#This is stupid, but I know how many files I have...
for ii in range(66):
	filename = "{0}_distances.json".format(ii)
	with open(filename, 'r') as jsonFile:
		data = json.loads(jsonFile.read())

		#Should be one
		origin = data['origin_addresses'][0]

		#Zip the destination address and information about getting there
		trips = zip(data['destination_addresses'], data['rows'][0]['elements'])

		import pdb; pdb.set_trace()

		#Count up the total distance and total time
		total_time = 0
		total_dist = 0

		#Now add them to my big pile
		for trip in trips:
			if origin in all_pairs_distances.keys():
				#The values are duration in seconds and distance in meters
				all_pairs_distances['origin'][trip[0]] = {'duration':trip[1]['duration']['value'], 'distance':trip[1]['distance']['value']}
			else:
				#New origin, add a map for it
				all_pairs_distances['origin'] = {}

			#Count up the totals
			total_time += trip[1]['duration']['value']
			total_dist += trip[1]['distance']['value']

			#Calculate the correction factor between straight line distance and 

		#Now we have the average travel rate in m/sec
		travel_rate = total_dist/total_time


