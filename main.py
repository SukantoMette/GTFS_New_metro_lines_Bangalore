'''
This main file generates a GTFS (General Transit Feed Specification) dataset for the present and upcoming metro lines in Bangalore.
The dataset includes information on 16 routes across 8 metro lines. The latitude and longitude coordinates for the upcoming metro stations are obtained approximately using Google Maps and the Bangalore Metro Detailed Project Report,
and are stored in separate CSV files in the "stops_data" folder.
The frequency of the metro trains varies throughout the day and along the two routes for the same metro line. This information is stored in "trips time and frequency to.xlsx" and "trips time and frequency fro.xlsx" files in the "frequency_tables" folder.
The fare for the current Bangalore metro lines (Purple and Green lines) is scraped from http://fare.bmrc.co.in/ and is stored in the "fare_scrapped.csv" file.
The fare for the upcoming metro lines is calculated using linear regression between the distance and metro fare. This approach provides better fit by considering the distances along the actual metro network, rather than using the
haversine distance between source and destination stops, where speed of the metro is assumed to be 38 km/hr.

All the files required for the GTFS dataset, including "stops.csv", "route.csv", "trips.csv", "stoptimes.csv", "fare_rule.csv", and "fare_attribute.csv", are stored in the "GTFS_data" folder.
'''

from collections import defaultdict

from GTFS import create_stops_file
from GTFS import create_route_file
from GTFS import create_trips_file
from GTFS import create_stoptimes_file
from GTFS import time_gap

from Fare import add_actual_distance_col
from Fare import add_haversine_distance_col
from Fare import get_old_metro_network
from Fare import linear_regression
from Fare import get_new_metro_network
from Fare import create_fare_files

import pandas as pd




def main():
    # CREATING GTFS
    METRO_SPEED = 38 # km/h
    ROUTE_ID_LIST = ['M_PW', 'M_PC', 'M_GM', 'M_GS', 'M_OJ', 'M_OK', 'M_YR', 'M_YB', 'M_SH', 'M_SK', 'M_RK', 'M_RS', 'M_BS', 'M_BK', 'M_PiK', 'M_PiN']
    METRO_LINE_MAP_TO_METRO_LINE_NAME_DICT = {'M_P': "purple_line",
                                              'M_G': "green_line",
                                              'M_O': "orange_line",
                                              'M_Y': "yellow_line",
                                              'M_S': "silver_line",
                                              'M_R': "red_line",
                                              'M_B': "blue_line",
                                              'M_Pi': "pink_line"}
    STOPS_DATA_PATH = f"./stops_data"
    GTFS_DATA_PATH = f"./GTFS_data"

    FREQUENCY_TABLE_TO_PATH = './frequency_tables/trips time and frequency to.xlsx'
    FREQUENCY_TABLE_FRO_PATH = './frequency_tables/trips time and frequency fro.xlsx'

    len_purple_line, len_green_line, len_orange_line, len_yellow_line, len_silver_line, len_red_line, len_blue_line, len_pink_line = create_stops_file(STOPS_DATA_PATH, GTFS_DATA_PATH)

    create_route_file(GTFS_DATA_PATH, ROUTE_ID_LIST)

    trips_table = defaultdict(list)
    trips_table['trip_id'] = []
    trips_table['route_id'] = []
    trips_table['arrival time'] = []
    trips_txt = pd.DataFrame.from_dict(trips_table)

    stop_times_txt = defaultdict(list)

    start_point_of_trip_file = 0

    for route_id in ROUTE_ID_LIST:
        if route_id in ROUTE_ID_LIST[:len(ROUTE_ID_LIST):2]:
            trips_frequency_table = pd.read_excel(FREQUENCY_TABLE_TO_PATH)
            metro_line_id = route_id[:-1]
            consecutive_station_time_difference = time_gap(stops_data_path=STOPS_DATA_PATH, metro_name=METRO_LINE_MAP_TO_METRO_LINE_NAME_DICT[metro_line_id], metro_speed=METRO_SPEED, reverse=0)

        else:
            trips_frequency_table = pd.read_excel(FREQUENCY_TABLE_FRO_PATH)
            metro_line_id = route_id[:-1]
            consecutive_station_time_difference = time_gap(stops_data_path=STOPS_DATA_PATH, metro_name=METRO_LINE_MAP_TO_METRO_LINE_NAME_DICT[metro_line_id], metro_speed=METRO_SPEED, reverse=1)

        trips_txt = pd.concat([trips_txt, create_trips_file(trips_frequency_table, route_id)], ignore_index=True)

        create_stoptimes_file(stop_times_txt,
                              trips_table=trips_txt,
                              line_id_str=metro_line_id,
                              route_id=route_id,
                              metro_line_time_difference_between_stops=consecutive_station_time_difference,
                              start_point_of_trip_file=start_point_of_trip_file,
                              route_id_list=ROUTE_ID_LIST)
        start_point_of_trip_file = trips_txt.shape[0]


    stop_times_txt = pd.DataFrame.from_dict(stop_times_txt)
    stop_times_txt['departure_time'] = stop_times_txt['arrival_time']

    trips_txt = trips_txt.drop(columns='arrival time')

    trips_txt.to_csv(f'{GTFS_DATA_PATH}/trips.csv', index=False)
    stop_times_txt.to_csv(f'{GTFS_DATA_PATH}/stoptimes.csv', index=False)

    # CREATING FARE FILES
    stops_df = pd.read_csv(f"{GTFS_DATA_PATH}/stops.csv")

    scrapped_fare_df = pd.read_csv("fare_scrapped.csv")
    scrapped_fare_df, stop_dict = add_haversine_distance_col(scrapped_fare_df, stops_df, len_purple_line, len_green_line)
    G_old_metro_network = get_old_metro_network(stops_df, len_purple_line, len_green_line)
    scrapped_fare_df = add_actual_distance_col(scrapped_fare_df, stop_dict, G_old_metro_network)
    slope, intercept = linear_regression(scrapped_fare_df)
    G_new_metro_network = get_new_metro_network(stops_df, len_purple_line, len_green_line, len_orange_line, len_yellow_line, len_silver_line, len_red_line, len_blue_line, len_pink_line)

    fare_rule_df, fare_attribute_df = create_fare_files(stops_df, scrapped_fare_df, G_new_metro_network, slope, intercept)

    fare_rule_df.to_csv(f"{GTFS_DATA_PATH}/fare_rule.csv", index=False)
    fare_attribute_df.to_csv(f"{GTFS_DATA_PATH}/fare_attribute.csv", index=False)




if __name__ == "__main__":
    main()