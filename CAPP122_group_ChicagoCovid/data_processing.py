import numpy as np
import pandas as pd
import re
import datetime

def summarise_by_zip_latest(data, zip_name, time_ind):
    """Gets the row corresponding to the latest week available by zip code

    Args:
        data (Pandas DataFrame): DataFrame to filter
        zip_name (str): Name of the column containing zip codes
        time_ind (str): Name of the column containig time information

    Returns:
        Pandas DataFrame
    """

    if not isinstance(data[zip_name][0], str):
        data[zip_name] = data[zip_name].apply(str)

    return data.groupby(zip_name).max(time_ind)

##### Processing Weekly case numbers
covid_case_num = pd.read_csv("rawdata/covid_case_num.csv", index_col = 0)

# Time Structure
covid_case_num["week_end"] = pd.to_datetime(covid_case_num["week_end"])

# Dropping Unknown Variables
covid_case_num.drop(["week_start", 
                    ":@computed_region_rpca_8um6", 
                    ":@computed_region_vrxf_vc4k",
                    ":@computed_region_6mkv_f3dw", 
                    ":@computed_region_bdys_3d7i",
                    ":@computed_region_43wa_7qmu"], 
                    axis = 1, inplace = True)



##### Processing Vaccine numbers
covid_vaccination_num = pd.read_csv("rawdata/covid_vaccination_num.csv",
                                     index_col = 0)

# Dropping Unknown Variables
covid_vaccination_num.drop([":@computed_region_vrxf_vc4k", 
                            ":@computed_region_6mkv_f3dw",
                            ":@computed_region_bdys_3d7i", 
                            ":@computed_region_43wa_7qmu",
                            ":@computed_region_rpca_8um6"], 
                            axis = 1, inplace = True)

# Aggregating by week
covid_vaccination_num["date"] = pd.to_datetime(covid_vaccination_num["date"])
covid_vaccination_num["week_number"] = covid_vaccination_num["date"].dt. \
                                       isocalendar().week 

agg_funs = {"total_doses_daily": "sum" , 
            "total_doses_cumulative": "max", 
            "_1st_dose_daily": "sum",
            '_1st_dose_cumulative': "max",
            '_1st_dose_percent_population': "max", 
            'vaccine_series_completed_daily': "sum",
            'vaccine_series_completed_cumulative': "max",
            'vaccine_series_completed_percent_population': "max",
            "date": "max"}

weekly_vaccine = covid_vaccination_num.groupby(["zip_code", "week_number"]). \
                 agg(agg_funs)
weekly_vaccine = weekly_vaccine.reset_index()

##### Processing Population Information
population = pd.read_csv("rawdata/population.csv", index_col = 0)

# Taking only data from 2019
population = population[population.year == 2019]

# Normalizing by population total
col_names = population.columns[5:-1]
for item in col_names:
    population[item] = 100 * (population[item] / population.population_total)

# Renaming zip_code
population.rename(columns = {"geography": "zip_code"}, inplace = True)

# Creating Categoricals

max_ref = population[["population_latinx", 
                      "population_asian_non_latinx", 
                      "population_black_non_latinx", 
                      "population_white_non_latinx",
                      "population_other_race_non"]].copy()

max_ref = max_ref.max(axis = 1)

population["majority_latino"] = max_ref == population.population_latinx
population["majority_latino"] = population["majority_latino"].astype(int)

population["majority_asian"] = max_ref == population.population_asian_non_latinx
population["majority_asian"] = population["majority_asian"].astype(int)

population["majority_black"] = max_ref == population.population_black_non_latinx
population["majority_black"] = population["majority_black"].astype(int)

population["majority_white"] = max_ref == population.population_white_non_latinx
population["majority_white"] = population["majority_white"].astype(int)


# Dropping uneccessary variables
population.drop(["geography_type", "year", "record_id", "population_total"],
                axis = 1, inplace = True)

pop_filter =[x for x in population.columns if not x.endswith(("nx", "_non"))]
population = population[pop_filter]



### Processing Vaccionation Sites
covid_vaccination_sites = pd.read_csv("rawdata/covid_vaccination_sites.csv", 
                                      index_col = 0)

vaccionation_sites = covid_vaccination_sites.postal_code.value_counts()
vaccionation_sites = vaccionation_sites.reset_index()
vaccionation_sites.rename(columns = {"index": "zip_code", 
                                     "postal_code": "vaccionation_sites"}, 
                                     inplace = True)

vaccionation_sites["zip_code"] = vaccionation_sites["zip_code"].astype(str)



### Processing Health Centers
health_centers = pd.read_csv("rawdata/health_centers.csv")

# Getting zip code

def extract_zip(string):
    """
    Extracts zip code from health_center.location_1
    """

    return re.findall(".*\"zip\":\s+\"(.*)\"", string)[0]

health_centers["zip_code"] = health_centers.location_1. \
                             apply(lambda x: extract_zip(x))

health_centers = health_centers.zip_code.value_counts()
health_centers = health_centers.reset_index()
health_centers.rename(columns = {"index": "zip_code", 
                                 "zip_code": "health_centers"}, 
                                 inplace = True)



### Processing Hospitals
hospital = pd.read_csv("rawdata/hospital.csv", index_col = 0)
hospitals_by_zip = hospital.addr_zip.value_counts()
hospitals_by_zip = hospitals_by_zip.reset_index()
hospitals_by_zip.rename(columns = {"index": "zip_code", 
                                   "addr_zip": "number_of_hospitals"}, 
                                   inplace = True)

hospitals_by_zip["zip_code"] = hospitals_by_zip["zip_code"].astype(str)



### Joining Databases - CROSS SECTION   

lastest_cases = summarise_by_zip_latest(covid_case_num, "zip_code", "week_end")
lastest_cases = lastest_cases.reset_index()
lastest_cases = lastest_cases.drop("week_number", axis = 1)

lastest_vaccines = summarise_by_zip_latest(weekly_vaccine, "zip_code", "date")
lastest_vaccines = lastest_vaccines.reset_index()
lastest_vaccines = lastest_vaccines.drop("week_number", axis = 1)

to_append = {"demographic_info" : population, 
             "vaccine_sites" : vaccionation_sites,
             "health_centers" : health_centers,
             "hospitals" : hospitals_by_zip}

joint_database = pd.merge(lastest_cases, lastest_vaccines, on = "zip_code",
                          how = "left")

for item in to_append.values():
    joint_database = pd.merge(joint_database, item, on = "zip_code", 
                              how = "left")

repl_with_zero = joint_database.columns[-3:]
joint_database.loc[:, repl_with_zero] = joint_database.loc[:, repl_with_zero]. \
                                        fillna(0)

joint_database = joint_database.loc[joint_database.zip_code != "60666"]
joint_database = joint_database.loc[joint_database.zip_code != "Unknown"]


### Joining Databases - TIME SERIES   

ts_covid_case_num = covid_case_num.copy()
ts_weekly_vaccine = weekly_vaccine.copy()

ts_covid_case_num["year"] = ts_covid_case_num.week_end.dt.year
ts_weekly_vaccine["year"] = ts_weekly_vaccine.date.dt.year

ts_joint = pd.merge(ts_covid_case_num, ts_weekly_vaccine, 
                    left_on = ["zip_code", "year", "week_number"], 
                    right_on = ["zip_code", "year", "week_number"],
                    how = "left")

ts_joint = ts_joint.sort_values(by = ["zip_code", "week_end"])


### Writing databases
joint_database.to_csv("databases/cross_section_database " + 
                      str(datetime.date.today()) + ".csv", index = False)

ts_joint.to_csv("databases/ts_database " + 
                str(datetime.date.today()) + ".csv", index = False)