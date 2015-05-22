-- psql -h 147.230.21.34 -U student -d rdb2015_danielmadera -f create-triggers-views.sql

set schema 'rdb';

drop rule if exists units_on_duplicate_ignore on units;
drop rule if exists devices_on_duplicate_ignore on devices;
drop rule if exists blocks_on_duplicate_ignore on blocks;
drop rule if exists locations_on_duplicate_ignore on locations;
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
        insert into units (unit, deviation) values (new.unit, new.unit_deviation);
        -- devices
        insert into devices (serial_number, description) values (new.serial_number, new.device_description);
        -- blocks
        insert into blocks (id, description) values (new.block_id, new.block_description);
        -- locations
        insert into locations (id, longitude, latitude, description) values (new.location_id, new.longitude, new.latitude, new.location_description);
        -- measurements
        insert into measurements (created, value1, value2, unit, block_id, device_sn, location_id) values (new.created, new.value1, new.value2, new.unit, new.block_id, new.serial_number, new.location_id);        
        return null;
    end;
$insert_raw_data$ language plpgsql;

create trigger insert_raw_data
    instead of insert on raw_data_view
    for each row
    execute procedure insert_raw_data();

create rule units_on_duplicate_ignore as on insert to units
    where exists (
        select 1 from units where unit = new.unit
    ) do instead nothing;

create rule devices_on_duplicate_ignore as on insert to devices
    where exists (
        select 1 from devices where serial_number = new.serial_number
    ) do instead nothing;

create rule blocks_on_duplicate_ignore as on insert to blocks
    where exists (
        select 1 from blocks where id = new.id
    ) do instead nothing;

create rule locations_on_duplicate_ignore as on insert to locations
    where exists (
        select 1 from locations where id = new.id
    ) do instead nothing;

create rule measurements_on_duplicate_ignore as on insert to measurements
    where exists (
        select 1 from measurements where 
            created = new.created and value1 = new.value1 and
            value2 = new.value2 and unit = new.unit and
            block_id = new.block_id and device_sn = new.device_sn and
            location_id = new.location_id
    ) do instead nothing;