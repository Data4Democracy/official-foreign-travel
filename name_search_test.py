import re
import os
import sys

import name_search
import scraper
import pickle

def search_many(src_dir, log_file_name):
    """Writes all of the reports from src_dir into output_filename"""
    pkl = os.path.isfile('names_index.pickle')
    if pkl:
        with open('names_index.pickle','rb') as f:
            charset, members_list, members_dict, members_index = \
                    pickle.load(f)
    else:
        charset, members_list, members_dict, members_index = \
                name_search.initialize()
        with open('names_index.pickle','wb') as f:
            pickle.dump((charset, members_list, members_dict, members_index), f)

    count = 0
    with open(log_file_name, 'w') as logfile:
        for src_file_name in os.listdir(src_dir):
            count += 1
            print(count, src_file_name)
            src_file_path = src_dir + src_file_name
            for line in scraper.process_a_file(src_file_path):
                t = [s[1:-1] for s in line.split(',')[:4]]
                try:
                    if (t[0].startswith('Hon')) or (t[0].startswith('Speaker')):
                        ret = name_search.search_by_name(t[0], t[2], t[3], \
                                members_index, charset)
                        if ret[0][1] < 3:
                            print('Missing {0}: {1}, {2}'.format(src_file_name, line, ret), file=logfile)
                        elif (len(ret)>1) and (ret[1][1]*1.1 > ret[0][1]):
                            print('Inconcl. {0}: {1}, {2}'.format(src_file_name, line, ret), file=logfile)
                except Exception as e:
                    print('ERROR {0}: {1}, {2}'.format(src_file_name, t, e), file=logfile)

def print_help():
    """Prints a simply help doc, and then exits the program."""
    print('usage: {source directory} {output filename}')
    sys.exit()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print_help()
    search_many(sys.argv[1], sys.argv[2])
