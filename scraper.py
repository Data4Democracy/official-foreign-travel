##  See notes in Issues for more on this code and what more needs to be done.


test1 = '2014q2apr07.txt'
test2 = '2017q1jan09.txt'

import re
def  look_for_names(file, report):
    results = []
    for line in file:
        if re.search('Committee total', line):
            break
        line_split = line.split('  ')
        
        if len(line_split[0]) > 0 and re.match('\w', line_split[0]):
            #print(line_split[0])
            
            search_r = re.search('([\w.\s]+?)\.+$', line_split[0])
            
            traveler = search_r.group(1)
            
            dates = re.findall('(\d{,2}\/\d{,2})', line)
            arrival = dates[0]
            departure = dates[1]
            
            destination = re.search('\d\s+([a-zA-Z]+).+',line).group(1)
            
            d = {'table_desc': report,
                'traveler': traveler,
                'destination': destination,
                'arrival': arrival,
                'departure': departure}
            results.append(d)
            
    return results
    
with open(test1, 'r') as f:
    list_of_names = []
    for line in f:
        line = line.strip()
        if re.match('REPORT OF', line):
            print(line)
            report = line
        if line.strip().find('Name') == 0:
            list_of_names.append(look_for_names(f, report))


    print(list_of_names)
