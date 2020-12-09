#!/usr/bin/env python3
'''
    covid19_api.py
	A simple api to display a few covid19 statistics by state in the USA
	Adapted from flask_sample.py by Jeff Ondich

	Ben Aoki-Sherwood & Avery Watts
	October 13 2020
'''
import sys
import argparse
import flask
import json
import psycopg2

from config import password
from config import database
from config import user

try:
    connection = psycopg2.connect(database=database, user=user, password=password)
except Exception as e:
    print(e)
    exit()

app = flask.Flask(__name__)

@app.route('/state/<state_abbreviation>/daily')
def get_single_state_daily_data(state_abbreviation):
	state_daily_covid_data = query_state_data(state_abbreviation.upper())
	return json.dumps(state_daily_covid_data)

def query_state_data(state_abbreviation):
	#For the state specified by the state abbreviation, retrieves covid19 data for each day in the dataset as a list of dictionaries.
	
	state_daily_covid_data = []
	try:
		cursor = connection.cursor()
		query = f"SELECT date, abbreviation, deaths, new_positive_tests, new_negative_tests, new_hospitalizations FROM states, covid19_days WHERE states.id=covid19_days.state_id AND states.abbreviation='{state_abbreviation}';"
		cursor.execute(query)
	except Exception as e:
		print(e)
		exit()

	for row in cursor:
		state_daily_covid_data.append({'date': str(row[0]), 'state': row[1], 'deaths': row[2], 'positive': row[3], 'negative': row[4], 'hospitalizations': row[5]})

	return state_daily_covid_data

@app.route('/state/<state_abbreviation>/cumulative')
def get_single_state_cumulative_data(state_abbreviation):
	state_daily_data_dict_list = query_state_data(state_abbreviation.upper())
	state_cumulative_data = accumulate_state_daily_data(state_daily_data_dict_list)
	return json.dumps(state_cumulative_data )

def accumulate_state_daily_data(state_daily_data_dict_list):
	#Compiles a list of dictionaries of daily covid data for a state into a single dictionary with the cumulative statistics for that state.
	
	start_date = state_daily_data_dict_list[len(state_daily_data_dict_list)-1].get('date')
	end_date = state_daily_data_dict_list[0].get('date')
	state = state_daily_data_dict_list[0].get('state')
	deaths = 0
	positive = 0
	negative = 0
	hospitalizations = 0

	for date_dictionary in state_daily_data_dict_list:
		deaths += date_dictionary.get('deaths')
		positive += date_dictionary.get('positive')
		negative += date_dictionary.get('negative')
		hospitalizations += date_dictionary.get('hospitalizations')

	state_cumulative_data = {'start_date': start_date, 'end_date': end_date, 'state': state, 'deaths': deaths, 'positive': positive, 'negative': negative, 'hospitalizations': hospitalizations}
	return state_cumulative_data 

@app.route('/states/cumulative')
def get_all_states_cumulative_data():
	sorting_metric = flask.request.args.get('sort')
	sort_by_string = parse_sorting_metric(sorting_metric)
	all_states_cumulative_data = []
	for state in get_state_abbreviations():
		   all_states_cumulative_data.append(accumulate_state_daily_data(query_state_data(state)))
	sorted_all_states_cumulative_data = sort_data_by(sort_by_string, all_states_cumulative_data)
	return json.dumps(sorted_all_states_cumulative_data)

def parse_sorting_metric(sorting_metric):
	if sorting_metric == 'cases':
		sort_by_string = 'positive'
	elif sorting_metric == 'hospitalizations':
		sort_by_string = 'hospitalizations'	 
	else:
		 sort_by_string = 'deaths'
	return sort_by_string

def sort_data_by(sort_string, data_dict_list):
	sorted_dict_list = sorted(data_dict_list, key=lambda state: state[sort_string], reverse=True)
	return sorted_dict_list
		   
def get_state_abbreviations():
	state_abbreviations = []
	try:
		cursor = connection.cursor()
		query = 'SELECT abbreviation FROM states;'
		cursor.execute(query)
	except Exception as e:
		print(e)
		exit()
	for abbreviation in cursor:
		state_abbreviations.append(abbreviation[0])
	return state_abbreviations

@app.route('/help')
def get_help():
	help_message = 'USAGE: \n /state/{state_abbreviation}/daily responds with a list of dictionaries of daily covid19 data for the state given in the state_abbreviation field. Data consists of the date, the state, the deaths, positive tests, negative tests, and hospitalizations for each day. \n /state/{state_abbreviation}/cumulative responds with a single dictionary containing the cumulative covid data for the given state. \n /states/cumulative?sort=[deaths|cases|hospitalizations] responds with a list of dictionaries containing the cumulative data for each state sorted greatest-to-least by the sort parameter, which is deaths by default. \n /help responds with this message.'
	print(help_message)
	return help_message
		   
if __name__ == '__main__':
    parser = argparse.ArgumentParser('A simple COVID19 data Flask API')
    parser.add_argument('host', help='the host on which this application is running')
    parser.add_argument('port', type=int, help='the port on which this application is listening')
    arguments = parser.parse_args()
    app.run(host=arguments.host, port=arguments.port, debug=True)
