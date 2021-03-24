'''
This module collects raw data from APIs

Data Sources:
    Chicago Data Portal API
    Chicago Health Atlas API
    City Health Dashboard API
'''

import csv
import ssl
import urllib.request
import pandas as pd
import requests
from sodapy import Socrata


def get_dataportal_api_data():
    '''
    Collects data from Chicago Data Portal API

    Output:
        dataset_dict: a dictionary mapping table_name
                      to the relevantpandas Dataframe
    '''
    client = Socrata("data.cityofchicago.org",
                    "BxWCnzf8952oHnxHDXohAdBSQ",
                    "API EMAIL ACCOUNT", ##need replace
                    "API KEYWORD")  ##need replace

    dataset_id = {
        "covid_case_num": "yhhz-zm2v",
        "covid_vaccination_num": "553k-3xzc",
        "covid_vaccination_sites": "6q3z-9maq",
        "population": "85cm-7uqa",
        "health_centers": "cjg8-dbka"}

    dataset_dict = {}
    for filename, set_id in dataset_id.items():
        request = client.get(set_id)
        df = pd.DataFrame.from_records(request)
        dataset_dict[filename] = df
        dataframe_to_csv(df, filename)

    return dataset_dict


def get_hospital_data():
    '''
    Collects hospital data from Chicago Health Atlas API

    Output:
        df: pandas DataFrame of Chicago hospital information
    '''
    url = "https://api.chicagohealthatlas.org/api/v1/hospitals"
    response = requests.get(url)
    dictr = response.json()
    df = pd.json_normalize(dictr)
    filename = "hospital"
    dataframe_to_csv(df, filename)
    return df


def get_health_indicator_data():
    '''
    Collects health indicator data from City Health Dashboard API

    Output:
        df: pandas DataFrame of Chicago health indicators
    '''
    indicator_yr = [
        ("children-in-poverty","2017,+5+Year+Estimate"),
        ("dental-care","2016,+1+Year+Modeled+Estimate"),
        ("diabetes","2017,+1+Year+Modeled+Estimate"),
        ("frequent-mental-distress","2016,+1+Year+Modeled+Estimate"),
        ("frequent-physical-distress","2016,+1+Year+Modeled+Estimate"),
        ("housing-cost-excessive","2017,+5+Year+Estimate"),
        ("income-inequality","2017,+5+Year+Estimate"),
        ("life-expectancy", "2010-2015,+6+Year+Modeled+Estimate"),
        ("obesity", "2016,+1+Year+Modeled+Estimate"),
        ("uninsured","2017,+5+Year+Estimate"),
        ("preventive-services", "2016,+1+Year+Modeled+Estimate")
    ]

    df = request_cityhealth_api_data(indicator_yr[0][0],
                                     indicator_yr[0][1])

    for indicator, data_yr_type in indicator_yr[1:]:
        indicator_df = request_cityhealth_api_data(indicator, data_yr_type)
        df = df.merge(indicator_df, on="geoid")

    map_df = get_geoid_zipcode_map()
    df = df.merge(map_df, on="geoid")

    col_rename = {"children-in-poverty":"children_in_poverty",
                  "dental-care":"dental_care",
                  "frequent-mental-distress":"frequent_mental_distress",
                  "frequent-physical-distress":"frequent_physical_distress",
                  "housing-cost-excessive":"housing_cost_excessive",
                  "income-inequality":"income_inequality",
                  "life-expectancy":"life_expectancy",
                  "preventive-services":"preventive_services"}
    df.rename(columns = col_rename, inplace = True)
    filename = "health_indicator_tract"
    dataframe_to_csv(df, filename)

    return df


def request_cityhealth_api_data(indicator, data_yr_type):
    '''
    Request data from City Health Dashboard API
    based on specific indicator name and data_yr_type

    Input:
        indicator: str, name of indicator
        data_yr_type: str, the year of the data source
    Output:
        indicator_df: pandas DataFrame, tract level data based on 
                      indicator input and data_yr_type
    '''
    end_point = "api.cityhealthdashboard.com/api/data/tract-metric/"
    loc_filter = "&city_name=Chicago&state_abbr=IL"
    api_key = "API KEY" ## replace with API key

    request_str = "https://{}{}?" + \
                  "token={}{}&data_yr_type={}"
    request_str = \
        request_str.format(end_point, indicator, api_key, loc_filter, data_yr_type)
    request_json = requests.get(request_str)
    indicator_dict = request_json.json()

    indicator_value = {"geoid":[], indicator:[]}
    for row in indicator_dict["rows"]:
        geoid = row["stcotr_fips"]
        indicator_value["geoid"].append(str(geoid))
        value = row["est"]
        indicator_value[indicator].append(value)

    indicator_df = pd.DataFrame(indicator_value)
    return indicator_df


def get_geoid_zipcode_map():
    '''
    Get the dataframe mapping the geoid to zipcode
    Source: census.gov

    Output:
        map_df: pandas Dataframe mapping the geoid to zipcode
    '''
    url = \
    "https://www2.census.gov/geo/docs/maps-data/data/rel/zcta_tract_rel_10.txt"
    ssl._create_default_https_context = ssl._create_unverified_context
    df = pd.read_csv(url, sep=",", dtype=str)
    map_df = df.drop(df[df['STATE'] != '17'].index)
    map_df = map_df.loc[:, ["ZCTA5","GEOID"]]
    map_df.rename(columns = {"ZCTA5": "zip_code",
                              "GEOID": "geoid"},
                  inplace = True)
    return map_df


def dataframe_to_csv(dataframe, filename):
    '''
    Converts Pandas Dataframe to csv file

    Input:
        dataframe: pandas DataFrame object
        filename: str
    Output:
        a CSV file
    '''
    path = "" + filename + ".csv" ## replace with actual path
    dataframe.to_csv(path)


def main():
    print ("Collecting all raw data.")
    get_dataportal_api_data()
    get_hospital_data()
    get_health_indicator_data()
    print ("Raw data is ready.")


if __name__ == "__main__":
    main()
