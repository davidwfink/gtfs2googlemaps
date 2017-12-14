import csv
import googlemaps
import json
import os

#agencies is a dictionary where the key is the agency_id and the value is the agency_name
agencies = {}
with open('gtfs/agency.txt', encoding="utf8") as f:
    for row in csv.DictReader(f):
        agencies[row["agency_id"]] = row['agency_name']
#print("agencies: " + json.dumps(agencies))

#routes is a dictionary where the key is the route_id, and the value is an element dictionary.
#The element dictionary includes information about the route, and another dictionary of stops
#which will be populated below
routes = {}
route_ids = []
with open('gtfs/routes.txt', encoding="utf8") as f:
    for row in csv.DictReader(f):
        route = {}
        route['num'] = row['route_short_name']
        route['name'] = row['route_long_name']
        #agency is populated with agency_name
        route['agency_name'] = agencies[row['agency_id']]
        route['stops'] = {}
        routes[row['route_id']] = route
        route_ids.append(row['route_id'])
#print("routes: " + json.dumps(routes))
#print("route_ids: " + json.dumps(route_ids))

#trips is a dictionary that contains the first trip for each route_id. The key is the trip_id
#and the value is the route_id
trips = {}
trip_ids = []
processed_route_ids = []
with open('gtfs/trips.txt', encoding="utf8") as f:
    for row in csv.DictReader(f):
        if (row["route_id"] in route_ids) and not (row["route_id"] in processed_route_ids):
            trips[row['trip_id']] = row['route_id']
            trip_ids.append(row["trip_id"])
            processed_route_ids.append(row["route_id"])
#print("trips: " + json.dumps(trips))
#print("trip_ids: " + json.dumps(trip_ids))

#This code populates the stops element dictionary of each route in the route dictionary
#The key is the stop_sequence, and the value is the stop_id
stop_ids = []
with open('gtfs/stop_times.txt', encoding="utf8") as f:
    for row in csv.DictReader(f):
        if row["trip_id"] in trip_ids:
            routes[trips[row['trip_id']]]['stops'][row['stop_sequence']] = row['stop_id']
            stop_ids.append(row["stop_id"])
#print("routes: " + json.dumps(routes))
#print("stop_ids: " + json.dumps(stop_ids))

#stops is a dictionary where the key is the stop_id, and the value is an element dictionary
# that includes information about each stop
stops = {}
with open('gtfs/stops.txt', encoding="utf8") as f:
    for row in csv.DictReader(f):
        if row['stop_id'] in stop_ids:
            stops[row['stop_id']] = row
#print("stops: " + json.dumps(stops))

print("var allData = {", end='')
lastnum = ""
for r in routes:
    route = routes[r]
    if lastnum == route['num']:
        print("],[", end='')
    else:
        if lastnum != "":
            print("]], ", end='')
        print("\"" + route['num'] + "\": [[", end='')
    lastnum = route['num']
    first = True
    for stop in route['stops']:
        stop_id = route['stops'][stop]
        if first == False:
            print(",", end='')
        print(stops[stop_id]['stop_lat'] + "," + stops[stop_id]['stop_lon'], end='')
        first = False
print("]]};")

maps = googlemaps.Client(key=os.environ['GOOGLE_MAPS_API_KEY'], timeout=None, connect_timeout=None, read_timeout=None, retry_timeout=60, requests_kwargs=None, queries_per_second=10, channel=None)
print("var allData = {", end='')
lastnum = ""
for r in routes:
    route = routes[r]
    if lastnum == route['num']:
        print("],[", end='')
    else:
        if lastnum != "":
            print("]], ", end='')
        print("\"" + route['num'] + "\": [[", end='')
    lastnum = route['num']

    stops_in_route = []
    for stop in route['stops']:
        stop_id = route['stops'][stop]
        stops_in_route.append(stops[stop_id]['stop_lat'] + "," + stops[stop_id]['stop_lon'])
    snapped = maps.snap_to_roads(path=stops_in_route, interpolate=True)

    first = True
    for point in snapped:
        if first == False:
            print(",", end='')
        print(point['location']['latitude'], point['location']['longitude'], sep=',', end='')
        first = False

print("]]};")
