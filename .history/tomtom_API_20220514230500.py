import json
import sys
import time
import datetime
from urllib.request import urlopen
import csv
import pandas as pd
from datetime import datetime
import time


apikey = ["VFjjgONiaSNpMPCOMRvSmQ4cwRIpPpuA", "s9AazSTPdc04acDYRid2WxqBhc44oWZN", "1Fg5gA8AkajFvFFL4aer2nQdOeyZruYe",
          "zRtUxicG4GUA7t8Rf7Np5eVkWZv39348", "PXhiLGLGEBrfLgfhO0uRt3fG06t4lVlf", "aurBxgI2lhipas4g7XFhNeALbBaJlAWt",
          "gvYGCCG8dZRkbCABaM9gU49jAgiC7qzh", "CxFgRJfOnPDjAGicX3xwXO93CjrCq37u", "tsRhH3qShi8TI4twQY5XqRQhQYBhKfjV",
          "uQt6Or9i7DGTYZ3Ap8QWQr2hOuPH5Vcg", "WBfGxCRAKU9S6pPnGpTuoeEMQp2ZXvC5", "FzlRpUd8PJ3wnQpjTGWPhMpDaADdQmVG",
          "ZpBcELyc8wNLlFZ48aXNf3xbDt0GumA1", "vE7QZ9GTv2MNhvPVs5Lu0qGWtQg9gs78", "n11hwbUs7raXK3NXsW7SUzdPRA0GsJQV",
          "cRxoU0lrstjPXJoW9mqJVRvvbTADujO9", "3Hq5rGxiNFqADoleUlqfrmjtXfAGLEgH", "LTyc0jeeOVcBJbr0tpOnzAkwj6V4Sfnw",
          "hz6nP2t4tgJ5ABGBZPd3nTwcA01XGxsE", "1k3CGnEEC7OE6GiP4XLDyqdYq2v0bt1e"]


def api_queries(mode, lat_orig, lon_orig, lat_dest, lon_dest, api):
    '''
         Testing case
         mode   = "truck"
         [lat_orig, lon_orig, lat_dest, lon_dest] = [
             52.50930, 13.42936, 52.50844, 13.42859]
         [lat_orig, lon_orig, lat_dest, lon_dest] = [
             30.410934, -86.912323, 38.637062, -77.311096]
    '''
    url = "https://api.tomtom.com/routing/1/calculateRoute/" + str(lat_orig) + "%2C" + str(lon_orig) + "%3A" + str(lat_dest) + "%2C" + str(
        lon_dest) + "/json?instructionsType=text&routeRepresentation=summaryOnly&computeTravelTimeFor=all&routeType=fastest&traffic=true&avoid=unpavedRoads&travelMode=" + mode + "&key=" + api
    getData = urlopen(url).read()
    return json.loads(getData)


'''
def json_parsing_steps(routecontent, route, mode):

    nstep = len(routecontent[route]['guidance']['instructions'])
    output_step = []
    for step in range(nstep):
        step_lat = routecontent[route]['guidance']['instructions'][step]['point']['latitude']
        step_lon = routecontent[route]['guidance']['instructions'][step]['point']['longitude']
        instruction_type = routecontent[route]['guidance']['instructions'][step]['instructionType']
        try:
            roadnumber = routecontent[route]['guidance']['instructions'][step]['roadNumbers']
        except:
            roadnumber = "blank"
        street = routecontent[route]['guidance']['instructions'][step]['street']
        maneuver = routecontent[route]['guidance']['instructions'][step]['maneuver']
        try:
            turningangle = routecontent[route]['guidance']['instructions'][step]['turnAngleInDecimalDegrees']
        except:
            turningangle = 9999
        message = routecontent[route]['guidance']['instructions'][step]['message']
        new_step_obs = [indexnum, mode, route, step, step_lat, step_lon,
                        instruction_type, roadnumber, street, maneuver, turningangle,  message]
        output_step.append(new_step_obs)
    return output_step
'''


def json_parsing(jsonfile, mode):

    content = jsonfile['routes']
    tot_routes = len(content)

    output_route = []
    for route in range(tot_routes):
        dist_m = content[route]['summary']['lengthInMeters']
        traffic_time_s = content[route]['summary']['liveTrafficIncidentsTravelTimeInSeconds']
        departure_time = content[route]['summary']['departureTime']
        arrival_time = content[route]['summary']['arrivalTime']
        notraffic_s = content[route]['summary']['noTrafficTravelTimeInSeconds']
        hist_traffic_s = content[route]['summary']['historicTrafficTravelTimeInSeconds']
        traffic_delay_s = content[route]['summary']['trafficDelayInSeconds']
        traffic_delay_m = content[route]['summary']['trafficLengthInMeters']
        new_obs = [indexnum, mode, route, departure_time, arrival_time, dist_m,
                   traffic_delay_s, traffic_delay_m, notraffic_s, hist_traffic_s, traffic_time_s]
        output_route.append(new_obs)

        # parse step data
        '''
        try:
            output_step = json_parsing_steps(content, route, mode)
        except:
            print("Error is here")
        '''
    return output_route
    ''', output_step'''

# =======================================================================


'''
my_df_step = pd.DataFrame([], columns=["indexnum", "mode", "route", "step", "step_lat", "step_lon",
                          "instruction_type", "roadnumber", "street", "maneuver", "turningangle", "message"])
'''

infile = pd.read_csv("test_input.csv")
counter = 0
hours_counter = 0
while hours_counter <= 72:
    my_df = pd.DataFrame([],  columns=["indexnum", "mode", "route", "departure_time", "arrival_time",
                                       "dist_m", "traffic_delay_s", "traffic_delay_m", "notraffic_s", "hist_traffic_s", "traffic_time_s"])
    now = datetime.now()
    print(str(now.hour)+" : "+str(now.minute))
    if now.minute > 0:
        jobs = infile
        for index, row in jobs.iterrows():
            time.sleep(0.5)
            counter += 1
            indexnum = row['indexnum']
            try:
                # retrieve json file
                jsonfile = api_queries(
                    "car", row['lat_orig'], row['lon_orig'], row['lat_dest'], row['lon_dest'], apikey[counter % 20])
                # parse route and step data
                output_route = json_parsing(jsonfile, "car")
                output_route = output_route.append(now.hour)
                output_route_df = pd.DataFrame(output_route, columns=["indexnum", "mode", "route", "departure_time", "arrival_time",
                                               "dist_m", "traffic_delay_s", "traffic_delay_m", "notraffic_s", "hist_traffic_s", "traffic_time_s"])
            except:
                error_list = [row['indexnum'], "ERROR", "ERROR", "ERROR", "ERROR",
                              "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", str(now.hour)]
                output_route_df = pd.DataFrame(error_list, columns=["indexnum", "mode", "route", "departure_time", "arrival_time",
                                               "dist_m", "traffic_delay_s", "traffic_delay_m", "notraffic_s", "hist_traffic_s", "traffic_time_s"])
            my_df = pd.concat([my_df, output_route_df])
            pd.set_option("display.max_rows", None,
                          "display.max_columns", None)
            print(my_df)
            '''
            output_step_df = pd.DataFrame(output_step, columns=[
                "indexnum", "mode", "route", "step", "step_lat", "step_lon", "instruction_type", "roadnumber", "street", "maneuver", "turningangle", "message"])                        
            '''
            '''
            my_df_step = my_df_step.concat(output_step_df)
            '''
        print(str(counter) + " trips have been queried at " + str(now.hour))
        hours_counter += 1
        # Write files to output
        my_df.to_csv(r"output.csv", mode="a", index=False, header=True)
        '''
        my_df_step.to_csv(r"output_step.csv", index=False, header=True)
        '''
    else:
        time.sleep(60)  # sleep 1 min
