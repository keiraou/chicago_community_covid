'''
This module cleans raw data
'''

import data_collect
import pandas as pd
import re
import datetime
pd.set_option('mode.chained_assignment', None)


DATASET_DICT = data_collect.get_dataportal_api_data()
COL_DROP = [":@computed_region_rpca_8um6",
            ":@computed_region_vrxf_vc4k",
            ":@computed_region_6mkv_f3dw",
            ":@computed_region_bdys_3d7i",
            ":@computed_region_43wa_7qmu"]


def clean_covid_case_num():
    '''
    Clean covid_case_num data from Chicago Data Portal API

    Output:
        covid_case_num: pandas DataFrame of cleaned covid_case_num
    '''

    covid_case_num = DATASET_DICT["covid_case_num"]
    covid_case_num["week_end"] = pd.to_datetime(covid_case_num["week_end"])
    
    covid_case_num.drop(["week_start", "zip_code_location"] + COL_DROP,
                    axis = 1, inplace = True)
    
    return covid_case_num


def clean_covid_vaccination_num():
    '''
    Clean covid_vaccination_num data from Chicago Data Portal API

    Output:
        covid_vaccination_num: pandas DataFrame of cleaned covid_vaccination_num
    '''

    covid_vaccination = DATASET_DICT["covid_vaccination_num"]
    covid_vaccination["date"] = pd.to_datetime(covid_vaccination["date"])
    covid_vaccination.drop(["zip_code_location"] + COL_DROP,
                                axis = 1, inplace = True)

    return covid_vaccination


def clean_covid_vaccination_sites():
    '''
    Clean covid_vaccination_site data from Chicago Data Portal API

    Output:
        covid_vaccination_sites: pandas DataFrame of covid_vaccination_sites
    '''
    covid_vaccination_sites = DATASET_DICT["covid_vaccination_sites"]
    covid_vaccination_sites = covid_vaccination_sites.\
        loc[:, ["facility_name","postal_code"]]

    return covid_vaccination_sites


def clean_population():
    '''
    Clean population data from Chicago Data Portal API

    Output:
        population: pandas DataFrame of cleaned population data
    '''
    population = DATASET_DICT["population"]
    population = population[population.year == '2019']
    population.rename(columns = {"geography": "zip_code"}, inplace = True)
    
    population.drop(["geography_type", "year", "record_id"],
                     axis = 1, inplace = True)

    pop_filter = [x for x in population.columns if 
                    not x.endswith(("nx", "_non"))]
    

    return population[pop_filter]


def clean_health_centers():
    '''
    Clean data health_centers from Chicago Data Portal API

    Output:
        health_centers: pandas DataFrame of cleaned health_centers data
    '''

    health_centers = DATASET_DICT["health_centers"]
    health_centers.drop([":@computed_region_awaf_s7ux"] + COL_DROP, 
                         axis = 1, inplace = True)

    health_centers["location_1"] = health_centers["location_1"].apply(str)
    health_centers["zip_code"] = health_centers.location_1. \
                                apply(lambda x: extract_zip(x))
                                
    health_centers.drop(["location_1"], axis = 1, inplace = True)

    return health_centers


def extract_zip(string):
    '''
    Extracts zip code from health_center.location_1
    '''
    return re.findall(".*\"zip\":\s+\"(.*)\"", string)[0]
