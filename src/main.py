# -*- coding: utf-8 -*-
"""test1PST.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EKfnpDarejaVydlQTzMRz0LidCGdb2PQ
"""

#import pulp
import pandas as pd
import networkx as nx
from pulp import LpMaximize, LpMinimize, LpProblem, LpStatus, lpSum, LpVariable
import numpy as np
import random
#from scipy.stats import rankdata
import time
from itertools import islice

class DataSets:
    base_path = '../data/'
    CORA =     {'path': 'cora/cora.cites', 'sep': '\t', 'name': 'Cora'}  # ~ 5K edges 2K nodes
    FACEBOOK = {'path': 'facebook/facebook_combined.txt', 'sep': ' ', 'name': 'Facebook'} # ~88K edges 4K nodes
    ENRON_EMAILS = {'path': 'enron/email-Enron.txt', 'sep': '\t', 'name': 'Enron Emails'} # ~ 184K edges 33K nodes
    GRQC = {'path': 'grqc/ca-GrQc.txt', 'sep': '\t', 'name': 'General Relativity & Quantum Cosmology collab network'}
    HEPTH = {'path': 'HepTh/ca-HepTh.txt', 'sep': '\t', 'name': 'High Energy Physics - Theory collaboration network'}
    PA_ROAD = {'path': 'PA-roads/roadNet-PA.txt', 'sep': '\t', 'name': 'Pennsylvania Road Network'}
    EPINIONS = {'path': 'epinions/soc-Epinions1.txt', 'sep': '\t', 'name': 'Epinions.com Network'}# 508k edges 75k nodes
    # returns an networkx graph object representing the dataset
    # if lcc is true, it returns only largest connected component
    @classmethod    
    def get_undirected_networkx_graph(cls, dataset, lcc=True):
        path = cls.base_path + dataset['path']
        separator = dataset['sep']
        edgelist = pd.read_csv(path, sep=separator, names=['target', 'source'], comment='#')
        G = nx.from_pandas_edgelist(edgelist)
        if lcc == True:
            gs = [G.subgraph(c) for c in nx.connected_components(G)]
            G = max(gs, key=len)
        return G
    
    @classmethod   
    def get_directed_networkx_graph(cls, dataset, lcc=True):
        path = cls.base_path + dataset['path']
        separator = dataset['sep']
        edgelist = pd.read_csv(path, sep=separator, names=['target', 'source'], comment='#')
        G = nx.from_pandas_edgelist(edgelist,source='source', target='target', create_using=nx.DiGraph())
        if lcc == True:
            gs = [G.subgraph(c) for c in nx.connected_components(G)]
            G = max(gs, key=len)
        return G

    
    @classmethod
    def get_df_lcc(cls, dataset, lcc=True):
        path = cls.base_path + dataset['path']
        separator = dataset['sep']
        edgelist = pd.read_csv(path, sep=separator, names=['target', 'source'], comment='#')
        G = nx.from_pandas_edgelist(edgelist)
        if lcc == True:
            gs = [G.subgraph(c) for c in nx.connected_components(G)]
            G = max(gs, key=len)
        df = nx.to_pandas_edgelist(G)
        df.columns = [0,1]
        return df
    
    @classmethod
    def get_df(cls, dataset):
        path = cls.base_path + dataset['path']
        separator = dataset['sep']
        df = pd.read_csv(path, sep=separator, header=None, comment='#')
        return df




# get weight of single edge
def weight(G, edge):
    """ edge: 2-tuple """
    return G.get_edge_data(*edge)['weight']

def path_weight(G, path):
    """ path: list of nodes in path """
    w = sum([weight(G,(path[i],path[i+1]))for i,node in enumerate(path) if i<len(path)-1])
    return w

def k_shortest_paths(G, s, t, k_paths, weight='weight'):
    return list(islice(nx.shortest_simple_paths(G, s, t, weight=weight), k_paths))

def generate_random_st_pair():
    s, t = np.random.choice(V, 2)
    while(not nx.has_path(G, source=s, target=t) and not s==t):
        s, t = np.random.choice(V, 2)
    dist = nx.shortest_path_length(G, source=s, target=t, weight='weight')   
    return s, t, dist
    
def single_result_to_df(result):
    return pd.DataFrame(result).astype(int)



def get_a_pe(a_pe, i, j):
  if j in a_pe[i]:
    return 1
  else:
    return 0

weighted = False
early_stop = False
percP = 0.1
k = 1.2
num_pairs = 1

print('weighted: ', weighted)
print('early_stop: ', early_stop)
print('percP: ', percP)
print('k: ', k)
print('num_pairs: ', num_pairs)
print()


G = DataSets.get_directed_networkx_graph(dataset=DataSets.EPINIONS, lcc=False)
#G = DataSets.get_directed_networkx_graph(dataset=DataSets.FACEBOOK, lcc=False)
if weighted:
    for (u,v,w) in G.edges(data=True):
        w['weight'] = random.randint(1,10)
else:
    for (u,v,w) in G.edges(data=True):
        w['weight'] = 1
        
print('nodes: {} \nedges: {}'.format(G.number_of_nodes(), G.number_of_edges()))


E = list(G.edges()) 
V = list(G.nodes()) 
W = [e[2]['weight'] for e in list(G.edges(data=True))] # get edge weights



R = random.choices(range(len(E)), k=round(len(E) * percP))
Pe = [0] * len(E)
for e in R:
  Pe[e] = 1

print('number of private edges:', len(R))
print(len(Pe))
print(R)

Pst = [[] for i in range(num_pairs)]
for i in range(num_pairs):
  s= 48722
  t= 723
  # s, t = np.random.choice(V, 2)
  # while(not nx.has_path(G, source=s, target=t)):
  #   s, t = np.random.choice(V, 2)
# s = 2139 t= 1359 distance = 4
# s = 2304 t= 1961 distance = 2
# s = 3240 t= 383 distance = 7
# s = 3405 t= 2882 distance = 3
# s = 3297 t= 415 distance = 6
  dist = nx.shortest_path_length(G, source=s, target=t, weight='weight')

  print("s =",s,"t=",t)
  print("distance:", dist)

  k_paths = 20
  while True:
    paths = k_shortest_paths(G, s, t, k_paths)
    print('length of paths is',len(paths))
    if k_paths > len(paths) or path_weight(G, paths[-1]) > k*dist:
      break
    print('k_paths: ', k_paths, ', largest dist: ', path_weight(G, paths[-1]))
    print()
    k_paths = k_paths * 2
    if early_stop and k_paths > 100:
      print('Early Stop for computing all short paths of dist <= ', k*dist, '!!! May not find Optimal solution!')
      break
    print('set a new value of k_paths: ', k_paths)
  print()
  print('number of found paths: ', len(paths), ', largest dist: ', path_weight(G, paths[-1]))

  for path in paths:
    weights = path_weight(G, path)
    # print("length of path: {}    k*dist = {}".format(weight, k*dist))
    if weights <= k*dist:
      Pst[i].append(path)
  print("number of paths in Pst:", i, len(Pst[i]))
print('Pst:', Pst)

a_pe = [[] for i in range(num_pairs)]

for i in range(num_pairs):
  for y in range(len(Pst[i])):
    a_pe[i].append({})

  p=0
  for path in Pst[i]:
    for j,node in enumerate(path):
      if j<len(path)-1:
        a_pe[i][p][(path[j],path[j+1])] = 1
        a_pe[i][p][(path[j+1],path[j])] = 1
    p = p + 1
  print('list of a_pe is', i, a_pe[i])

start_time = time.time()
model = LpProblem(name="min", sense=LpMinimize)

tot_P = 0
for i in range(num_pairs):
  tot_P = tot_P + len(Pst[i])

Xe = LpVariable.dicts("Xe", range(0,len(E)), cat='integer', lowBound=0, upBound=1) 
Yp = LpVariable.dicts("Yp", range(0, tot_P), cat='integer', lowBound=0, upBound=1)

model += lpSum([Xe[i]*Pe[i] for i in range(0,len(E))])

# For each pair of nodes (s,t), one Yp in Pst should be included
cur_P = 0
for i in range(num_pairs):
  model += sum([Yp[cur_P + j] for j in range(0,len(Pst[i]))]) >= 1
  cur_P = cur_P + len(Pst[i])

j=0
for e in E:
  cur_P = 0
  for i in range(num_pairs):
    model += sum([Yp[cur_P +k] * get_a_pe(a_pe[i], k, e)  for k in range(0,len(Pst[i]))]) <= Xe[j]
    cur_P = cur_P + len(Pst[i])
  j = j + 1
print('model construction took: {:.1f} seconds'.format((time.time() - start_time)))
print()

# Solve problem
start_time = time.time()
model.solve()
Xe_soln = np.array([Xe[i].varValue for i in range(0, len(E))])
Yp_soln = np.array([Yp[i].varValue for i in range(0, tot_P)])
print (("Status:"), LpStatus[model.status])
print("solving lp problem took: {:.1f} seconds".format(time.time() - start_time))

print()
nonzero = np.nonzero(Xe_soln*Pe)[0]
print('number of private edges included:', len(nonzero))
if len(nonzero) > 0:
  for e in nonzero:
    print(E[e])
print()

nonzero = np.nonzero(Xe_soln)[0]
print('added edges:')
for e in nonzero:
  print(E[e])
print()
print('added paths:')
nonzero = np.nonzero(Yp_soln)[0]
j = 0
cur_P = 0
for e in nonzero:
  while cur_P + len(Pst[j]) <= e:
      cur_P = cur_P + len(Pst[j])
      j = j + 1
  print(Pst[j][e-cur_P])

