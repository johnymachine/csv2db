-- psql -h 147.230.21.34 -U student -d RDB2015_DanielMadera -f create-view-raw-data.sql

set schema 'rdb';

drop trigger if exists insert_raw_data on raw_data_view;
drop function if exists insert_raw_data();
drop view if exists raw_data_view;

create view raw_data_view as
    select 
        m.created as created, 
        m.unit as unit, 
        l.id as location_id, 
        l.longitude as longitude, 
        l.latitude as latitude, 
        l.description as location_description, 
        m.value1 as value1, 
        m.value2 as value2, 
        u.deviation as unit_deviation, 
        d.serial_number as serial_number, 
        d.description as device_description, 
        b.id as block_id, 
        b.description as block_description
    from measurements as m
    join units as u on u.unit = m.unit
    join devices as d on d.serial_number = m.device_sn
    join blocks as b on b.id = m.block_id
    join locations as l on l.id = m.location_id;

create function insert_raw_data() returns trigger as $insert_raw_data$
    begin
        -- units
        insert into units (unit, deviation) 
            values (new.unit, new.deviation);
        -- devices
        insert into devices (serial_number, description) 
            values (new.serial_number, new.device_description);
        -- blocks
        insert into blocks (id, description) 
            values (new.block_id, new.block_description);
        -- locations
        insert into locations (id, longitude, latitude, description) 
            values (new.location_id, new.longitude, new.latitude, new.location_description);
        -- measurements
        insert into measurements (created, value1, value2, unit, block_id, device_sn, location_id)
            values (new.created, new.value1, new.value2, new.unit, new.block_id, new.serial_number, new.location_id);
    end;
$insert_raw_data$ language plpgsql;

create trigger insert_raw_data
    instead of insert on raw_data_view
    for each row
    execute procedure insert_raw_data();

