# covid19API
An API project for Software Design with Jeff Ondich at Carleton College. Uses data from the Covid Tracking Project.

Uses the psycopg2 and Flask modules for Python to retrieve the results of SQL queries to the database and present these results at
the appropriate API endpoints, respectively. The output is presented in raw JSON format. The database is included as "covid19.sql" and includes
data from 10/12/2020 and before.

Once the database is set up, launch the server using "python3 covid19_api.py [host] [port]".
