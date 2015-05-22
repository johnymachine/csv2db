-- psql -h 147.230.21.34 -U student -d RDB2015_DanielMadera -f create-view-raw-data.sql

set schema 'rdb';
CREATE VIEW raw_data_view AS
    SELECT 
        "timestamp" as created, m.unit as unit, l.id as location_id, longtitute, latitute, l.description as location_description, value1, 
        value2, u.deviation as unit_deviation, m.device_sn as device_sn, d.description as device_deviation, 
        m.block_id as block_id, b.description as block_description
    FROM measurements as m
    JOIN units as u on u.unit = m.unit
    JOIN devices as d on d.serial_number = m.device_sn
    JOIN blocks as b on b.id = m.block_id
    JOIN locations as l on l.id = m.location_id