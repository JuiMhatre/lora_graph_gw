import math
import itertools
import csv
import utm
from datetime import datetime
import pandas as pd
from multiprocessing import Pool
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy
import Graph
import re

def calculateDistance(x1,x2,y1,y2):
    return math.sqrt(math.pow(x1-x2,2)+math.pow(y1-y2,2))
    
def generateEdges(nodes,Max_Range,Max_Sensors):
    edges=readedges(nodes,Max_Sensors)
    if edges is not None:
        return edges
    edges=[[]for i in nodes]
    for curr_sensor in nodes:
        # curr_connected=0        
        edges[nodes.index(curr_sensor)] = list(map(lambda x: nodes.index(x),filter(lambda x: (x!=curr_sensor and (calculateDistance(curr_sensor[0],x[0],curr_sensor[1],x[1])<=Max_Range)),nodes)))
        # for sensor_to_test in nodes:
        #     if(sensor_to_test!=curr_sensor):
        #         if(calculateDistance(curr_sensor[0],sensor_to_test[0],curr_sensor[1],sensor_to_test[1])<=Max_Range):
        #             edges[nodes.index(curr_sensor)].append(nodes.index(sensor_to_test))
        #             curr_connected+=1
    saveedges(edges,Max_Sensors)
    return(edges)

def readedges(nodes,Max_Sensors):
    try:
        df = pd.read_csv('/home/jmhare1/gatewayPlacement/lora_graph_gw/Pre_Study/ConnectedComponent/savededges_sensor'+str(int(Max_Sensors))+'.csv',sep=",")
    except FileNotFoundError as e:
        return None
    edges = [[]for i in nodes]
    for index, row in df.iterrows():
        row.adj=row.adj.replace(']','')
        row.adj=row.adj.replace('[','')
        res=re.split(r',|-', row.adj)
        res = [int(i) for i in res]
        edges[index] = res
    return edges

def saveedges(edges,Max_Sensors):
    output = {"idx": [], "adj": []}
    idx=0
    for curr in edges:            
        output['idx'].append(idx)
        output['adj'].append(curr)
        idx +=1
    pd.DataFrame(data=output).to_csv('/home/jmhare1/gatewayPlacement/lora_graph_gw/Pre_Study/ConnectedComponent/savededges_sensor'+str(int(Max_Sensors))+'.csv')
    pass

def hata(sf,gw_height,sens_height):#returns distance in m
    # represents Spreading Factor Tolerances for Path Loss in dB
    plrange = [131, 134, 137, 140, 141, 144]
    distance = 10**(-(69.55+76.872985-13.82*math.log10(gw_height)-3.2*(math.log10(
        11.75*sens_height)**2)+4.97-plrange[sf-7])/(44.9-6.55*math.log10(gw_height)))
    return distance*1000

def create_placement(vars):
    Max_Sensors=vars[0]
    Sensors=vars[1]
    print(Max_Sensors)
    start=datetime.now()
    Gateways=[]
    Max_Range=hata(12,15,1)
    Min_Sensors=0
    Target_Coverage=100#%
    oldsensors=[i for i in Sensors]
    
    edges=generateEdges(oldsensors,Max_Range,Max_Sensors)
    graph = Graph.Graph(len(Sensors),edges,Max_Sensors)   
    connected_components=graph.connectedComponents()
    x = numpy.arange(len(connected_components))
    ys = [i+x+(i*x)**2 for i in range(len(connected_components))]
    colors = cm.rainbow(numpy.linspace(0, 1, len(ys)))
    # for cc,c  in zip(connected_components,colors):
    #     plot([Sensors[i] for i in cc],c,connected_components.index(cc))
    # plt.show()
    centeres_x_y_cc=[]
    cc_num=0
    for cc in connected_components:
            x= numpy.array([Sensors[i] for i in cc])[:,0]
            y= numpy.array([Sensors[i] for i in cc])[:,1]
            total_in_cc = len(cc)
            indices =[]
            counter =0
            while counter <=total_in_cc:
                indices.append(counter)
                counter +=Max_Sensors
            for i in indices:
                start =i
                end =  i+Max_Sensors if i + Max_Sensors < total_in_cc else total_in_cc
                centeres_x_y_cc.append([])
                centeres_x_y_cc[cc_num].append(sum(x)/len(cc))
                centeres_x_y_cc[cc_num].append(sum(y)/len(cc))
                centeres_x_y_cc[cc_num].append(cc)
                Gateways.append([centeres_x_y_cc[cc_num][0],centeres_x_y_cc[cc_num][1]])            
                cc_num +=1
    output = {"id": [], "x": [], "y": [], "height": [],"environment": []}
    for g in Gateways:
            latlon=utm.to_latlon(g[0],g[1],32,"U")
            output['id'].append(g)
            output['x'].append(latlon[1])
            output['y'].append(latlon[0])
            output['height'].append(5.0)
            output['environment'].append("urban")
            # jui print(g)

    # while(100-(len(oldsensors)/len(Sensors))*100<Target_Coverage):
    #     edges=generateEdges(oldsensors,Max_Range,Max_Sensors)
    #     if(len(edges)<1):
    #         break
    #     designatedgw=max(edges,key=len)
    #     if(len(designatedgw)<Min_Sensors):
    #         break
    #     Gateways.append(Sensors.index(oldsensors[edges.index(designatedgw)]))
    #     newsensors=[]
    #     for curr_sensor in oldsensors:   
    #         if(oldsensors.index(curr_sensor)!=edges.index(designatedgw) and oldsensors.index(curr_sensor) not in designatedgw):
    #             newsensors.append(curr_sensor)
    #     oldsensors=newsensors
    # output = {"id": [], "x": [], "y": [], "height": [],"environment": []}
    # for g in Gateways:
    #     latlon=utm.to_latlon(Sensors[g][0],Sensors[g][1],32,"U")
    #     output['id'].append(g)
    #     output['x'].append(latlon[1])
    #     output['y'].append(latlon[0])
    #     output['height'].append(5.0)
    #     output['environment'].append("urban")
    pd.DataFrame(data=output).to_csv('/home/jmhare1/gatewayPlacement/lora_graph_gw/Pre_Study/ConnectedComponent/files/gateways_Placement_Max_Sensors'+str(int(Max_Sensors))+'.csv')
    # Sensors_to_export=[[Sensors[i][0],Sensors[i][1],0,0,float("Inf"),0] for i in range(len(Sensors))]
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

    # for sens in Sensors_to_export:
    #     for g in Gateways:
    #         dist=calculateDistance(Sensors[g][0],sens[0],Sensors[g][1],sens[1])
    #         if(dist<sens[4]):
    #             sens[4]=dist
    #             sens[3]=g
    #             currsf=12
    #             for sf in range(12,6,-1):
    #                 if dist<hata(sf,15,1):
    #                     currsf=sf
    #             sens[2]=currsf
    #             sens[5]+=1
    # output = {"lon": [], "lat": [], "BestGW": [],"SF": [], "NumberOfSensors": [],"NumGWs":[]}
    # for sens in Sensors_to_export:
    #     if(sens[2]!=0):
    #         latlon=utm.to_latlon(sens[0],sens[1],32,"U")
    #         output['lat'].append(latlon[1])
    #         output['lon'].append(latlon[0])
    #         output['BestGW'].append(sens[3])
    #         output['SF'].append(sens[2])
    #         output['NumberOfSensors'].append(1)
    #         output['NumGWs'].append(sens[5])
    pd.DataFrame(data=output).to_csv('/home/jmhare1/gatewayPlacement/lora_graph_gw/Pre_Study/ConnectedComponent/files/reachable_sensors_Max_Sensors'+str(int(Max_Sensors))+'.csv')
    pd.DataFrame(data=output).to_json('/home/jmhare1/gatewayPlacement/lora_graph_gw/Pre_Study/ConnectedComponent/files/reachable_sensors_Max_Sensors'+str(int(Max_Sensors))+'.json')


if __name__ == "__main__":
    base_range=hata(12,15,1)
    Sensors=[]
    with open("/home/jmhare1/gatewayPlacement/lora_graph_gw/Pre_Study/ConnectedComponent/sensors.csv", newline='') as csvfile:
        data = list(csv.reader(csvfile))
        for curr in data:
            try:
                Sensors.append([float(curr[0]),float(curr[1])])
            except:
                pass
    with Pool(10) as p:
        devices_against_collision = p.map(create_placement, [[i,Sensors] for i  in range(300,3001,50)])
