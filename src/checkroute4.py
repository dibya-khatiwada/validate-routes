import re
import pandas as pd
import numpy as np
from tabulate import tabulate
from rov import ROV


prefix_v4_regex_line = '\*>?\=?\ ?\ (\d+.){1,3}\d+/?\d+'
route_list =[]
results = []

def print_results():
    pd.set_option('display.max_columns', None)
    df = pd.DataFrame(results)
    states = ['Valid', 'Invalid', 'NotFound', 'Invalid,more-specific']
    print(f"\nTotal Number of Processesed Prefixes: {len(route_list)}")
    print("-------------------------------------------------------------------------")
    for state in states:
        for adjstate in states:
            new_df = df[(df['irr'] == state) & (df['rpki'] == adjstate)]
            new_df.index = np.arange(1, len(new_df)+1)
            print (f"IRR - {state}, RPKI - {adjstate} : {new_df.prefix.count()} prefixe(s)")
            print("-------------------------------------------------------------------------")
            if new_df.prefix.count() != 0:
                print(tabulate(new_df, headers = 'keys', tablefmt = 'psql'))
            print("\n\n")

def validate_routes():
    rov = ROV()
    rov.download_databases()
    rov.load_databases()
    for route, asn in route_list:
            state = rov.check(route, asn)
            state["prefix"] = route
            state["origin_as"] = asn
            results.append(state)

def check_route(prefix):
    if  re.search('(\d+.){1,3}\d+\/?(\d+)?', prefix):
        if prefix.split('.')[-1] == '0':
            prefix = prefix + '/24'
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
    with open('../routing_data/ktm.txt', 'r',16000) as file:
        data = file.readlines()
        for index, line in enumerate(data):
            if re.search(prefix_v4_regex_line, line):
                if len(list(filter(lambda item: item, line.split(' ')))) < 3:
                    # print(line)
                    split_line = list(filter(lambda item: item, line.split(' ')))  + list(filter(lambda item: item, data[index+1].split(' ')))   
                            
                else:
                    split_line = list(filter(lambda item: item, line.split(' '))) 
                append_prefix([split_line[1].strip(), split_line[-2].strip()])
    file.close()
    validate_routes()
    print_results()
                
if __name__ == '__main__':
    main()
    
