-- psql -h 147.230.21.34 -U student -d postgres -f create-db.sql

create database rdb2015_danielmadera
    with owner student
    encoding 'utf8' 
    template template0;
