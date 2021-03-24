'''
This module store cleaned data to sqlite3 database
'''

from pathlib import Path
import sqlite3
import pandas as pd
import data_collect
import data_cleaning
import sys
import os

DATABASE_PATH = "covid_research.sqlite3"

def get_all_data():
    '''
    Get all cleaned data from APIs and
    store them into sqlite3 databases
    '''
    create_table()
    data_dict = {}

    covid_case_num = data_cleaning.clean_covid_case_num()
    data_dict["covid_case_num"] = covid_case_num
    covid_vaccination_num = data_cleaning.clean_covid_vaccination_num()
    data_dict["covid_vaccination_num"] = covid_vaccination_num
    covid_vaccination_sites = data_cleaning.clean_covid_vaccination_sites()
    data_dict["covid_vaccination_sites"] = covid_vaccination_sites
    population = data_cleaning.clean_population()
    data_dict["population"] = population
    health_centers = data_cleaning.clean_health_centers()
    data_dict["health_centers"] = health_centers
    hospital = data_collect.get_hospital_data()
    data_dict["hospital"] = hospital
    health_indicator_tract = data_collect.get_health_indicator_data()
    data_dict["health_indicator_tract"] = health_indicator_tract

    for table, df in data_dict.items():
        import_data(table, df)


def create_table():
    '''
    Creates the cleaned data tables using SQL scripts
    '''
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    with open('create_table.sql') as f:
        commands = f.read()
        cursor.executescript(commands)
    conn.close()


def import_data(table, df):
    '''
    Insert data from pandas DataFrame to the table in sqlite3 databses

    Input:
        table: str, name of the table in sqlite3 databases
        df: pandas DataFrame of data
    '''
    conn = sqlite3.connect(DATABASE_PATH)
    df.to_sql(table, con=conn, index=False, if_exists='replace')
    conn.close()


def gen_get_data_query():
    '''
    Generate dictionary of table name mapping to get data queries

    Output:
        dictionary of table name mapping to get data queries
    '''
    query_dict = {}
    general_query = "SELECT * FROM {} ;"
    data_lst = ["covid_case_num",
                "covid_vaccination_num",
                "covid_vaccination_sites",
                "population",
                "health_centers",
                "hospital",
                "health_indicator_tract"]
    for dataset in data_lst:
        query_dict[dataset] = general_query.format(dataset)
    return query_dict


GET_DATA_QUERY = gen_get_data_query()


def get_data(table):
    '''
    Get dataframe of one specific table from the splite3 databases

    Input:
        table: str, name of the table in sqlite3 databses

    Output:
        dataframe: pandas DataFrame of requested data
    '''
    if table in GET_DATA_QUERY:
        connection = sqlite3.connect(DATABASE_PATH)
        conn = connection.cursor()
        query = GET_DATA_QUERY[table]
        conn.execute(query)
        result_data = conn.fetchall()
        column_des = conn.description
        column_names = [column_des[i][0] for i in range(len(column_des))]
        df = pd.DataFrame(list(result_data), columns = column_names)
        conn.close()
        connection.close()
        return df
    print("Table is not available")


if __name__ == "__main__":
    print("Updating all cleaned data tables in database 'covid_research.sqlite3'")
    get_all_data()
    print("Successfully updated the tables")
