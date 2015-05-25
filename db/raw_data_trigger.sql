set search_path to 'rdb';

-- smazani nevalidnich radku
delete from raw_data where created in (
select created from raw_data
	left outer join units on raw_data.unit = units.unit and raw_data.unit_deviation != units.deviation
	left outer join devices on raw_data.serial_number = devices.serial_number and raw_data.device_description != devices.description
	left outer join blocks on raw_data.block_id = blocks.id and  raw_data.block_description != blocks.description
where units.unit is not null or devices.serial_number is not null or blocks.id is not null);

-- vlozit neexistujici devices, units, ...
insert into units
	select * from first_unique_units();

insert into blocks
	select * from first_unique_blocks();

insert into devices
	select * from first_unique_devices();

insert into locations(id, longitude, latitude)
select distinct location_id, 0, 0 from raw_data;

-- smazani nekonzistentnich
delete from raw_data where created in (
select created from raw_data
	left outer join units on raw_data.unit = units.unit and raw_data.unit_deviation != units.deviation
	left outer join devices on raw_data.serial_number = devices.serial_number and raw_data.device_description != devices.description
	left outer join blocks on raw_data.block_id = blocks.id and  raw_data.block_description != blocks.description
where units.unit is not null or devices.serial_number is not null or blocks.id is not null);

insert into measurements(created, value1, value2, unit, block_id, device_sn, location_id)
select created, value1, value2, unit, block_id, serial_number, location_id from raw_data;