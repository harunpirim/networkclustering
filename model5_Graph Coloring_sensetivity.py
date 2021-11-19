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
E, E_plus, E_minus = [], [], []
m_ij ={}

df = pd.read_csv("signed.csv")
for index, row in df.iterrows():
    if (row[1], row[2]) not in E:
        E.append((row[1], row[2]))
        m_ij[row[1], row[2]] = row[3]

        if row[3] >0:
            if (row[1], row[2]) not in E_plus:
                E_plus.append((row[1], row[2]))
        else:
            if (row[1], row[2]) not in E_minus:
                E_minus.append((row[1], row[2]))

    if row[1] not in V:
        V.append(row[1])
    if row[2] not in V:
        V.append(row[2])

obj_val = []
K_list = range(3,10)
for K in K_list:
    C= range(K)

    # #-------------------------------------------------------#
    # #                 defining variable                     #
    # #-------------------------------------------------------#

    X_ic, f_ij = {}, {}
    graph_coloring = Model()
    for c in C:
        for i in V:
            X_ic[i,c] = graph_coloring.addVar(vtype=GRB.BINARY, lb=0, ub=1, name="X_ic[%s, %s]" % (i,c))

    for (i,j) in E:
        f_ij[i,j] = graph_coloring.addVar(vtype=GRB.BINARY, lb=0, ub=1, name="f_ij[%s, %s]" % (i,j))
    # #-------------------------------------------------------#
    # #                 defining constraints                     #
    # #-------------------------------------------------------#
    for i in V:
        graph_coloring.addConstr(quicksum(X_ic[i,c] for c in C) == 1, name= 'const1')

    for (i,j) in E_plus:
        for c in C:
            graph_coloring.addConstr(f_ij[i,j] >= X_ic[i,c]-X_ic[j,c], name= 'cons2')

    for (i,j) in E_minus:
        for c in C:
            graph_coloring.addConstr(f_ij[i,j] >= X_ic[i,c]+X_ic[j,c]-1, name= 'cons3')

    cost = quicksum(f_ij[i,j] for (i,j) in E)

    graph_coloring.setObjective(cost, GRB.MINIMIZE)

    graph_coloring.update()
    graph_coloring.optimize()
    obj_val.append(graph_coloring.objval)

    # val_map = {}
    # for c in C:
    #     for i in V:
    #         if X_ic[i,c].x >0:
    #             print("X_ic[%s, %s]:" % (i,c), X_ic[i,c].x, "colour type:", c)
    #             val_map[i] = c
    #
    #
    # G = nx.Graph()
    # G.add_nodes_from([i for i in V])
    # G.add_edges_from([(i, j, {'weight': m_ij[i, j]}) for (i,j) in E])
    # values = [val_map.get(node) for node in G.nodes()]
    # nx.draw(G, cmap=plt.get_cmap('viridis'), node_color=values, with_labels=True, node_size=40,width= 0.1, font_color='black', font_size = '6')
    # plt.show()

print("obj_val:", obj_val)
plt.rc('font', family='serif')
plt.plot(list(K_list), obj_val, 'bs')
plt.xlabel('Number of Cluster')
plt.ylabel('Objective value')
plt.show()