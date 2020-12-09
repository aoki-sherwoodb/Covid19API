import csv

# dictionary: {'AK':0, 'NE':0, 'IA':0, 'MA':0, ...}
# {'AK':0, 'NE':1, 'IA':2, 'MA':3, ...}
states_dictionary = {}
states_file  = open('all-states-history.csv')
reader = csv.reader(states_file)

for row in reader:
    state_abbrev = row[1]
    if state_abbrev not in states_dictionary:
        states_dictionary[state_abbrev] = len(states_dictionary)
states_file.close()

states_csv_file = open('states.csv', 'w')
writer = csv.writer(states_csv_file)
for key in states_dictionary:
    writer.writerow([states_dictionary[key], key])
states_csv_file.close()

data_csv_file = open('covid19_data.csv', 'w')
writer = csv.writer(data_csv_file)
states_file = open('all-states-history.csv')
reader = csv.reader(states_file)
#need deaths, new postitive tests, new negative tests, new hospitalizations
for row in reader:
    output = [row[0], states_dictionary[row[1]], row[2], row[5], row[4], row[3]]
    writer.writerow(output)
