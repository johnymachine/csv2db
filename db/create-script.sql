-- psql -h 127.0.0.1 -U student -d rdb2015_danielmadera -f create-script.sql
-- psql -h 147.230.21.34 -U student -d rdb2015_danielmadera -f create-script.sql

-- author: Daniel Madera
-- description: creates all structures including schema, functions, triggers and rules in database

drop schema if exists rdb cascade;
create schema rdb;
set schema 'rdb';
set search_path to 'rdb';

-- ## TABLES ## --

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
        u.deviation as unit_deviation,
        m.block_id as block_id,
        m.serial_number as serial_number,
        d.deviation as device_deviation,
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
    declare 
        u rdb.units%ROWTYPE;
        d rdb.devices%ROWTYPE;
        b rdb.blocks%ROWTYPE;
        l rdb.locations%ROWTYPE;
    begin
        set schema 'rdb';
        select * into u from units where units.unit = new.unit;
        select * into d from devices where devices.serial_number = new.serial_number;
        select * into b from blocks where blocks.id = new.block_id;
        select * into l from locations where locations.id = new.location_id;

        if u is not null and u.deviation != new.unit_deviation then
            -- raise notice 'row is not consistent because of unit';
            return null;
        end if;        

        if d is not null and (d.description != new.device_description or d.deviation != new.device_deviation) then
            -- raise notice 'row is not consistent because of device';
            return null;
        end if;

        if b is not null and b.description != new.block_description then
            -- raise notice 'row is not consistent because of block';
            return null;
        end if;
        
        if l is not null and (l.longitude != new.longitude or l.latitude != new.latitude or l.description != new.location_description) then
            -- raise notice 'row is not consistent because of location';
            return null;
        end if;
        
        
        if u is null then
            insert into units (unit, deviation) values (new.unit, new.unit_deviation);
        end if;
        if d is null then 
            insert into devices (serial_number, deviation, description) values (new.serial_number, new.device_deviation, new.device_description);
        end if;
        if b is null then
            insert into blocks (id, description) values (new.block_id, new.block_description);
        end if;
        if l is null then
            insert into locations (id, longitude, latitude, description) values (new.location_id, new.longitude, new.latitude, new.location_description);
        end if;
        insert into measurements (created, value1, value2, unit, block_id, serial_number, location_id) values (new.created, new.value1, new.value2, new.unit, new.block_id, new.serial_number, new.location_id);        
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

-- ## TRIGGERS ## --
create trigger insert_raw_data
    instead of insert on raw_data_view
    for each row execute procedure insert_raw_data();

create trigger log_insert_raw_data
    after insert on raw_data_view
    for statement execute procedure log_insert_raw_data();

create trigger log_remove_block
    before delete on blocks
    for each row execute procedure log_remove_block();

create trigger log_remove_device
    before delete on devices
    for each row execute procedure log_remove_device();
