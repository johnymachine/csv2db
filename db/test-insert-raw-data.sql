-- psql -h 147.230.21.34 -U student -d rdb2015_danielmadera -f test-insert-raw-data.sql

-- author: Daniel Madera
-- description: test if duplicate data are ommitting properly

set schema 'rdb';
begin;

delete from measurements;
delete from units;
delete from devices;
delete from blocks;
delete from locations;

insert into raw_data_view (
        created, unit, location_id, longitude, latitude, location_description, value1, value2, 
        unit_deviation, serial_number, device_description, block_id, block_description
    ) values (
        '2015-01-01 00:00:00', 'A', 1, 1.0, 1.0, 'loc_description', 0, 1, 0.1, -- + u, d, b, l, m
        'sn_A', 'device_description', 1, 'block_description'
    );

insert into raw_data_view (
        created, unit, location_id, longitude, latitude, location_description, value1, value2, 
        unit_deviation, serial_number, device_description, block_id, block_description
    ) values (
        '2015-02-01 00:00:00', 'A', 1, 1.0, 1.0, 'loc_description', 0, 1, 0.1, -- + m
        'sn_A', 'device_description', 1, 'block_description'
    );
insert into raw_data_view (
        created, unit, location_id, longitude, latitude, location_description, value1, value2, 
        unit_deviation, serial_number, device_description, block_id, block_description
    ) values (
        '2015-01-01 00:00:00', 'A', 1, 1.0, 1.0, 'loc_description', 2, 3, 0.1, -- + m
        'sn_A', 'device_description', 1, 'block_description'
    );

select 1 as expected, count(*) as actual, case when 1 = count(*) then 'pass' else 'failed consistency of units' end as result from units;
select 1 as expected, count(*) as actual, case when 1 = count(*) then 'pass' else 'failed consistency of devices' end as result from devices;
select 1 as expected, count(*) as actual, case when 1 = count(*) then 'pass' else 'failed consistency of locations' end as result from locations;
select 1 as expected, count(*) as actual, case when 1 = count(*) then 'pass' else 'failed consistency of blocks' end as result from blocks;
select 3 as expected, count(*) as actual, case when 3 = count(*) then 'pass' else 'failed consistency of measurements' end as result from measurements;

insert into raw_data_view (
        created, unit, location_id, longitude, latitude, location_description, value1, value2, 
        unit_deviation, serial_number, device_description, block_id, block_description
    ) values (
        '2015-01-01 00:00:00', 'Hz', 1, 1.0, 1.0, 'loc_description', 0, 1, 0.1, -- + u, m
        'sn_A', 'device_description', 1, 'block_description'
    );

insert into raw_data_view (
        created, unit, location_id, longitude, latitude, location_description, value1, value2, 
        unit_deviation, serial_number, device_description, block_id, block_description
    ) values (
        '2015-01-01 00:00:00', 'Hz', 1, 1.0, 1.0, 'loc_description', 0, 1, 0.01, -- inconsistent unit deaviation
        'sn_A', 'device_description', 1, 'block_description'
    );

insert into raw_data_view (
        created, unit, location_id, longitude, latitude, location_description, value1, value2, 
        unit_deviation, serial_number, device_description, block_id, block_description
    ) values (
        '2015-01-01 00:00:00', 'A', 1, 1.0, 1.0, 'loc_description1', 0, 1, 0.1, -- inconsistent location description
        'sn_A', 'device_description', 1, 'block_description'
    );

insert into raw_data_view (
        created, unit, location_id, longitude, latitude, location_description, value1, value2, 
        unit_deviation, serial_number, device_description, block_id, block_description
    ) values (
        '2015-01-01 00:00:00', 'A', 2, 1.0, 1.0, 'loc_description2', 0, 1, 0.1, -- l, m
        'sn_A', 'device_description', 1, 'block_description'
    );


select 2 as expected, count(*) as actual, case when 2 = count(*) then 'pass' else 'failed consistency of units' end as result from units;
select 1 as expected, count(*) as actual, case when 1 = count(*) then 'pass' else 'failed consistency of devices' end as result from devices;
select 2 as expected, count(*) as actual, case when 2 = count(*) then 'pass' else 'failed consistency of locations' end as result from locations;
select 1 as expected, count(*) as actual, case when 1 = count(*) then 'pass' else 'failed consistency of blocks' end as result from blocks;
select 5 as expected, count(*) as actual, case when 5 = count(*) then 'pass' else 'failed consistency of measurements' end as result from measurements;

insert into raw_data_view (
        created, unit, location_id, longitude, latitude, location_description, value1, value2, 
        unit_deviation, serial_number, device_description, block_id, block_description
    ) values (
        '2015-01-01 00:00:00', 'Hz', 1, 1.0, 1.0, 'loc_description', 0, 1, 0.1, -- inconsistent measurement already exist
        'sn_A', 'device_description', 1, 'block_description'
    );

insert into raw_data_view (
        created, unit, location_id, longitude, latitude, location_description, value1, value2, 
        unit_deviation, serial_number, device_description, block_id, block_description
    ) values (
        '2015-01-01 00:00:00', 'Hz', 1, 1.0, 1.0, 'loc_description', 0, 1, 0.1, -- inconsistent device
        'sn_A', 'device_description1', 1, 'block_description'
    );

insert into raw_data_view (
        created, unit, location_id, longitude, latitude, location_description, value1, value2, 
        unit_deviation, serial_number, device_description, block_id, block_description
    ) values (
        '2015-01-01 00:00:00', 'A', 1, 1.0, 1.0, 'loc_description', 0, 1, 0.1, -- inconsistent block
        'sn_A', 'device_description', 1, 'block_description1'
    );

insert into raw_data_view (
        created, unit, location_id, longitude, latitude, location_description, value1, value2, 
        unit_deviation, serial_number, device_description, block_id, block_description
    ) values (
        '2015-01-01 00:00:00', 'A', 1, 1.0, 1.0, 'loc_description', 0, 1, 0.1, -- b, m
        'sn_A', 'device_description', 2, 'block_description2'
    );

insert into raw_data_view (
        created, unit, location_id, longitude, latitude, location_description, value1, value2, 
        unit_deviation, serial_number, device_description, block_id, block_description
    ) values (
        '2015-01-01 00:00:00', 'A', 1, 1.0, 1.0, 'loc_description', 0, 1, 0.1, -- d, m
        'sn_B', 'device_description2', 1, 'block_description'
    );


select 2 as expected, count(*) as actual, case when 2 = count(*) then 'pass' else 'failed consistency of units' end as result from units;
select 2 as expected, count(*) as actual, case when 2 = count(*) then 'pass' else 'failed consistency of devices' end as result from devices;
select 2 as expected, count(*) as actual, case when 2 = count(*) then 'pass' else 'failed consistency of locations' end as result from locations;
select 2 as expected, count(*) as actual, case when 2 = count(*) then 'pass' else 'failed consistency of blocks' end as result from blocks;
select 7 as expected, count(*) as actual, case when 7 = count(*) then 'pass' else 'failed consistency of measurements' end as result from measurements;

-- select * from measurements;


rollback;