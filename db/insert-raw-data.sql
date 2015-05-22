-- psql -h 147.230.21.34 -U student -d rdb2015_danielmadera -f insert-raw-data.sql

set schema 'rdb';

insert into raw_data_view (
        created, 
        unit, 
        location_id, 
        longitude, 
        latitude, 
        location_description, 
        value1, 
        value2, 
        unit_deviation, 
        serial_number, 
        device_description, 
        block_id, 
        block_description
    ) values (
        '2015-05-15 15:15:00',
        'A',
        2,
        31813.000,
        2116.000,
        'prutok b2',
        180422.000,
        129.000,
        0.015,
        '2548DESWE-87-874/4',
        'WEIGHT METER',
        6,
        'Voltage in dam 3'
    ),
    (
        '2015-05-15 15:15:00',
        'A',
        2,
        31813.000,
        2116.000,
        'prutok b2',
        12.000,
        129.000,
        0.015,
        '2548DESWE-87-874/4',
        'WEIGHT METER',
        6,
        'Voltage in dam 3'
    ),
    (
        '2015-05-15 15:15:00',
        'A',
        2,
        31813.000,
        2116.000,
        'prutok b2',
        1222.000,
        129.000,
        0.015,
        '2548DESWE-87-874/4',
        'WEIGHT METER',
        6,
        'Voltage in dam 3'
    );