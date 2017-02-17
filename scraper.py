import re
import os
import sys

def skip_line(line):
    patterns = [
        r'^ *[[.*]] *$',
        r'Please Note:',
        r'Commercial (Airfare|Aircraft|Transportation)'
    ]
    for pattern in patterns:
        if re.search(pattern, line, flags=re.IGNORECASE):
            return True
    return False


def end_line(line):
    patterns = [
        r'^ *-+$',
        r' {113}0 {77}0'
    ]
    for pattern in patterns:
        if re.search(pattern, line, flags=re.IGNORECASE):
            return True
    return False

def get_lines(file, year, include_table_header=True, print_debug_lines=False):
    print(year)
    start_line = '-{107}\\\\2\\\\-{23}\\\\2\\\\'
    header_search_string = r'REPORTS? OF EXPENDITURES FOR '
    lines = []
    record_lines = False
    previous_line = ''
    current_name = ''
    header_line = ''
    for line in file:
        if re.search(header_search_string, line):
            header_line = line.strip()
        elif re.search(start_line, line):
            record_lines = True
        elif end_line(line):
            record_lines = False
        elif record_lines:
            if print_debug_lines:
                print(line)
            if skip_line(line):
                continue
            else:
                end_of_header_year = re.search(r'[0-9]{4}\.?$', header_line.strip())
                myYear = year
                if end_of_header_year:
                    myYear = end_of_header_year.group(0)[0:4]
                else:
                    print(header_line)
                values = get_columns(line, myYear)
                if(len(values) == 0):
                    continue
                if(values[0] == ''):
                    values[0] = current_name
                else:
                    current_name = values[0]
                if include_table_header:
                    values.append(header_line.strip())
                yield values
        else:
            continue

def get_honorific(nameValue):
    b = re.match(r'^[a-zA-Z]{2,}\.', nameValue)
    if b:
        return b.group(0)
    else:
        return ''

def clean_cell(value, default=''):
    """Removes repeated periods, trailing periods and strips leading and trailing whitespace."""
    value = re.sub(r'\.+$','', value.strip()).strip()
    if value == '':
        return default
    else:
        return value

def get_columns(line, year):
    """Extract the columns. Uses absolute spacing."""

    items = []
    # Get the representative's name
    name = clean_cell(line[0:39])
    items.append(name)

    honorific = get_honorific(name)
    items.append(honorific)

    # Get the arrival date
    arrival_date = clean_cell(line[43:48])
    if arrival_date == '':
        return []
    
    arrival_date += '/' + year
    items.append(arrival_date)

    # Get the departure date
    departure_date = clean_cell(line[55:60])
    if departure_date == '':
        return []
    departure_date += '/' + year
    items.append(departure_date)

    # Get the country
    country = clean_cell(line[63:88])
    items.append(country)

    return items

def write_header_line(out_file):
    items = ['name',
             'honorific',
             'arrival_date',
             'departure_date',
             'country',
             'table_header',
             'source_file']
    print(','.join(['"' + c + '"' for c in items]), file=out_file)

def process_a_file(file_name):
    """Processes a file returns rows through yield to make it iterable."""
    year = os.path.basename(file_name)[0:4]
    with open(file_name, 'r') as f:
        for line in get_lines(f, year):
            yield ','.join([ '"' + c + '"' for c in line])

def write_to_a_file(src_file, dest_file):
    """Writes one report to a file."""
    with open(dest_file, 'w') as f:
        for line in process_a_file(src_file):
            print(line, file=f)

def write_many_to_one(src_dir, output_filename):
    """Writes all of the reports from src_dir into output_filename"""
    with open(output_filename, 'w') as outfile:
        write_header_line(outfile)
        for src_file_name in os.listdir(src_dir):
            src_file_path = src_dir + src_file_name
            for line in process_a_file(src_file_path):
                print(line + ',"' + src_file_name + '"', file=outfile)

def write_many_to_many(src_dir, out_dir):
    """Processes each file and outputs to a file with the same name in the out_directory"""
    for src_file_name in os.listdir(src_dir):
        src_file_path = src_dir + src_file_name
        out_file_path = out_dir + src_file_name
        write_to_a_file(src_file_path, out_file_path)

def print_help():
    """Prints a simply help doc, and then exits the program."""
    print('usage: {source directory} {output filename}')
    sys.exit()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print_help()
    origin = sys.argv[1]
    dest = sys.argv[2]
    if os.path.isdir(origin) and os.path.isdir(dest):
        write_many_to_many(sys.argv[1], sys.argv[2])
    elif os.path.isdir(origin):
        write_many_to_one(origin, dest)
    else:
        write_to_a_file(origin,dest)
