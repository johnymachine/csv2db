-- psql -h 147.230.21.34 -U student -d rdb2015_danielmadera -f test-insert-raw-data.sql

-- author: Daniel Madera
-- description: test if duplicate data are ommitting properly

set schema 'rdb';
begin;

truncate table measurements cascade;
truncate table units cascade;
truncate table devices cascade;
truncate table blocks cascade;
truncate table locations cascade;

insert into raw_data_view (
        created, unit, location_id, longitude, latitude, location_description, value1, value2, 
        unit_deviation, serial_number, device_description, block_id, block_description
    ) values (
        '2015-05-15 15:15:00', 'A', 2, 31813.000, 2116.000, 'prutok b2', 180422.000, 129.000, 0.015,
        '2548DESWE-87-874/4', 'WEIGHT METER', 6, 'Voltage in dam 3'
    ), (
        '2015-05-15 15:15:00', 'A', 2, 31813.000, 2116.000, 'prutok b2', 180422.000, 129.000, 0.015,
        '2548DESWE-87-874/4', 'WEIGHT METER', 6, 'Voltage in dam 3'
    ), (
        '2015-05-15 15:15:00', 'A', 2, 31813.000, 2116.000, 'prutok b2', 180422.000, 129.000, 0.015,
        '214SDAADW-83-274/3', 'WEIGHT METER', 6, 'Voltage in dam 3'
    ), (
        '2015-05-15 15:15:00', 'A', 2, 31813.000, 2116.000, 'prutok b2', 1222.000, 129.000, 0.015,
        '2548DESWE-87-874/4', 'WEIGHT METER', 3,  'Voltage in dam 3'
    );

select case when count(*) = 2 then 'pass' else 'failed count of measurements' end as result from measurements;
select case when count(*) = 2 then 'pass' else 'failed count of devices' end as result from devices;
select case when count(*) = 1 then 'pass' else 'failed count of locations' end as result from locations;
select case when count(*) = 2 then 'pass' else 'failed count of blocks' end as result from blocks;

rollback;