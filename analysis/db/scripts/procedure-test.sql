create type parsed_values as (id integer, description text);
create or replace function parse_csv( TEXT ) RETURNS setof parsed_values as $$
my $source = shift;
my @rows = split /\r?\n/, $source;
my @reply = ();
for my $row (@rows) {
    my @values = ();
    while ( $row =~ s/("(?:[^"]|"")*"|[^",]*)(,|$)// ) {
        my $single_value = $1;
        $single_value =~ s/^"//;
        $single_value =~ s/"$//;
        $single_value =~ s/""/"/g;
        push @values, $single_value;
        last if '' eq $row;
    }
    push @reply, {
        "catid" => $values[0],
        "whatever" => $values[1],
    };
}
return \@reply;
$$ language plpython;