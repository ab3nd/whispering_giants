#!/usr/bin/python

#Get driving times for the routes from two-opt optimization. 
#It would have been better to optimize based on all-pairs driving distance, but that 
#would require paying google for higher API quotas. 


#My list of all the two-opt routes
#Originally starting from every possible locaiton, but that got optmizied away in favor of
#starting from locations that are on the coasts, mostly. 
import two_opt_routes
import my_api_key
import requests
import time
import json
import pickle


example_json ='''{
   "destination_addresses" : [ "New York, NY, USA" ],
   "origin_addresses" : [ "Washington, DC, USA" ],
   "rows" : [
      {
         "elements" : [
            {
               "distance" : {
                  "text" : "225 mi",
                  "value" : 361715
               },
               "duration" : {
                  "text" : "3 hours 49 mins",
                  "value" : 13725
               },
               "status" : "OK"
            }
         ]
      }
   ],
   "status" : "OK"
}'''

def parseJson(jsonStr):
	data = json.loads(jsonStr)
	distance = data['rows'][0]['elements'][0]['distance']['value'] 
	duration = data['rows'][0]['elements'][0]['duration']['value'] 
	return distance, duration



stretches = {}
#The routes are a list of lists
for route in two_opt_routes.all_routes:
	#Between each pair of cities is a stretch, we don't know the lenght yet
	#Putting them in a hash means I only keep unique ones 
	for start, end in zip(route[:-1], route[1:]):
		stretches[(start, end)] = 0

print stretches.keys()
print len(stretches.keys())

#If the stretches file already exists, load it, otherwise, create it from google API calls
try: 
	with open("stretches.pickle", 'rb') as infile:
		stretches = pickle.load(infile)

except IOError:
	for stretch in stretches.keys():
		API_key = my_api_key.API_key
		url = "https://maps.googleapis.com/maps/api/distancematrix/json"
		#Combine the parameters, the requests package takes care of URL encoding
		payload = {'key':API_key, 'units':'imperial', 'destinations':stretch[1], 'origins':stretch[0]}

		#Fire the request
		r = requests.get(url, params=payload)

		if r.status_code == 200:
			#import pdb; pdb.set_trace()
			distance, duration = parseJson(r.text)
			stretches[stretch] = {"dist":distance, 'dur':duration}

		else:
			print "Got {0} in request status code, expected 200, quitting".format(r.status_code)
			break

		#Rate limiting for broke hackers
		time.sleep(1)

	with open("stretches.pickle", 'w') as outfile:
		pickle.dump(stretches, outfile)

#stretches now contains a lookup table for locations to distances
for route in two_opt_routes.all_routes:
	total_distance = 0
	total_time = 0
	for start, end in zip(route[:-1], route[1:]):
		total_distance += stretches[(start, end)]['dist']
		total_time += stretches[(start, end)]['dur']
	#convert to miles and hours from meters and seconds
	total_distance = total_distance / 1609.34 
	total_time = total_time / 360

	print route
	print "{0} hours".format(total_time)
	print "{0} miles".format(total_distance)
	print "This probably includes driving back to the start"
	print "------"