-- psql -h 127.0.0.1 -U postgres -d RDB2015_DanielMadera -f insert-devices.sql
-- psql -h 147.230.21.34 -U student -d RDB2015_DanielMadera -f insert-devices.sql

set schema 'rdb';

insert into devices(serial_number, description) values ('2548DESWE-87-874/4', 'WEIGHT METER');
insert into devices(serial_number, description) values ('2517/7', 'AMPER METER 1');
insert into devices(serial_number, description) values ('DESWR/DFGTRE-587', 'AMPER METER 2');
insert into devices(serial_number, description) values ('251-DF-DFR-FRT', 'FLOW METER 3');