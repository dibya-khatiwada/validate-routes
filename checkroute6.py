import re
import pandas as pd
from tabulate import tabulate
from rov import ROV

pd.set_option('display.max_columns', None)



prefix_v6_regex = '\*>?\ ?\ \d+[a-zA-Z]*'
prefix_list =[]
results = []



def print_results():
    pd.set_option('display.max_columns', None)
    df = pd.DataFrame(results)
    states = ['Valid', 'Invalid', 'NotFound', 'Invalid,more-specific']
    for state in states:
        for adjstate in states:
            print (f"IRR - {state}, RPKI - {adjstate}: {df[(df['irr'] == state) & (df['rpki'] == adjstate)].prefix.count()} prefixes")
            print("============================================================================================")
            if df[(df['irr'] == state) & (df['rpki'] == adjstate)].prefix.count() != 0:
                print(tabulate(df[(df['irr'] == state) & (df['rpki'] == adjstate)], headers = 'keys', tablefmt = 'psql'))
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print("\n\n")

def validate_prefix():
    rov = ROV()
    rov.download_databases()
    rov.load_databases()

    for prefix, asn in prefix_list:
        # print(prefix)
        state = rov.check(prefix, int(asn))
        state["prefix"] = prefix
        state["origin_as"] = asn
        results.append(state)        


def append_prefix(prefix):           
        prefix_list.append(prefix)

def main():
    
    with open('routing_data/ktm6.txt', 'r') as file:
        data = file.readlines()
        for index, line in enumerate(data):
            if re.search(prefix_v6_regex, line):
                line = list(filter(lambda item: item, line.split(' ')))
                if len(line) <= 3:
                    while line[-1] != 'i\n':
                        line = (line + list(filter(lambda item: item, data[index+1].split(' '))))
                        index +=1
                    append_prefix([line[1].strip(), line[-2].strip()])
                    
                else:
                    append_prefix([line[1].strip(), line[-2].strip()])
                   
    # for prefix, asn in prefix_list:
    #     print(prefix, asn)
    
    file.close()
    validate_prefix()
    print_results()
    
    
    
            

if __name__ == '__main__':
    main()
    