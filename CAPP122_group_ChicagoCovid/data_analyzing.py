from math import radians, cos, sin, asin, sqrt, ceil
import pandas as pd


def find_neighbors(coor, covid, zip1, k):
    '''
    Given a Chicago zip code and an integer k,
    find the k nearest neighbours around.

    Inputs:
        coor: a pandas dataframe that maps zipcodes to coordinates
        covid: a pandas dataframe maps zipcodes with other variables
        zip1: int, the zip code area that the user cares about
        k: int, the number of neighbours around to compare
    Returns:
        A list that includes all the k nearest neighbours zip codes.
        If the zip code area is not included in the covid database,
        use the first neighbor that has been recorded in the database
        as prediction for the zip code, and count k from that one.
    '''

    if zip1 not in coor['Zip'].values:
        raise RuntimeError("zipcode not in Chicago")

    lat1 = coor.loc[coor.Zip == zip1, 'Latitude'].values[0]
    lon1 = coor.loc[coor.Zip == zip1, 'Longitude'].values[0]
    coor['distance'] = coor.apply(lambda x: haversine(lon1, \
                                  lat1, x[2], x[1]), axis=1)
    coor = coor.rename(columns = {'Zip': 'zip_code'}).drop(\
                        ['Latitude','Longitude'], axis=1)
    covid = pd.merge(covid, coor, on='zip_code', how='left')

    covid = covid.sort_values('distance')
    sort_neighbor = list(covid['zip_code'].values)
    if zip1 in covid['zip_code'].values:
        sort_neighbor.remove(zip1)
    return sort_neighbor[: k]


def compare_to_neighbors(zip, k, var):
    '''
    Compare the zip code area's variable values with
    k-neighbors' variable values.

    Inputs:
        zip: int, the zip code area that the user inputs
        k: int, the number of neighbours around to compare
        var: the output variable users would like to compare on
    Returns:
        a dictionary that maps a calculated variable to a
        dictionary that contains "weight" and "value" as
        two keys corresponding to two dictionaries that map
        zipcode area and k-neighbors to their results.
    '''

    coor = pd.read_csv("rawdata/chicago-zip-code-latitude-and-longitude.csv",
                        sep='\t')
    covid = pd.read_csv("databases/cross_section_database 2021-03-15.csv")

    neigh_zips = find_neighbors(coor, covid, zip, k)
    neigh_mask = covid['zip_code'].isin(neigh_zips)
    neigh_df = covid[neigh_mask]

    if zip not in covid['zip_code'].values:
        zip = neigh_zips[0]

    inp = covid.loc[covid.zip_code == zip]
    inp_weight = inp[var].values[0] / inp['population'].values[0]
    sum_pop = sum(neigh_df['population'])
    sum_col = sum(neigh_df.loc[:, var])
    nei_weight = sum_col/sum_pop
    result1 = compare_result(inp_weight, inp_weight)

    inp_val = covid.loc[covid.zip_code == zip, var].values[0]
    weight = neigh_df['population']/sum_pop
    nei_val = sum(neigh_df.loc[:, var] * weight)
    result2 = compare_result(inp_val, nei_val)

    dic = {}
    dic[var] = {"weight": {zip: round(inp_weight, 2),
                "neighbor": round(nei_weight, 2), "result": result1},
                "value": {zip: round(inp_val, 2),
                    "neighbor": round(nei_val, 2), "result": result2}}
    return dic


def compare_result(val1, val2):
    '''
    Compare two floats.

    Inputs:
        val1, val2: float
    Returns: string indicating the comparison result
    '''
    epsilon = 1e-9

    if val1 < val2:
        result = "below"
    elif val1 > val2:
        result = "above"
    elif abs(val1 - val2) < epsilon:
        result = "equal to"
    return result


def haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the circle distance between two points
    on the earth (specified in decimal degrees)

    Inputs:
        lon1, lat1, lon2, lat2: coordinates of two points on earth
    Returns:
        distance between two points
    '''

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    km = 6367 * c
    return km