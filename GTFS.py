'''
This file contain functions used for creating the GTFS data set apart from the fare files.
'''



from collections import defaultdict

import datetime as dt
import numpy as np
import pandas as pd
import haversine as hs
import math


def create_stops_file(stops_data_path: str, GTFS_data_path: str):
    '''
    This function generates the "stops.csv" file for a GTFS dataset. Each stop on a metro line is assigned a unique identifier called "stop_id".
    The format of a stop_id consists of three parts: the mode of transport (here metro), the first letter of the line name, and a sequence number.
    stop_id = {mode_of_transport}_{first_letter_of_line_name}_{sequence}
    This ensures that each stop has a unique identifier within the dataset.

    Args:
        stops_data_path (str): path of folder where all the metro line csv file is present, contaning stop_name, stop_latitude and stop_longitude.
        GTFS_data_path (str): path of folder where all created GTFS files are stored.

    Returns:
        purple_line_df.shape[0] (int): number of stops in purple line.
        green_line_df.shape[0] (int): number of stops in green line.
        orange_line_df.shape[0] (int): number of stops in orange line.
        yellow_line_df.shape[0] (int): number of stops in yellow line.
        silver_line_df.shape[0] (int): number of stops in silver line.
        red_line_df.shape[0] (int): number of stops in red line.
        blue_line_df.shape[0] (int): number of stops in blue line.
        pink_line_df.shape[0] (int): number of stops in pink line.


    '''
    green_line_df = pd.read_csv(f"{stops_data_path}/green_line.csv")
    purple_line_df = pd.read_csv(f"{stops_data_path}/purple_line.csv")
    initial_stop_id = 100
    purple_line_stop_id = []
    green_line_stop_id = []
    for x in range(purple_line_df.shape[0]):
        purple_line_stop_id.append(initial_stop_id)
        initial_stop_id += 1
    for x in range(green_line_df.shape[0]):
        green_line_stop_id.append(initial_stop_id)
        initial_stop_id += 1
    stops_txt = defaultdict(list)

    stops_txt['stop_id'] = [100+x for x in range(purple_line_df.shape[0] + green_line_df.shape[0])]

    stops_txt['stop_name'] = list(purple_line_df["stop_name"]) + list(green_line_df["stop_name"])

    stops_txt['stop_lat'] = list(purple_line_df["lat"]) + list(green_line_df["lat"])

    stops_txt['stop_lon'] = list(purple_line_df["lon"]) + list(green_line_df["lon"])
    stops_txt['zone_id'] = [100+x for x in range(purple_line_df.shape[0] + green_line_df.shape[0])]
    stops_txt = pd.DataFrame.from_dict(stops_txt)
    stops_txt = stops_txt[['stop_id', 'stop_lat', 'stop_lon', 'stop_name', 'zone_id']]

    stops_txt.to_csv(f'{GTFS_data_path}/stops.csv', index=False)

    return purple_line_stop_id, green_line_stop_id

def create_route_file(GTFS_data_path, route_id_list):
    '''
    This function generates the "route.csv" file for a GTFS dataset. Each metro line in the dataset has two route identifiers that correspond to the two directions of travel along the line.
    The route_id is a combination of three parts: the mode of travel (here metro), the first letter of the line name, and the first letter of the first stop in one direction of the line.
    route_id = {mode of travel}_{first_letter_of_line_name}{first_letter_of_first_stop_in_one_direction}.

    Args:
        GTFS_data_path (str): path of folder where all created GTFS files are stored.
        route_id_list (list): list of route_id for all 8 metro lines, resulting in 16 route_ids.

    Returns:
        None

    '''

    routes_dict = defaultdict(list)

    routes_dict['route_id'] = route_id_list
    routes_dict['route_short_name'] = ['Metro Purple Whitefield',
                                       'Metro Purple Challaghatta',
                                       'Metro Green Madavara',
                                       'Metro Green Silk Institute']
    routes_dict['route_long_name'] = ['Metro Purple Whitefield to Challaghatta',
                                      'Metro Purple Challaghatta to Whitefield',
                                      'Metro Green Madavara to Silk Institute',
                                      'Metro Green Silk Institute to Madavara']
    routes_dict['route_desc'] = [-1] * 4
    routes_dict['route_type'] = [1] * 4
    routes_dict['agency_id'] = ['BMRCL'] * 4
    route_txt = pd.DataFrame.from_dict(routes_dict)
    route_txt = route_txt[['route_id', 'route_short_name', 'route_long_name', 'route_desc', 'route_type', 'agency_id']]

    route_txt.to_csv(f'{GTFS_data_path}/route.csv', index=False)

    return


def create_trips_file(trips_frequency_table, route_id_str, trip_id_start):
    '''
        This function is used to create the trips table which is later used as input for another function(create_stoptimes_file) and is also used to create trips.csv file for GTFS dataset.
        This function calculate the number of trains required for each time slot for a given frequency in that time slot and then finding the arrival time of that trip.
        trip_id denotes a sequence of stops that occur during a specific time period (here a day), number of trips on a particular route is the total number of trains required in that time period.
        trip_id = {route_id}_{order}, where order = 1,2,3,...total_number_of_trains.

        Args :
            trips_frequency_table (pandas.DataFrame): containing frequency of metro line for different time slot of the day.
            route_id_str (str): Denotes the route_id of metro_line in a specific direction.

        Returns :
            trips_table (pandas.Dataframe): A DataFrame containing trip_id, route_id and arrival time

    '''

    # making necessary column additions to the trip frequeny DataFrame

    trips_frequency_table['frequency'] = trips_frequency_table['frequency'].apply(lambda x: dt.timedelta(minutes=x))
    trips_frequency_table['end time'] = trips_frequency_table['end time'].apply(lambda x: dt.datetime.combine(dt.date.today(), x))
    trips_frequency_table['start time'] = trips_frequency_table['start time'].apply(lambda x: dt.datetime.combine(dt.date.today(), x))

    trips_frequency_table['time difference'] = trips_frequency_table['end time'] - trips_frequency_table['start time']
    trips_frequency_table['number of trains'] = np.ceil(trips_frequency_table['time difference'] / trips_frequency_table['frequency'])

    trips_frequency_table['number of trains'] = trips_frequency_table['number of trains'].astype('int64')

    # Creating dictionary trips_table, which after making changes will be converted to DataFrame

    trips_table = defaultdict(list)
    index_count = 0

    # adding necessary values inside the columns

    for row in trips_frequency_table.itertuples():

        start_time = row[1]
        curr_index = index_count

        for _ in range(curr_index, row[5] + curr_index):
            trips_table['trip_id'].append(int(trip_id_start))
            trip_id_start += 1
            trips_table['route_id'].append(int(route_id_str))
            trips_table['arrival time'].append(start_time)
            start_time = start_time + row[3]
            index_count += 1

    trips_table = pd.DataFrame.from_dict(trips_table)

    return trips_table, trip_id_start


def create_stoptimes_file(stop_times_txt, trips_table: pd.DataFrame, line_id_str: str,route_id: str, metro_line_time_difference_between_stops: list, start_point_of_trip_file: int, route_id_list: list, route_id_stop_dict):
    """
        This Function is used to create the stopstimes.txt file

        Args :
            trips_table : DataFrame gotten from create_trips_file function
            line_id_str : String containing the metro line initial, used for naming purposes
            metro_line_time_diiference_between_stops : A list constaining the time difference between consecutive stops

        Returns :
            stop_times_txt : A DataFrame which will be converted to stoptimes.txt file

    """

    # making necessary changes to the time difference list
    metro_line_time_difference_between_stops.append(0)
    metro_line_time_difference_between_stops = [dt.timedelta(minutes=val) for val in metro_line_time_difference_between_stops]

    # Filling the stop times dictionary with relevant data and converting it to DataFrame

    for row in range(start_point_of_trip_file, trips_table.shape[0]):

        arrival_time = trips_table["arrival time"].iloc[row]

        for index in range(len(metro_line_time_difference_between_stops)):
            stop_times_txt['trip_id'].append(int(trips_table["trip_id"].iloc[row]))
            stop_times_txt['arrival_time'].append(arrival_time)
            arrival_time = arrival_time + metro_line_time_difference_between_stops[index]
            stop_times_txt['stop_id'].append(route_id_stop_dict[route_id][index])
            stop_times_txt['stop_sequence'].append(index)
    # routes_dict['route_id'] = ['PW', 'PC', 'GM', 'GS', 'OJ', 'OK', 'YR', 'YB', 'SH', 'SK', 'RK', 'RS', 'BS', 'BK', 'PiK', 'PiN']


def time_gap(stops_data_path, metro_name, metro_speed, reverse):
    df = pd.read_csv(f"{stops_data_path}/{metro_name}.csv")
    names = list(df["stop_name"])
    lat = list(df['lat'])
    lon = list(df['lon'])
    dis = []
    for i in range(1, len(names)):
        dis.append(hs.haversine((lat[i-1], lon[i-1]), (lat[i], lon[i])))

    time_gap = [math.ceil((x/metro_speed)*60) for x in dis]

    if reverse:
        return time_gap
    else:
        return time_gap[::-1]
