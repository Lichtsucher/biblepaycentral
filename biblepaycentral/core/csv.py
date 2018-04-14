class BrokenCSV(Exception):
    pass

def pool_cvs_to_list(raw):
    """ converts a cvs file form the pool to a valid python list/dict combination.
        It also ignores anything after the last line and the special <ROW> ending of
        every line

        Original:
        id|RosettaID|Username|<ROW>
        5d8a505e-efbc-4dce-8113-02b10f2c83b5|1987449|Ponfarriac|<ROW>

        Result:
        [
            {
                'id': '5d8a505e-efbc-4dce-8113-02b10f2c83b5',
                'Username': 'Ponfarriac',
                'RosettaID': '1987449',
            }
        ]

        """

    # first, we look for the last "|<ROW>". Everything after that is junk
    last_pos = raw.rfind('|<ROW>')
    raw = raw[0:last_pos]

    # the lines are marked by an ending |<ROW>', so we split them by that
    raw_lines = raw.split('|<ROW>')

    # we don't like empty lists
    if len(raw_lines) < 2:
        raise BrokenCSV

    # we need to extract the header line, we use it later to build the dict
    # of every line. There will be no header-line itself in the result
    raw_header = raw_lines.pop(0).strip().replace('|<ROW>', '').split('|')

    lines = []
    for raw_line in raw_lines:
        line_data = raw_line.strip().split('|')

        line = {}
        for pos, header in enumerate(raw_header):
            line[header] = line_data[pos]

        lines.append(line)

    return lines