-- psql -h 127.0.0.1 -U student -d rdb2015_danielmadera -f create-script.sql
-- psql -h 147.230.21.34 -U student -d rdb2015_danielmadera -f create-script.sql

-- author: Daniel Madera
-- description: creates all structures including schema, functions, triggers and rules in database

drop schema if exists rdb cascade;
create schema rdb;
set schema 'rdb';

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
    device_sn character varying(80) not null,
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
    device_sn character varying(80) not null,
    location_id integer not null
) with (oids=false);

create table units (
    unit character varying(30) not null,
    deviation real not null
) with (oids=false);

create table devices (
    serial_number character varying(80) not null,
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
alter table measurements add constraint measurement_device foreign key (device_sn) references devices (serial_number) on delete cascade on update cascade;
alter table measurements add constraint measurement_location foreign key (location_id) references locations (id) on delete restrict on update cascade;

create index ix_measurement_unit on measurements (unit);
create index ix_measurement_block on measurements (block_id);
create index ix_mesurememnt_device on measurements (device_sn);
create index ix_mesuremement_location on measurements (block_id);

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
        m.device_sn as serial_number,
        m.unit as unit,
        l.longitude as loc_x,
        l.latitude as loc_y
    from measurements as m
    join units as u on u.unit = m.unit
    join devices as d on d.serial_number = m.device_sn
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
        d.description as device_description, 
        b.id as block_id, 
        b.description as block_description
    from measurements as m
    join units as u on u.unit = m.unit
    join devices as d on d.serial_number = m.device_sn
    join blocks as b on b.id = m.block_id
    join locations as l on l.id = m.location_id;

-- ## FUNCTIONS ## --
create or replace function insert_raw_data() returns trigger as $insert_raw_data$        
    begin
                
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

        select count(*) into affected_rows from measurements where device_sn = old.serial_number;
        insert into logs (operation, created, username, tablename, description) values 
            (lower(tg_op), (now() at time zone 'utc'), user, 'measurements', affected_rows || ' measurement(s) were removed with device ' || old.serial_number || '.');
        return old; 
    end;
$log_remove_device$ language plpgsql;

-- ## TRIGGERS ## --
create trigger insert_raw_data
    after insert on raw_data
    for statement execute procedure insert_raw_data();

create trigger log_insert_raw_data
    after insert on raw_data_view
    for statement execute procedure log_insert_raw_data();

create trigger log_remove_block
    before delete on blocks
    for each row execute procedure log_remove_block();

create trigger log_remove_device
    before delete on devices
    for each row execute procedure log_remove_device();


create rule units_on_duplicate_ignore as on insert to units
     where exists (
         select 1 from units where id = new.id) do instead nothing;

/*
-- ## RULES ## --
-- useless, slows down inserts to a crawl
create or replace rule measurements_on_duplicate_ignore as on insert to measurements
    where exists (
        select 1 from measurements where 
            created = new.created and value1 = new.value1 and
            value2 = new.value2 and unit = new.unit and
            block_id = new.block_id and device_sn = new.device_sn and
            location_id = new.location_id
    ) do instead nothing;
*/