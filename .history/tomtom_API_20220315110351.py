import json
import sys
import time
import datetime
from urllib.request import urlopen
import csv
import pandas as pd 
from datetime import datetime 
import time 


apikey = ["Ox4YwdYU3BSMooPpB65EUl5Ioxo2wOcN", "UlHtK8wneRhvtAepd41MiEpePgUjGaNG", "RoIba9zpvuYQaC6w9jUoEUgn4nBEZSF0"]


def api_queries(mode, lat_orig, lon_orig, lat_dest, lon_dest, api):
   '''
        Testing case
        mode   = "truck"
        [lat_orig, lon_orig, lat_dest, lon_dest] = [
            52.50930, 13.42936, 52.50844, 13.42859]
        [lat_orig, lon_orig, lat_dest, lon_dest] = [
            30.410934, -86.912323, 38.637062, -77.311096]
   '''
   if mode == "truck":
       url = "https://api.tomtom.com/routing/1/calculateRoute/" + str(lat_orig) + "%2C" + str(lon_orig) + "%3A" + str(lat_dest) + "%2C" + str(
          lon_dest) + "/json?instructionsType=text&routeRepresentation=summaryOnly&computeTravelTimeFor=all&routeType=fastest&traffic=true&avoid=unpavedRoads&travelMode=" + mode + "&vehicleLength=13.6&vehicleWidth=2.45&vehicleHeight=2.45&vehicleAxleWeight=6000&vehicleCommercial=true&key=" + api
   if mode == "car":
       url = "https://api.tomtom.com/routing/1/calculateRoute/" + str(lat_orig) + "%2C" + str(lon_orig) + "%3A" + str(lat_dest) + "%2C" + str(
          lon_dest) + "/json?instructionsType=text&routeRepresentation=summaryOnly&computeTravelTimeFor=all&routeType=fastest&traffic=true&avoid=unpavedRoads&travelMode=" + mode + "&key=" + apikey[1]
   getData = urlopen(url).read()
   return json.loads(getData)

    
def json_parsing_steps(routecontent, route, mode):
  
    nstep = len(routecontent[route]['guidance']['instructions'])
    output_step = []
    for step in range(nstep): 
        step_lat         = routecontent[route]['guidance']['instructions'][step]['point']['latitude']
        step_lon         = routecontent[route]['guidance']['instructions'][step]['point']['longitude']
        instruction_type = routecontent[route]['guidance']['instructions'][step]['instructionType']
        try:    
            roadnumber       = routecontent[route]['guidance']['instructions'][step]['roadNumbers']
        except: 
            roadnumber   = "blank"
        street           = routecontent[route]['guidance']['instructions'][step]['street']
        maneuver         = routecontent[route]['guidance']['instructions'][step]['maneuver']
        try:
            turningangle        = routecontent[route]['guidance']['instructions'][step]['turnAngleInDecimalDegrees']
        except: 
            turningangle = 9999
        message          = routecontent[route]['guidance']['instructions'][step]['message']
        new_step_obs = [indexnum, mode, route, step, step_lat, step_lon, instruction_type, roadnumber, street,maneuver, turningangle,  message]
        output_step.append(new_step_obs)
    return output_step
    

def json_parsing(jsonfile, mode):
   
    content    = jsonfile['routes']
    tot_routes = len(content)
    
    output_route = []
    for route in range(tot_routes):
        dist_m          = content[route]['summary']['lengthInMeters']
        traffic_time_s  = content[route]['summary']['liveTrafficIncidentsTravelTimeInSeconds']
        departure_time  = content[route]['summary']['departureTime']
        arrival_time    = content[route]['summary']['arrivalTime']
        notraffic_s     = content[route]['summary']['noTrafficTravelTimeInSeconds']
        hist_traffic_s  = content[route]['summary']['historicTrafficTravelTimeInSeconds']
        traffic_delay_s = content[route]['summary']['trafficDelayInSeconds']
        traffic_delay_m = content[route]['summary']['trafficLengthInMeters']
        new_obs = [indexnum, mode, route, departure_time, arrival_time, dist_m, traffic_delay_s, traffic_delay_m, notraffic_s, hist_traffic_s, traffic_time_s ]
        output_route.append(new_obs)

        # parse step data
        output_step = json_parsing_steps(content, route, mode)

    return  output_route, output_step

# =======================================================================

my_df      = pd.DataFrame([],  columns =["indexnum", "mode", "route", "departure_time", "arrival_time", "dist_m", "traffic_delay_s", "traffic_delay_m", "notraffic_s", "hist_traffic_s", "traffic_time_s"] )
my_df_step = pd.DataFrame([] , columns =["indexnum", "mode", "route", "step", "step_lat", "step_lon", "instruction_type", "roadnumber","street","maneuver", "turningangle", "message"] )


infile = pd.read_csv("us_1k_sample.csv")
counter = 0 
while infile.shape[0] != 0: #while there are trips un-queried 

    now = datetime.now()
    print(now.hour*60 + now.minute)
    
    if (now.hour*60 + now.minute) % 5 != 0:
        time.sleep(60) #sleep 1 min
    else: 
        deptime5 = int((now.hour*60 + now.minute)/5) * 5
        jobs     = infile.loc[infile['deptime5'] == deptime5]
        print(str(jobs.shape[0]) + " trips needs to be queried at deptime " + str(deptime5))
       
        for index, row in jobs.iterrows(): 
            counter += 1
            indexnum = row['indexnum']
            for m in ['truck', 'car']:
                try: 
                    # retrieve json file
                    jsonfile = api_queries(m, row['lat_orig'], row['lon_orig'], row['lat_dest'], row['lon_dest'], apikey[counter%2])
                    
                    try:
                        # parse route and step data
                        output_route, output_step = json_parsing(jsonfile, m)
                        output_route_df   = pd.DataFrame(output_route, columns =["indexnum", "mode", "route", "departure_time", "arrival_time", "dist_m", "traffic_delay_s", "traffic_delay_m", "notraffic_s", "hist_traffic_s", "traffic_time_s"] )
                        output_step_df    = pd.DataFrame(output_step , columns =["indexnum", "mode", "route", "step", "step_lat", "step_lon", "instruction_type", "roadnumber","street","maneuver", "turningangle", "message"] )
                        my_df      = my_df.append(output_route_df)
                        my_df_step = my_df_step.append(output_step_df)
                    except: 
                        print(str(indexnum) + " " + m + "Parsing  Unsuccessful")

                except: 
                    print(str(indexnum) + " " + m +" Unsuccessful")
            # remove the row from infile
            infile = infile.drop(infile[(infile.indexnum == indexnum) & (infile.deptime5 == deptime5)].index)
        
        # Write files to output
        my_df.to_csv(r"output.csv", index=False, header=True)
        my_df_step.to_csv(r"output_step.csv", index=False, header=True)
            
