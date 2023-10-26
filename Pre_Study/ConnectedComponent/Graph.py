import sys
class Graph:
    def __init__(self, vertices,edges,MaxSensors):
        self.V = vertices
        self.adj = edges
        self.maxsensor = MaxSensors
    def DFS(self,temp,s,visited):            
        stack = []
        stack.append(s) 
        if len(temp) >=self.maxsensor:
            return temp
        temp.append(s)        
        while (len(stack)): 
            s = stack[-1]             
            stack.pop() 
            if (not visited[s]): 
                visited[s] = True 
            for node in self.adj[s]: 
                if (not visited[node] and self.isConnectedToTemp(temp,node)): 
                    if node not in temp:
                        temp.append(node)
                    stack.append(node)
        return temp
                    
    def isConnectedToTemp(self, temp, node):
        for t in temp:
            if t not in self.adj[node]:
                return False;
        return True; 
    def DFSUtil(self, temp, v, visited):
        connected_to_all=True
        for t in temp:
            if t not in self.adj[v]:
                connected_to_all = False
                break
        if not connected_to_all :
            return temp
        visited[v] = True
        temp.append(v) 
        for i in self.adj[v]:
            if visited[i] == False:
                temp = self.DFS(temp, i, visited)
        return temp

    def connectedComponents(self):
        visited = []
        cc = []
        vnum = self.V
        for i in range(vnum):
            visited.append(False)
        for v in range(vnum):
            if visited[v] == False:
                temp = []
                cc.append(self.DFS(temp, v, visited))
        # self.combileComponents(cc)
        return cc
    
    
