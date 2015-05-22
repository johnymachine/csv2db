-- psql -h 147.230.21.34 -u student -d rdb2015_danielmadera -f insert-raw-data.sql

insert into raw_data_view (
        created, 
        unit, 
        location_id, 
        longitute, 
        latitute, 
        location_description, 
        value1, 
        value2, 
        unit_deviation, 
        serial_number, 
        device_description, 
        block_id, 
        block_description
    ) values (
        '1431528412',
        'A',
        '2',
        '31813.000',
        '2116.000',
        'prutok b2',
        '18041.000',
        '129368.000',
        '0.015',
        '2548DESWE-87-874/4',
        'WEIGHT METER',
        '6',
        'Voltage in dam 3'
    );