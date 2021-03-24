
DROP TABLE IF EXISTS covid_case_num;
DROP TABLE IF EXISTS covid_vaccination_num;
DROP TABLE IF EXISTS covid_vaccination_sites;
DROP TABLE IF EXISTS population;
DROP TABLE IF EXISTS health_centers;
DROP TABLE IF EXISTS hospital;
DROP TABLE IF EXISTS health_indicator_tract;


CREATE TABLE covid_case_num
   (zip_code integer,
   week_number integer,
   week_end datetime,
   tests_weekly integer,
   tests_cumulative decimal, decimal,
   test_rate_weekly decimal,
   test_rate_cumulative decimal,
   percent_tested_positive_weekly decimal,
   percent_tested_positive_cumulative decimal,
   deaths_weekly integer,
   deaths_cumulative integer,
   death_rate_weekly decimal,
   death_rate_cumulative decimal,
   population integer,
   row_id varchar(50),
   cases_weekly integer,
   cases_cumulative integer,
   case_rate_weekly decimal,
   case_rate_cumulative decimal,
   PRIMARY KEY (zip_code)
   );


CREATE TABLE covid_vaccination_num
   (zip_code integer,
   date datetime,
   total_doses_daily integer,
   total_doses_cumulative integer,
   _1st_dose_daily integer,
   _1st_dose_cumulative integer,
   _1st_dose_percent_population decimal,
   vaccine_series_completed_daily integer,
   vaccine_series_completed_cumulative integer,
   vaccine_series_completed_percent_population decimal,
   population integer,
   row_id varchar(50),
   PRIMARY KEY (zip_code)
   );


CREATE TABLE covid_vaccination_sites
   (facility_name varchar(50),
   postal_code integer,
   PRIMARY KEY (postal_code)
   );


CREATE TABLE population
   (zip_code integer,
   population_total integer,
   population_age_0_17 integer,
   population_age_18_29 integer,
   population_age_30_39 integer,
   population_age_40_49 integer,
   population_age_50_59 integer,
   population_age_60_69 integer,
   population_age_70_79 integer,
   population_age_80 integer,
   population_age_18_ integer,
   population_age_65_ integer,
   population_female integer,
   population_male integer,
   PRIMARY KEY (zip_code)
   );


CREATE TABLE health_centers
   (facility varchar(100),
   community_area varchar(50),
   phone  varchar(20),
   fqhc_look_alike_or_neither_special_notes varchar(50),
   zip_code integer,
   PRIMARY KEY (zip_code)
   );


CREATE TABLE hospital
   (id integer,
   src_id integer,
   name varchar(100),
   slug varchar(100),
   primary_type varchar(20),
   sub_type varchar(50),
   addr_street varchar(100),
   addr_city varchar(20),
   addr_zip integer,
   contact_phone varchar(20),
   lat_long varchar(50),
   PRIMARY KEY (addr_zip)
   );


CREATE TABLE health_indicator_tract
   (geoid integer,
   children_in_poverty decimal,
   dental_care decimal,
   diabetes decimal,
   frequent_mental_distress decimal,
   frequent_physical_distress decimal,
   housing_cost_excessive decimal,
   income_inequality decimal,
   life_expectancy decimal,
   obesity decimal,
   uninsured decimal,
   preventive_services decimal,
   zip_code integer,
   PRIMARY KEY (zip_code)
   );
