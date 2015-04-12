create or replace function parse_csv(input_csv text)
  returns text
AS $$
    return input_csv
$$ LANGUAGE plpythonu;
