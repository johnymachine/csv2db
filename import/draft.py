def parse_csv(filename, row_count):
    # otevru soubor
    # rozparsovani
    with open(filename) as f:
        for row_set in f:
            data = parse(row_set)
            yield data

# pouziti
for data_set in parse_csv():
    # poslat do db
    