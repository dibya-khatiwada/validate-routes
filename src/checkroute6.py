import re
import pandas as pd
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
        asn = asn.replace('{', '').replace('}','')
        state = rov.check(route, int(asn))
        state["prefix"] = route
        state["origin_as"] = asn
        results.append(state)        

def append_prefix(route):   
        if route[1] == '32768':
            route[1] = '3856'        
        route_list.append(route)

def main():
    with open('../routing_data/ktm6.txt', 'r') as file:
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
    
