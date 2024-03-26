from pulp import LpVariable, LpProblem, LpMinimize, lpSum, value,LpStatus
import pandas as pd
import math
import re
import csv
import utm
import numpy as np
def calculateDistance(x1,x2,y1,y2):
    return math.sqrt(math.pow(x1-x2,2)+math.pow(y1-y2,2))
def distance(demand_point, facility_location):
    return ((demand_point[0] - facility_location[0]) ** 2 + (demand_point[1] - facility_location[1]) ** 2) ** 0.5
def generateEdges(nodes,Max_Sensor):
    edges=readedges(nodes,Max_Sensor)
    if edges is not None:
        return edges
    n = len(nodes)  # Number of potential facility locations

    # Calculate distance matrix
    edges = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            edges[i, j] = math.sqrt((nodes[i][0]-nodes[j][0])**2 + (nodes[i][1]-nodes[j][1])**2)

    saveedges(edges,Max_Sensor)
    return(edges)

def readedges(nodes,Max_Sensor):
    try:
        df = pd.read_csv("D:\Assignments\Algo\impl\lora_graph_gw\Pre_Study\Pmedian\savededges_Sensors"+str(Max_Sensor)+".csv",sep=",")
    except FileNotFoundError as e:
        return None
    edges = [[]for i in nodes]
    for index, row in df.iterrows():
        row.adj=row.adj.replace(']','')
        row.adj=row.adj.replace('[','')
        row.adj=row.adj.replace('\n','')
        row.adj=row.adj.replace('\'','')
        res=re.split(r' ', row.adj)
        res = [float(i) for i in res if len(i)>0]
        edges[index] = res
    return edges

def saveedges(edges,Max_Sensor):
    output = {"idx": [], "adj": []}
    idx=0
    for curr in edges:            
        output['idx'].append(idx)
        output['adj'].append(curr)
        idx +=1
    pd.DataFrame(data=output).to_csv("D:\Assignments\Algo\impl\lora_graph_gw\Pre_Study\Pmedian\savededges_Sensors"+str(Max_Sensor)+".csv")
    pass


def hata(sf,gw_height,sens_height):#returns distance in m
    # represents Spreading Factor Tolerances for Path Loss in dB
    plrange = [131, 134, 137, 140, 141, 144]
    distance = 10**(-(69.55+76.872985-13.82*math.log10(gw_height)-3.2*(math.log10(
        11.75*sens_height)**2)+4.97-plrange[sf-7])/(44.9-6.55*math.log10(gw_height)))
    return distance*1000

def create_placement(vars):
    Max_Sensor=vars[0]
    Sensors=vars[1]
    distances=generateEdges(Sensors,Max_Sensor)
    Sensors=[(1, 2), (3, 5), (7, 8), (9, 10)]
    n=len(Sensors)
    num_facilities=10
   
    prob = LpProblem("p_median_problem", LpMinimize)

    facility_locations = [(i, j) for i in range(num_facilities) for j in range(num_facilities)]

    facilities = LpVariable.dicts("Facility", facility_locations, cat='Binary')
    assignment = LpVariable.dicts("Assign", [(i, j) for i in Sensors for j in facility_locations], cat='Binary')

    prob += lpSum([assignment[(i, j)] * distance(i, j) for i in Sensors for j in facility_locations])

    # Demand point assignment constraints
    for i in Sensors:
        prob += lpSum([assignment[(i, j)] for j in facility_locations]) == 1

    # Facility opening constraints
    for j in facility_locations:
        prob += lpSum([assignment[(i, j)] for i in Sensors]) <= len(Sensors) * facilities[j]

    # Sensor constraints
    for j in facility_locations:
        prob += lpSum([assignment[(i, j)] for i in Sensors]) <= Max_Sensor


    prob.solve()


    Gateways=[]
    output=[]
    # Print results
    print("Status:", LpStatus[prob.status])
    print("Optimal facility locations:")
    for j in facilities:
        if value(facilities[j]) > 0.5:
            print("Facility:", j)
    print("Optimal assignment of demand points to facilities:")
    for i in Sensors:
        for j in facilities:
            if value(assignment[(i, j)]) > 0.5:
                print(f"Assign demand point {i} to facility {j}")
        for g in Gateways:
            latlon=utm.to_latlon(g[0],g[1],32,"U")
            output['id'].append(g)
            output['x'].append(latlon[1])
            output['y'].append(latlon[0])
            output['height'].append(5.0)
            output['environment'].append("urban")
            # jui print(g)
    pd.DataFrame(data=output).to_csv('D:\Assignments\Algo\impl\lora_graph_gw\Pre_Study\Pmedian/files\S2\gateways_Placement_Range_sensor'+str(int(Max_Sensor))+'.csv')
    Sensors_to_export=[[Sensors[i][0],Sensors[i][1],0,0,float("Inf"),0] for i in range(len(Sensors))]
    for sens in Sensors_to_export:
        for g in Gateways:
            dist=calculateDistance(g[0],sens[0],g[1],sens[1])
            if(dist<sens[4]):
                sens[4]=dist
                sens[3]=g
                currsf=12
                for sf in range(12,6,-1):
                    if dist<hata(sf,15,1):
                        currsf=sf
                sens[2]=currsf
                sens[5]+=1
    output = {"lon": [], "lat": [], "BestGW": [],"SF": [], "NumberOfSensors": [],"NumGWs":[]}
    for sens in Sensors_to_export:
        if(sens[2]!=0):
            latlon=utm.to_latlon(sens[0],sens[1],32,"U")
            output['lat'].append(latlon[1])
            output['lon'].append(latlon[0])
            output['BestGW'].append(sens[3])
            output['SF'].append(sens[2])
            output['NumberOfSensors'].append(1)
            output['NumGWs'].append(sens[5])
    pd.DataFrame(data=output).to_csv('D:\Assignments\Algo\impl\lora_graph_gw\Pre_Study\Pmedian/files\S2/reachable_sensors_Range_sensor'+str(int(Max_Sensor))+'.csv')
    pd.DataFrame(data=output).to_json('D:\Assignments\Algo\impl\lora_graph_gw\Pre_Study\Pmedian/files\S2/reachable_sensors_Range_sensor'+str(int(Max_Sensor))+'.json')


if __name__ == "__main__":
    base_range=hata(12,15,1)
    Sensors=[]
    with open("D:\Assignments\Algo\impl\lora_graph_gw\Pre_Study\Pmedian\sensors.csv", newline='') as csvfile:
        data = list(csv.reader(csvfile))
        for curr in data:
            try:
                Sensors.append((float(curr[0]),float(curr[1])))
            except:
                pass
    create_placement([100,Sensors])
