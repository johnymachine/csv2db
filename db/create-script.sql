-- psql -h 147.230.21.34 -U student -d RDB2015_DanielMadera -f create-script.sql

drop schema if exists "rdb" cascade;
create schema "rdb";
set schema 'rdb';

create table "raw_data" (
    "timestamp" timestamp not null, 
    "unit" character varying(30) not null,
    "location_id" integer not null,
    "longtitute" real not null,
    "latitute" real not null, 
    "location_description" character varying(250),
    "value1" real not null,
    "value2" real not null,
    "unit_deviation" real not null,
    "device_sn" character varying(80) not null,
    "device_deviation" real not null,
    "device_description" character varying(250),
    "block_id" integer not null,
    "block_description" character varying(250)
);

create table "measurements" (
    "id" serial,
    "timestamp" timestamp not null,
    "value1" real not null,
    "value2" real not null,
    "unit" character varying(30) not null,
    "block_id" integer not null,
    "device_sn" character varying(80) not null
) with (oids=false);

create table "units" (
    "unit" character varying(30) not null,
    "deviation" real not null
) with (oids=false);

create table "devices" (
    "serial_number" character varying(80) not null,
    "description" character varying(250)
) with (oids=false);

create table "blocks" (
    "id" integer not null,
    "description" character varying(250)
) with (oids=false);

create table "locations" (
    "id" integer not null,
    "longtitute" real not null,
    "latitute" real not null,
    "description" character varying(250)
) with (oids=false);

alter table "measurements" add constraint "pk_measurements" primary key ("id");
alter table "units" add constraint "pk_units" primary key ("unit");
alter table "devices" add constraint "pk_devices" primary key ("serial_number");
alter table "blocks" add constraint "pk_blocks" primary key ("id");
alter table "locations" add constraint "pk_locations" primary key ("id");

alter table "measurements" add constraint "measurement_unit" foreign key ("unit") references "units" ("unit") on delete restrict on update cascade;
alter table "measurements" add constraint "measurement_block" foreign key ("block_id") references "blocks" ("id") on delete cascade on update cascade;
alter table "measurements" add constraint "measurement_device" foreign key ("device_sn") references "devices" ("serial_number") on delete restrict on update cascade;
alter table "measurements" add constraint "measurement_location" foreign key ("block_id") references "locations" ("id") on delete restrict on update cascade;

create index "ix_measurement_unit" on "measurements" ("unit");
create index "ix_measurement_block" on "measurements" ("block_id");
create index "ix_mesurememnt_device" on "measurements" ("device_sn");
create index "ix_mesuremement_location" on "measurements" ("block_id");
