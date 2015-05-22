-- psql -h 127.0.0.1 -U postgres -d rdb2015_danielmadera -f insert.sql
-- psql -h 147.230.21.34 -U student -d rdb2015_danielmadera -f insert.sql

set schema 'rdb';

-- devices
delete from devices;
insert into devices(serial_number, description) values ('2548DESWE-87-874/4', 'WEIGHT METER');
insert into devices(serial_number, description) values ('2517/7', 'AMPER METER 1');
insert into devices(serial_number, description) values ('DESWR/DFGTRE-587', 'AMPER METER 2');
insert into devices(serial_number, description) values ('251-DF-DFR-FRT', 'FLOW METER 3');

-- blocks
delete from blocks;
insert into blocks(id, description) values (6, 'Voltage in dam 3');
insert into blocks(id, description) values (5, 'Voltage in dam 2');
insert into blocks(id, description) values (2, 'Measurement desc 3');
insert into blocks(id, description) values (13, 'Flow in corridor 4');
