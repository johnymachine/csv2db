-- psql -h 127.0.0.1 -U student -d rdb2015_danielmadera -f create-script.sql
-- psql -h 147.230.21.34 -U student -d rdb2015_danielmadera -f create-script.sql

-- author: Daniel Madera
-- description: creates all structures including schema, functions, triggers and rules in database

drop schema if exists rdb cascade;
create schema rdb;
set schema 'rdb';

-- ## TABLES ## --
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

-- ## CONSTRAINTS ## --
alter table measurements add constraint pk_measurements primary key (id);
alter table units add constraint pk_units primary key (unit);
alter table devices add constraint pk_devices primary key (serial_number);
alter table blocks add constraint pk_blocks primary key (id);
alter table locations add constraint pk_locations primary key (id);

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
        u.deviation as unit_deviation
    from measurements as m
    join units as u on u.unit = m.unit
    join devices as d on d.serial_number = m.device_sn;

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
    declare 
        u units%ROWTYPE;
        d devices%ROWTYPE;
        b blocks%ROWTYPE;
        l locations%ROWTYPE;
    begin
        select * into u from units where units.unit = new.unit;
        select * into d from devices where devices.serial_number = new.serial_number;
        select * into b from blocks where blocks.id = new.block_id;
        select * into l from locations where locations.id = new.location_id;

        if  (u is not null and u.deviation != new.unit_deviation) or
            (d is not null and d.description != new.device_description) or
            (b is not null and b.description != new.block_description) or
            (l is not null and l.description != new.location_description)
        then
            -- raise notice 'row is not valid';
            return null;            
        end if;        
        
        if u is null then
            insert into units (unit, deviation) values (new.unit, new.unit_deviation);
        end if;
        if d is null then 
            insert into devices (serial_number, description) values (new.serial_number, new.device_description);
        end if;
        if b is null then
            insert into blocks (id, description) values (new.block_id, new.block_description);
        end if;
        if l is null then
            insert into locations (id, longitude, latitude, description) values (new.location_id, new.longitude, new.latitude, new.location_description);
        end if;
        insert into measurements (created, value1, value2, unit, block_id, device_sn, location_id) values (new.created, new.value1, new.value2, new.unit, new.block_id, new.serial_number, new.location_id);        
        return null;
    end;
$insert_raw_data$ language plpgsql;

-- ## TRIGGERS ## --
create trigger insert_raw_data
    instead of insert on raw_data_view
    for each row
    execute procedure insert_raw_data();

-- ## RULES ## --
create or replace rule measurements_on_duplicate_ignore as on insert to measurements
    where exists (
        select 1 from measurements where 
            created = new.created and value1 = new.value1 and
            value2 = new.value2 and unit = new.unit and
            block_id = new.block_id and device_sn = new.device_sn and
            location_id = new.location_id
    ) do instead nothing;