import re
import pandas as pd
import numpy as np
from tabulate import tabulate
from rov import ROV


pd.set_option('display.max_columns', None)



prefix_v6_regex = '\*>?\ ?\ \d+[a-zA-Z]*'
route_list =[]
results = []

def print_results():
    pd.set_option('display.max_columns', None)
    df = pd.DataFrame(results)
    states = ['Valid', 'Invalid', 'NotFound', 'Invalid,more-specific']
    print(f"\nTotal Number of Processesed Prefixes: {len(route_list)}")
    for state in states:
        for adjstate in states:
            new_df = df[(df['irr'] == state) & (df['rpki'] == adjstate)]
            new_df.index = np.arange(1, len(new_df)+1)
            print (f"IRR - {state}, RPKI - {new_df.prefix.count()} prefixes")
            print("============================================================================================")
            if new_df.prefix.count() != 0:
                print(tabulate(new_df, headers = 'keys', tablefmt = 'psql'))
            print("\n\n")

def validate_routes():
    rov = ROV()
    rov.download_databases()
    rov.load_databases()
    for route, asn in route_list:
        try:
            # print(route,asn)
            state = rov.check(route, int(asn))
            state["prefix"] = route
            state["origin_as"] = asn
            results.append(state)
        except TypeError:
            print(f"Invalid prefix ASN pair ! : {route}, {asn}")   


def check_route(prefix):
    if  re.search('(\d?[a-z]?)+:.*\/\d+', prefix):
        return(prefix)        
    else:
        print(f"Error! : Invalid Prefix - " + prefix)
        

def check_asn(asn):
    if re.search('^\d+', asn):
        if asn == '32768':
            asn = '3856'
        return int(asn)
    else:
        print("Error! : Invalid ASN - " + str(asn))
        
def append_prefix(route):
    prefix = check_route(route[0])
    asn = check_asn(route[1])
    route_list.append([prefix,asn])
    

def main():
    with open('../routing_data/fra6.txt', 'r') as file:
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
    file.close()
    validate_routes()
    print_results()         

if __name__ == '__main__':
    main()