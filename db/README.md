## Setting up server database

Required PostgreSQL database version >= 9.0

Required packages
```
	postgresql 
	postgresql-contrib 
	postgresql-plpython
```

Connect to database via command line (required package postgresql)
```
	psql -h SERVER_IP -U DATABASE_NAME
```

As superuser on used database perform query below to enable plpythonu extension.
```
	CREATE EXTENSION plpythonu;
```

Create function csv_parse as database useruser
```
    psql -h SERVER_IP -d DATABASE_NAME -U SUPERUSER_ROLE -f db/scripts/csv-parse-function.sql
```

## Development requirements
```
sudo apt-get install python3-dev
```
In python's virtual environment
```
pip3 install psycopg2
```