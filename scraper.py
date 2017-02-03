import re
import os
import sys

def get_lines(file, include_table_header=False, print_debug_lines=False):
    start_line = '-{107}\\\\2\\\\-{23}\\\\2\\\\'
    end_line= r' +-+'
    end_line2 = '                                                                                                                 0                                                                             0'
    header_search_string = 'REPORT OF EXPENDITURES FOR OFFICIAL'
    lines = []
    record_lines = False
    previous_line = ''
    current_name = ''
    header_line = ''
    year = ''
    for line in file:
        if re.search(header_search_string, line):
            header_line = line.strip()
            year = header_line.split(' ')[-1]
        elif re.search(start_line, line):
            record_lines = True
        elif re.search(end_line, line):
            record_lines = False
        elif re.search(end_line2, line):
            record_lines = False
        elif record_lines:
            if re.search(r'^ *[[.*]] *$', line):
                continue
            else:
                values = get_columns(line, year)
                if(values[0] == ''):
                    values[0] = current_name
                else:
                    current_name = values[0]
                if include_table_header:
                    values.append(header_line.strip())
                yield values
        else:
            continue
        if print_debug_lines:
            print(line)
    
def clean_cell(value, default=''):
    """Removes trailing periods and strips leading and trailing whitespace."""
    value = re.sub(r'\.+$','', value).strip()
    if value == '':
        return default
    else:
        return value

def get_columns(line, year):
    """Extract the columns. Uses absolute spacing."""
    items = []
    name = clean_cell(line[0:39])
    items.append(name)
    arrival_date = clean_cell(line[43:48]) + '/' + year
    items.append(arrival_date)
    departure_date = clean_cell(line[55:59]) + '/' + year
    items.append(departure_date)
    country = clean_cell(line[63:88])
    items.append(country)
    per_diem = clean_cell(line[103:114], default='0.00')
    items.append(per_diem)
    transportation = clean_cell(line[129:140], default='0.00')
    items.append(transportation)
    other = clean_cell(line[155:166], default='0.00')
    items.append(other)
    return items

def process_a_file(file_name):
    """Processes a file returns rows through yield to make it iterable."""
    with open(file_name, 'r') as f:
        for line in get_lines(f):
            yield ','.join([ '"' + c + '"' for c in line])

def write_to_a_file(src_file, dest_file):
    """Writes one report to a file."""
    with open(dest_file, 'w') as f:
        for line in process_a_file(src_file):
            print(line, file=f)

def write_many_to_one(src_dir, output_filename):
    """Writes all of the reports from src_dir into output_filename"""
    with open(output_filename, 'w') as outfile:
        for src_file_name in os.listdir(src_dir):
            src_file_path = src_dir + src_file_name
            for line in process_a_file(src_file_path):
                print(line + ',"' + src_file_name + '"', file=outfile)

# process_a_file('expenditures/2017q1jan09.txt')
# process_a_file('expenditures/2014q2apr07.txt')

def print_help():
    """Prints a simply help doc, and then exits the program."""
    print('usage: {source directory} {output filename}')
    sys.exit()

if __name__ == "__main__":
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print_help()
    write_many_to_one(sys.argv[1], sys.argv[2])
        
