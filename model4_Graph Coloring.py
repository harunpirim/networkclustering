from gurobipy import *
import random
import pandas as pd
import math
import numpy as np
import csv
import random
import matplotlib.pyplot as plt
import networkx as nx

# #-------------------------------------------------------#
# #                 defining set                          #
# #-------------------------------------------------------#

df = pd.read_csv("modmatrix.csv")
V =list()
m_ij = {}

counter = 1
for index, row in df.iterrows():
    V.append(int(row[0]))
    counter2 = 1
    for element in row[1:]:
        m_ij[counter,counter2] = element
        counter2 +=1
    counter +=1

E = []
df = pd.read_csv("adjacency matrix.csv")

counter = 1
for index, row in df.iterrows():
    counter2 = 1
    for element in row[1:]:
        if element >0:
            E.append((counter,counter2))
        counter2 +=1
    counter +=1
# #-------------------------------------------------------#
# #                 defining variable                     #
# #-------------------------------------------------------#

X_ij = {}
graph_coloring = Model()
for i in V:
    for j in V:
        if i!=j:
            X_ij[i,j] = graph_coloring.addVar(vtype=GRB.BINARY, lb=0, ub=1, name="X_ij[%s, %s]" % (i,j))

# #-------------------------------------------------------#
# #                 defining constraints                     #
# #-------------------------------------------------------#

for i in V:
    for j in V:
        for l in V:
            if i!=j and i!=l and l!=j:
                graph_coloring.addConstr(X_ij[i,l] <= X_ij[i,j] +X_ij[j,l], name='const1')

m = len(E)/2
cost = (1/2*m)*quicksum(m_ij[i,j]*(1-X_ij[i,j]) for i in V for j in V if i!=j)

graph_coloring.setObjective(cost, GRB.MAXIMIZE)

graph_coloring.update()
graph_coloring.optimize()


clusters = []
assigned_nodes = []
not_assigned_nodes = list(V)

for i in V:
    dummy = []
    for j in not_assigned_nodes:
        if i != j:
            if X_ij[i,j].x >0.05:
                dummy.append(j)
                not_assigned_nodes.remove(j)

    if len(dummy) >0:
        dummy.append(i)
        if i in not_assigned_nodes:
            not_assigned_nodes.remove(i)

    if len(dummy)>0:
        clusters.append(dummy)

print("num clusters:", len(clusters))


val_map = {}
for c in range(len(clusters)):
    for i in clusters[c]:
        val_map[i] = c

G = nx.Graph()
G.add_nodes_from([i for i in V])
G.add_edges_from([(i, j, {'weight': m_ij[i, j]}) for (i,j) in E])
values = [val_map.get(node) for node in G.nodes()]
nx.draw(G, cmap=plt.get_cmap('viridis'), node_color=values, with_labels=True, node_size=40,width= 0.1, font_color='black', font_size = '6')
plt.show()