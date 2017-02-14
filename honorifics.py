import csv
import re

def copyHonorifics(input_filename, output_filename):
    with open(input_filename,'r') as csvinput:
        with open(output_filename, 'w') as csvoutput:
            writer = csv.writer(csvoutput, lineterminator='\n')
            reader = csv.reader(csvinput)

            all = []
            row = next(reader)
            row.insert(1,'honorific')
            all.append(row)

            for row in reader:
                h = GetHonorific(row[0])
                row.append(row.insert(1,h))
                all.append(row)
            writer.writerows(all)

def GetHonorific(nameValue):
    b = re.match(r'^[a-zA-Z]+\.', nameValue)
    if b:
        return b.group(0)
    else:
        return ''

if __name__ == '__main__':
    copyHonorifics('travel_report_data.csv', 'travel_report_data_2.csv')
