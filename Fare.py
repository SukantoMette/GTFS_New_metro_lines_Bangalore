import pandas as pd
import haversine as hs
import networkx as nx

from scipy import stats
from haversine import Unit



def add_haversine_distance_col(scrapped_fare_df, stops_df, len_purple_line, len_green_line):
    stop_dict = {stops_df["stop_name"].iloc[row]: [stops_df["stop_id"].iloc[row], (stops_df["stop_lat"].iloc[row], stops_df["stop_lon"].iloc[row])] for row in range(0, len_purple_line+len_green_line)}

    haversine_dis = []
    for row in range(scrapped_fare_df.shape[0]):
        loc1 = stop_dict[scrapped_fare_df["source_stop"].iloc[row]][1]
        loc2 = stop_dict[scrapped_fare_df["destination_stop"].iloc[row]][1]
        haversine_dis.append(hs.haversine(loc1, loc2, unit=Unit.METERS))

    scrapped_fare_df["haversine_distance"] = haversine_dis

    return scrapped_fare_df, stop_dict


def get_old_metro_network(stops_df, len_purple_line, len_green_line):
    stop_dict = {stops_df["stop_id"].iloc[row]: (stops_df["stop_lat"].iloc[row], stops_df["stop_lon"].iloc[row]) for row in range(0, len_purple_line + len_green_line)}

    purple_line_stop_ids = list(stops_df["stop_id"].iloc[: len_purple_line])
    green_line_stop_ids = list(stops_df["stop_id"].iloc[len_purple_line : len_purple_line + len_green_line])

    g = nx.Graph()
    g.add_nodes_from(purple_line_stop_ids + green_line_stop_ids)

    g.add_edges_from([(purple_line_stop_ids[x-1], purple_line_stop_ids[x], {'weight': hs.haversine(stop_dict[purple_line_stop_ids[x-1]], stop_dict[purple_line_stop_ids[x]], unit=Unit.METERS)}) for x in range(1, len(purple_line_stop_ids))])
    g.add_edges_from([(green_line_stop_ids[x-1], green_line_stop_ids[x], {'weight': hs.haversine(stop_dict[green_line_stop_ids[x-1]], stop_dict[green_line_stop_ids[x]], unit=Unit.METERS)}) for x in range(1, len(green_line_stop_ids))])

    g.add_edges_from([('M_P_23', 'M_G_17', {'weight': 0})])

    return g


def add_actual_distance_col(scrapped_fare_df, stop_dict, G):
    actual_distance = []
    for row in range(scrapped_fare_df.shape[0]):
        actual_distance.append(nx.shortest_path_length(G, source=stop_dict[scrapped_fare_df["source_stop"].iloc[row]][0], target=stop_dict[scrapped_fare_df["destination_stop"].iloc[row]][0], weight='weight', method='dijkstra'))

    scrapped_fare_df["actual_distance"] = actual_distance

    return scrapped_fare_df

def linear_regression(scrapped_fare_df):
    haversine_distance = list(scrapped_fare_df["haversine_distance"])
    actual_distance = list(scrapped_fare_df["actual_distance"])
    fare = list(scrapped_fare_df["fare"])

    slope_haversine, intercept_haversine, r_haversine, p_haversine, std_err_haversine = stats.linregress(haversine_distance, fare)
    slope_actual, intercept_actual, r_actual, p_actual, std_err_actual = stats.linregress(actual_distance, fare)

    if std_err_haversine < std_err_actual:
        return slope_haversine, intercept_haversine
    else:
        return slope_actual, intercept_actual


def get_new_metro_network(stops_df, len_purple_line, len_green_line, len_orange_line, len_yellow_line, len_silver_line, len_red_line, len_blue_line, len_pink_line):
    stop_dict = {stops_df["stop_id"].iloc[row] : (stops_df["stop_lat"].iloc[row], stops_df["stop_lon"].iloc[row]) for row in range(stops_df.shape[0])}

    purple_line_stop_ids = list(stops_df["stop_id"].iloc[: len_purple_line])
    green_line_stop_ids = list(stops_df["stop_id"].iloc[(len_purple_line):(len_purple_line + len_green_line)])
    orange_line_stop_ids = list(stops_df["stop_id"].iloc[(len_purple_line + len_green_line):(len_purple_line + len_green_line + len_orange_line)])
    yellow_line_stop_ids = list(stops_df["stop_id"].iloc[(len_purple_line + len_green_line + len_orange_line):(len_purple_line + len_green_line + len_orange_line + len_yellow_line)])
    silver_line_stop_ids = list(stops_df["stop_id"].iloc[(len_purple_line + len_green_line + len_orange_line + len_yellow_line):(len_purple_line + len_green_line + len_orange_line + len_yellow_line + len_silver_line)])
    red_line_stop_ids = list(stops_df["stop_id"].iloc[(len_purple_line + len_green_line + len_orange_line + len_yellow_line + len_silver_line):(len_purple_line + len_green_line + len_orange_line + len_yellow_line + len_silver_line + len_red_line)])
    blue_line_stop_ids = list(stops_df["stop_id"].iloc[(len_purple_line + len_green_line + len_orange_line + len_yellow_line + len_silver_line + len_red_line):(len_purple_line + len_green_line + len_orange_line + len_yellow_line + len_silver_line + len_red_line + len_blue_line)])
    pink_line_stop_ids = list(stops_df["stop_id"].iloc[(len_purple_line + len_green_line + len_orange_line + len_yellow_line + len_silver_line + len_red_line + len_blue_line):(len_purple_line + len_green_line + len_orange_line + len_yellow_line + len_silver_line + len_red_line + len_blue_line + len_pink_line)])

    g = nx.Graph()
    g.add_nodes_from(purple_line_stop_ids + green_line_stop_ids + orange_line_stop_ids + yellow_line_stop_ids + silver_line_stop_ids + red_line_stop_ids + blue_line_stop_ids + pink_line_stop_ids)

    g.add_edges_from([(purple_line_stop_ids[x-1], purple_line_stop_ids[x], {'weight': hs.haversine(stop_dict[purple_line_stop_ids[x-1]], stop_dict[purple_line_stop_ids[x]], unit=Unit.METERS)}) for x in range(1, len(purple_line_stop_ids))])
    g.add_edges_from([(green_line_stop_ids[x-1], green_line_stop_ids[x], {'weight': hs.haversine(stop_dict[green_line_stop_ids[x-1]], stop_dict[green_line_stop_ids[x]], unit=Unit.METERS)}) for x in range(1, len(green_line_stop_ids))])
    g.add_edges_from([(orange_line_stop_ids[x-1], orange_line_stop_ids[x], {'weight': hs.haversine(stop_dict[orange_line_stop_ids[x-1]], stop_dict[orange_line_stop_ids[x]], unit=Unit.METERS)}) for x in range(1, len(orange_line_stop_ids))])
    g.add_edges_from([(yellow_line_stop_ids[x-1], yellow_line_stop_ids[x], {'weight': hs.haversine(stop_dict[yellow_line_stop_ids[x-1]], stop_dict[yellow_line_stop_ids[x]], unit=Unit.METERS)}) for x in range(1, len(yellow_line_stop_ids))])
    g.add_edges_from([(silver_line_stop_ids[x-1], silver_line_stop_ids[x], {'weight': hs.haversine(stop_dict[silver_line_stop_ids[x-1]], stop_dict[silver_line_stop_ids[x]], unit=Unit.METERS)}) for x in range(1, len(silver_line_stop_ids))])
    g.add_edges_from([(red_line_stop_ids[x-1], red_line_stop_ids[x], {'weight': hs.haversine(stop_dict[red_line_stop_ids[x-1]], stop_dict[red_line_stop_ids[x]], unit=Unit.METERS)}) for x in range(1, len(red_line_stop_ids))])
    g.add_edges_from([(blue_line_stop_ids[x-1], blue_line_stop_ids[x], {'weight': hs.haversine(stop_dict[blue_line_stop_ids[x-1]], stop_dict[blue_line_stop_ids[x]], unit=Unit.METERS)}) for x in range(1, len(blue_line_stop_ids))])
    g.add_edges_from([(pink_line_stop_ids[x-1], pink_line_stop_ids[x], {'weight': hs.haversine(stop_dict[pink_line_stop_ids[x-1]], stop_dict[pink_line_stop_ids[x]], unit=Unit.METERS)}) for x in range(1, len(pink_line_stop_ids))])

    g.add_edges_from([('M_P_30', 'M_O_8', {'weight': 0}), ('M_P_23', 'M_G_17', {'weight': 0}), ('M_P_22', 'M_R_8', {'weight': 0}), ('M_P_19', 'M_Pi_11', {'weight': 0}), ('M_P_12', 'M_B_13', {'weight': 0}), ('M_P_26', 'M_S_1', {'weight': 0})])
    g.add_edges_from([('M_G_26', 'M_O_3', {'weight': 0}), ('M_G_24', 'M_Y_1', {'weight': 0}), ('M_G_8', 'M_O_17', {'weight': 0})])
    g.add_edges_from([('M_O_1', 'M_Pi_4', {'weight': 0}), ('M_O_22', 'M_R_1', {'weight': 0}), ('M_O_22', 'M_B_22', {'weight': 0}), ('M_O_13', 'M_S_4', {'weight': 0})])
    g.add_edges_from([('M_Y_3', 'M_Pi_5,', {'weight': 0}), ('M_Y_5', 'M_B_1,', {'weight': 0})])
    g.add_edges_from([('M_R_18', 'M_B_4', {'weight': 0}), ('M_R_17', 'M_B_3', {'weight': 0}), ('M_R_12', 'M_Pi_7', {'weight': 0}), ('M_R_1', 'M_B_22', {'weight': 0})])
    g.add_edges_from([('M_B_20', 'M_Pi_18', {'weight': 0})])

    return g

def create_fare_files(stops_df, scrapped_fare_df, G, slope, intercept):
    stop_id_name_dict = {stops_df["stop_id"].iloc[row]: stops_df["stop_name"].iloc[row] for row in range(stops_df.shape[0])}
    actual_fare_dict = {(scrapped_fare_df["source_stop"].iloc[row], scrapped_fare_df["destination_stop"].iloc[row]): scrapped_fare_df["fare"].iloc[row] for row in range(scrapped_fare_df.shape[0])}

    stop_ids_list = list(stops_df["stop_id"])
    fare_id = []
    origin_id = []
    destination_id = []
    cost_li = []
    fare_id_index = 1
    for source in range(len(stop_ids_list)):
        for destination in range(len(stop_ids_list)):
            if stop_ids_list[source] != stop_ids_list[destination]:
                distance = nx.shortest_path_length(G, source=stop_ids_list[source], target=stop_ids_list[destination],weight='weight', method='dijkstra')
                fare = round((slope * distance) + intercept, 0)
                fare_id.append(f'M_F_{fare_id_index}')
                fare_id_index += 1
                cost_li.append(actual_fare_dict.get((stop_id_name_dict[stop_ids_list[source]], stop_id_name_dict[stop_ids_list[destination]]), fare))
                origin_id.append(stop_ids_list[source])
                destination_id.append(stop_ids_list[destination])

    fare_rule_df = pd.DataFrame(list(zip(fare_id, origin_id, destination_id)), columns=['fare_id', 'origin_id', 'destination_id'])
    fare_attribute_df = pd.DataFrame(list(zip(fare_id, cost_li)), columns=['fare_id', 'fare'])

    return fare_rule_df, fare_attribute_df

