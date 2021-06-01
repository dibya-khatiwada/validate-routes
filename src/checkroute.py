import re
import pandas as pd
import numpy as np
from tabulate import tabulate
import ipaddress
from rov import ROV

prefix_v4_regex_line = '\*>?\=?\ ?\ (\d+\.){1,3}\d+\/?\d+'
prefix_v6_regex_line = '\*>?\=?\ ?\ \d+[a-zA-Z]*:.*\/\d+'

def print_results():
    pd.set_option('display.max_columns', None)
    df = pd.DataFrame(results)
    states = ['Valid', 'Invalid', 'NotFound', 'Invalid,more-specific']
    print(f"\nTotal Number of Processesed Prefixes: {len(route_list)}")
    print("+----+-------+--------+------------------+-------------+-------------+")
    for state in states:
        for adjstate in states:
            new_df = df[(df['irr'] == state) & (df['rpki'] == adjstate)]
            new_df.index = np.arange(1, len(new_df)+1)
            if new_df.prefix.count() != 0:
                print (f"IRR - {state}, RPKI - {adjstate} : {new_df.prefix.count()} prefixes")
                print("+----+-------+--------+------------------+-------------+-------------+")
                print ("Top 20 ASNs by count: ")
                print(tabulate(new_df.groupby('origin_as').count().sort_values(by='prefix', ascending=False).\
                    nlargest(20, 'prefix')[["prefix"]].rename(columns={"prefix":"pfxcnt"}), headers='keys',tablefmt='github'))
                print("\n+----+-------+--------+------------------+-------------+-------------+\n")
                print(tabulate(new_df, headers = 'keys', tablefmt = 'github'))
                print('\n')
    print("+----+-------+--------+------------------+-------------+-------------+")
    print("Bogon Annoucements or ASN in the AS-PATH")
    bg_df = df[(df['bogon'] == True)] 
    bg_df.index = np.arange(1, len(bg_df)+1)
    print(tabulate(bg_df, headers='keys', tablefmt='github'))
    

def initialize_radixtree():
    global rov
    rov = ROV()
    rov.download_databases()
    rov.load_databases()

def validate_routes():
    for route, asn,bogon_flag in route_list:
        state = rov.check(route, asn)
        state["prefix"] = route
        state["origin_as"] = asn
        state["bogon"] = bogon_flag
        results.append(state)

def check_route(prefix):
    if  re.search('(\d+.){1,3}\d+\/?(\d+)?', prefix):
        if prefix.split('.')[-1] == '0':
            prefix = prefix + '/24'
        return(prefix)  
    elif  re.search('(\d?[a-z]?)+:.*\/\d+', prefix):
        return(prefix)
    else:
        print(f"Error! : Invalid Prefix - " + prefix)
        
def check_asn(asn):
    x = re.findall('\d+', asn)
    if len(x) > 1:
        asn = x[-1]
    else:
        asn = x[0]
    if asn == '32768':
        asn = '3856'
    return int(asn)

def check_bogon(route):
    bogon_flag = False
    BOGON_ASNS = [0, 23456, range(64496,131073), range(4200000000,4294967296)]
    if route[1] in BOGON_ASNS or route[1] in BOGON_ASNS[2] or route[1] in BOGON_ASNS[3] or not ipaddress.ip_network(route[0]).is_global:
       bogon_flag  = True
    return bogon_flag
    
def append_prefix(route):
    prefix = check_route(route[0])
    asn = check_asn(route[1])
    bogon_flag =  check_bogon([prefix, asn])
    route_list.append([prefix,asn,bogon_flag])

def main():
    initialize_radixtree()
    while True:
        try:
            bgp_file = input("Enter the file name..: ") ## Files are located in ../routing_data/
            if bgp_file:
                global route_list, results 
                route_list, results = [],[]
                with open(f'../routing_data/{bgp_file}', 'rt') as file:
                    data = file.readlines()        
                    for index, line in enumerate(data):
                        splitted_line = list(filter(lambda item: item, line.split(' ')))
                        if re.search(prefix_v4_regex_line, line):
                            if len(splitted_line) < 3:
                                splitted_line = splitted_line  + list(filter(lambda item: item, data[index+1].split(' ')))                           
                            append_prefix([splitted_line[1].strip(), splitted_line[-2].strip()]) 
                        
                        elif re.search(prefix_v6_regex_line, line):
                            if len(splitted_line) <= 3:
                                while splitted_line[-1] != 'i\n':
                                    splitted_line = (splitted_line + list(filter(lambda item: item, data[index+1].split(' '))))
                                    index +=1
                                    if splitted_line[-1] == '?\n':
                                        break
                                    
                            append_prefix([splitted_line[1].strip(), splitted_line[-2].strip()])      

                file.close()
                validate_routes()
                print_results()

        except FileNotFoundError:
            print("Unable to locate file !")
             
if __name__ == '__main__':
    main()
    
