drop type if exists parsed_values;
drop function if exists parse_csv(text);
create type parsed_values as (id text, name text);
create function parse_csv(input_csv text)
  returns setof parsed_values
AS $$
   import csv
   items_set = []
   reader = csv.reader(input_csv.strip().split('\n'), delimiter=',')
   for row in reader:
       items = [item.strip() for item in row]
       items_set.append(items)
   return items_set    
$$ LANGUAGE plpythonu;