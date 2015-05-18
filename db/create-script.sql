DROP DATABASE IF EXISTS "RDB2015_DanielMadera";
CREATE DATABASE "RDB2015_DanielMadera"
    WITH OWNER "student"
    ENCODING 'UTF8' 
    TEMPLATE template0;
    
create table "raw_data" (
    "timestamp" timestamp not null, 
    "unit" character varying(30) not null,
    "id" integer not null,
    "longtitute" real not null,
    "latitute" real not null, 
    "location_description" character varying(250),
    "value1" real not null,
    "value2" real not null,
    "unit_deviation" real not null,
    "device_sn" character varying(80) not null,
    "device_deviation" real not null,
    "device_description" character varying(250),
    "id" integer not null,
    "block_description" character varying(250)
);

create table "mesurements" (
    "id" integer not null,
    "timestamp" timestamp not null,
    "value1" real not null,
    "value2" real not null,
    "unit" character varying(30) not null,
    "blok_id" integer not null,
    "device_sn" character varying(80) not null
) with (oids=false);

create table "units" (
    "unit" character varying(30) not null,
    "deviation" real not null
) with (oids=false);

create table "devices" (
    "serial_number" character varying(80) not null,
    "deviation" real not null,
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
    
) with (oids=false);

alter table "mesurements" add constraint "pk_mesurements" primary key ("id");
alter table "units" add constraint "pk_units" primary key ("unit");
alter table "devices" add constraint "pk_devices" primary key ("serial_number");
alter table "blocks" add constraint "pk_blocks" primary key ("id");
alter table "locations" add constraint "pk_locations" primary key ("id");

alter table "mesurements" add constraint "mesurement_unit" foreign key ("unit") references "units" ("unit") on delete restrict on update cascade;
alter table "mesurements" add constraint "mesurement_blok" foreign key ("block_id") references "blocks" ("id") on delete cascade on update cascade;
alter table "mesurements" add constraint "mesurement_device" foreign key ("device_sn") references "devices" ("serial_number") on delete restrict on update cascade;
alter table "mesurements" add constraint "mesurement_location" foreign key ("block_id") references "locations" ("id") on delete restrict on update restrict;

create index "ix_mesurement_unit" on "mesurements" ("unit");
create index "ix_mesurement_blok" on "mesurements" ("block_id");
create index "ix_mesurememnt_device" on "mesurements" ("device_sn");
create index "ix_mesuremement_location" on "mesurements" ("block_id");