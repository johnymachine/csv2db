-- psql -h 127.0.0.1 -U student -d rdb2015_danielmadera -f create-script.sql
-- psql -h 147.230.21.34 -U student -d rdb2015_danielmadera -f create-script.sql

-- author: Daniel Madera
-- description: creates all structures including schema, functions, triggers and rules in database

drop schema if exists rdb cascade;
create schema rdb;
set schema 'rdb';
set search_path to 'rdb';

-- ## TABLES ## --

create table raw_data (
    created timestamp not null, 
    unit character varying(30) not null,
    location_id integer not null,
    longitude real not null,
    latitude real not null, 
    location_description character varying(250),
    value1 real not null,
    value2 real not null,
    unit_deviation real not null,
    serial_number character varying(80) not null,
    device_deviation real not null,
    device_description character varying(250),
    block_id integer not null,
    block_description character varying(250)
);

create table measurements (
    id serial,
    created timestamp not null,
    value1 real not null,
    value2 real not null,
    unit character varying(30) not null,
    block_id integer not null,
    serial_number character varying(80) not null,
    location_id integer not null
) with (oids=false);

create table units (
    unit character varying(30) not null,
    deviation real not null
) with (oids=false);

create table devices (
    serial_number character varying(80) not null,
    deviation real not null,
    description character varying(250)
) with (oids=false);

create table blocks (
    id integer not null,
    description character varying(250)
) with (oids=false);

create table locations (
    id integer not null,
    longitude real not null,
    latitude real not null,
    description character varying(250)
) with (oids=false);

create table logs (
    id serial,
    created timestamp not null default (now() at time zone 'utc'),
    operation character (6) not null,
    username varchar(30) not null,
    tablename varchar(30) not null,
    description varchar(250)
);

-- ## CONSTRAINTS ## --
alter table measurements add constraint pk_measurements primary key (id);
alter table units add constraint pk_units primary key (unit);
alter table devices add constraint pk_devices primary key (serial_number);
alter table blocks add constraint pk_blocks primary key (id);
alter table locations add constraint pk_locations primary key (id);
alter table logs add constraint pk_logs primary key (id);

alter table measurements add constraint measurement_unit foreign key (unit) references units (unit) on delete restrict on update cascade;
alter table measurements add constraint measurement_block foreign key (block_id) references blocks (id) on delete cascade on update cascade;
alter table measurements add constraint measurement_device foreign key (serial_number) references devices (serial_number) on delete cascade on update cascade;
alter table measurements add constraint measurement_location foreign key (location_id) references locations (id) on delete restrict on update cascade;

create index ix_measurement_unit on measurements (unit);
create index ix_measurement_block on measurements (block_id);
create index ix_mesurememnt_device on measurements (serial_number);
create index ix_mesuremement_location on measurements (location_id);
create index ix_mesuremement_created on measurements (created);

-- ## VIEWS ## --
create or replace view measurements_view as
    select 
        m.created as created, 
        m.value1 as value1, 
        m.value2 as value2, 
        abs(m.value1 - m.value2) as difference,
        d.description as device_description,
        d.deviation as device_deviation,
        m.block_id as block_id,
        m.serial_number as serial_number,
        m.unit as unit,
        l.longitude as loc_x,
        l.latitude as loc_y
    from measurements as m
    join units as u on u.unit = m.unit
    join devices as d on d.serial_number = m.serial_number
    join locations as l on l.id = m.location_id;

create or replace view raw_data_view as
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
        d.deviation as device_deviation,
        d.description as device_description, 
        b.id as block_id, 
        b.description as block_description
    from measurements as m
    join units as u on u.unit = m.unit
    join devices as d on d.serial_number = m.serial_number
    join blocks as b on b.id = m.block_id
    join locations as l on l.id = m.location_id;

-- ## FUNCTIONS ## --
create or replace function insert_raw_data() returns trigger as $insert_raw_data$        
    begin
        delete from raw_data where created in (
        select created from raw_data
            left outer join units on raw_data.unit = units.unit and raw_data.unit_deviation != units.deviation
            left outer join devices on raw_data.serial_number = devices.serial_number and (raw_data.device_description != devices.description or raw_data.device_deviation != devices.deviation)
            left outer join blocks on raw_data.block_id = blocks.id and  raw_data.block_description != blocks.description
            left outer join locations on raw_data.location_id = locations.id and 
                (raw_data.longitude != locations.longitude or raw_data.latitude != locations.latitude or raw_data.location_description != locations.description)
        where units.unit is not null or devices.serial_number is not null or blocks.id is not null);

        -- vlozit neexistujici devices, units, ...
        insert into units
            select * from first_unique_units();

        insert into blocks
            select * from first_unique_blocks();

        insert into devices
            select * from first_unique_devices();

        insert into locations
            select * from first_unique_locations();
            
        -- smazani nekonzistentnich
        delete from raw_data where created in (
        select created from raw_data
            left outer join units on raw_data.unit = units.unit and raw_data.unit_deviation != units.deviation
            left outer join devices on raw_data.serial_number = devices.serial_number and (raw_data.device_description != devices.description or raw_data.device_deviation != devices.deviation)
            left outer join blocks on raw_data.block_id = blocks.id and  raw_data.block_description != blocks.description
            left outer join locations on raw_data.location_id = locations.id and 
                (raw_data.longitude != locations.longitude or raw_data.latitude != locations.latitude or raw_data.location_description != locations.description)
        where units.unit is not null or devices.serial_number is not null or blocks.id is not null);

        insert into measurements(created, value1, value2, unit, block_id, serial_number, location_id)
        select created, value1, value2, unit, block_id, serial_number, location_id from raw_data;

        delete from raw_data;

        return null;
    end;
$insert_raw_data$ language plpgsql;

create or replace function log_insert_raw_data() returns trigger as $log_raw_data_insert$
    begin
        insert into logs (operation, created, username, tablename, description) values 
            (lower(tg_op), (now() at time zone 'utc'), user, tg_relname, 'CSV data were inserted.');  
        return null; 
    end;
$log_raw_data_insert$ language plpgsql;

create or replace function log_remove_block() returns trigger as $log_remove_block$
    declare
        affected_rows integer;
    begin
        insert into logs (operation, created, username, tablename, description) values 
            (lower(tg_op), (now() at time zone 'utc'), user, tg_relname, 'Block "' || old.description || '" was removed.');
        
        select count(*) into affected_rows from measurements where block_id = old.id;
        insert into logs (operation, created, username, tablename, description) values 
            (lower(tg_op), (now() at time zone 'utc'), user, 'measurements', affected_rows || ' measurement(s) were removed with block "' || old.description || '".');
        return old;
    end;
$log_remove_block$ language plpgsql;

create or replace function log_remove_device() returns trigger as $log_remove_device$
    declare
        affected_rows integer;
    begin
        insert into logs (operation, created, username, tablename, description) values 
            (lower(tg_op), (now() at time zone 'utc'), user, tg_relname, 'Device "' || old.serial_number || '" was removed.');

        select count(*) into affected_rows from measurements where serial_number = old.serial_number;
        insert into logs (operation, created, username, tablename, description) values 
            (lower(tg_op), (now() at time zone 'utc'), user, 'measurements', affected_rows || ' measurement(s) were removed with device ' || old.serial_number || '.');
        return old; 
    end;
$log_remove_device$ language plpgsql;

create or replace function first_unique_units() returns setof units as $first_unique_units$
    begin
        return query
        with ordered as
        (
        select
            unit,
            unit_deviation,
            row_number() over (partition by unit order by created asc) as rn
        from
            raw_data
        )
        select
            unit,
            unit_deviation
        from
            ordered
        where
            rn = 1;
    end;
$first_unique_units$ language plpgsql;

create or replace function first_unique_blocks() returns setof blocks as $first_unique_blocks$
    begin
        return query
        with ordered as
        (
        select
            block_id,
            block_description,
            row_number() over (partition by block_id order by created asc) as rn
        from
            raw_data
        )
        select
            block_id,
            block_description
        from
            ordered
        where
            rn = 1;
    end;
$first_unique_blocks$ language plpgsql;

create or replace function first_unique_devices() returns setof devices as $first_unique_devices$
    begin
        return query
        with ordered as
        (
        select
            serial_number,
            device_deviation,
            device_description,
            row_number() over (partition by serial_number order by created asc) as rn
        from
            raw_data
        )
        select
            serial_number,
            device_deviation,
            device_description
        from
            ordered
        where
            rn = 1;
    end;
$first_unique_devices$ language plpgsql;

create or replace function first_unique_locations() returns setof locations as $first_unique_locations$
    begin
        return query
        with ordered as
        (
        select
            location_id,
            longitude,
            latitude,
            location_description,
            row_number() over (partition by location_id order by created asc) as rn
        from
            raw_data
        )
        select
            location_id,
            longitude,
            latitude,
            location_description
        from
            ordered
        where
            rn = 1;
    end;
$first_unique_locations$ language plpgsql;



-- ## TRIGGERS ## --
create trigger insert_raw_data
    after insert on raw_data
    for statement execute procedure insert_raw_data();

create trigger log_insert_raw_data
    after insert on raw_data
    for statement execute procedure log_insert_raw_data();

create trigger log_remove_block
    before delete on blocks
    for each row execute procedure log_remove_block();

create trigger log_remove_device
    before delete on devices
    for each row execute procedure log_remove_device();


-- ## RULES ## --
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
