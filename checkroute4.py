import re
import pandas as pd
from tabulate import tabulate
from rov import ROV

prefix_v4_regex = '\*>?\ ?\ (\d+.){1,3}\d+/?\d+'
route_list =[]
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
            print("\n\n")

def validate_routes():
    rov = ROV()
    rov.download_databases()
    rov.load_databases()
    for route, asn in route_list:
            asn = asn.replace('{', '').replace('}','')
            state = rov.check(route, int(asn))
            state["prefix"] = route
            state["origin_as"] = asn
            results.append(state)

def append_prefix(route):
    if route not in route_list:
        if route[0].split('.')[-1] == '0':
            route[0] = route[0] + '/24'
        if route[1] == '32768':
            route[1] = '3856'  
        route_list.append(route)

def main():
    with open('routing_data/ktm.txt', 'r') as file:
        data = file.readlines()
        for index, line in enumerate(data):
            if re.search(prefix_v4_regex, line):
                if len(line.split(' ')) < 3:
                        split_line = line.split(' ') + list(filter(lambda item: item, data[index+1].split(' ')))        
                else:
                    split_line = list(filter(lambda item: item, line.split(' '))) 
                append_prefix([split_line[1].strip(), split_line[-2].strip()])
    file.close()
    validate_routes()
    print_results()
                
if __name__ == '__main__':
    main()
    