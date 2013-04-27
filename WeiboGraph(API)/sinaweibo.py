#! /bin/env python
# -*- coding: utf-8 -*-

'''
A python script to visualize your social network of sina weibo.
'''

import urllib
import urllib2
import cookielib
import re
import cPickle as p
import networkx as nx
import matplotlib.pyplot as plt

import weiboconfig as config
import client

__author__ = """dmy (doumengyu@gmail.com)"""

# Control parameters,EDIT here!
## UID means the user you want to analysis
UID ='1670662622'   
## Control Graphs, Edit for better graphs as you need
LABEL_FLAG = True  # Whether shows labels.NOTE: configure your matplotlibrc for Chinese characters.
REMOVE_ISOLATED = False  # Whether remove isolated nodes(less than iso_level connects)
DIFFERENT_SIZE = True  # Nodes for different size, bigger means more shared friends
ISO_LEVEL = 10
NODE_SIZE = 40  # Default node size


def getfriends(uid):
	"""Get the uid's friends and return the dict with uid as key,name as value."""
	print "Get %s 's friend list" % str(uid)
	dict1 = {}
	Client = client.Client.instance()
	if Client._init ==0:
		Client.init()
	users = Client.get_friend_bilateral(uid).users
	for user in users:
		no = user['id']
		uname = user['screen_name']
		dict1[no] = uname
	return dict1

def getdict(uid):
    """cache dict of uid in the disk."""
    try:
        with open(str(uid) + '.txt', 'r') as f:
            dict_uid = p.load(f)
    except:
        with open(str(uid) + '.txt', 'w') as f:
            p.dump(getfriends(uid), f)
        dict_uid = getdict(uid)
    return dict_uid

def getrelations(uid1, uid2):
	"""receive two user id, If they are friends, return 1, otherwise 0."""
	Client = client.Client.instance()
	if Client._init ==0:
		Client.init()
	result = Client.get_friendship(uid1,uid2)
	target = result.target
	source = result.source
	#if target.following and target.followed_by:
	if target.following and source.following:	
		return 1
	else:
		return 0


def getgraph(uid):
	"""Get the Graph Object and return it.
	You must specify a Chinese font such as `SimHei` in ~/.matplotlib/matplotlibrc"""
	dict_root = getdict(uid)  # Get root tree

	G = nx.Graph()  # Create a Graph object
	for uid1, uname1 in dict_root.items():
		# Encode Chinese characters for matplotlib **IMPORTANT**
		# if you want to draw Chinese labels,
		#uname1 = unicode(uname1, 'utf8')
		G.add_node(uname1)
		for uid2, uname2 in dict_root.items():
			#uname2 = unicode(uname2, 'utf8')
			# Not necessary for networkx
			if uid2 == uid1:
				continue
			if getrelations(uid1, uid2):
				G.add_edge(uname1, uname2)
	return G


def draw_graph(uid, filename='graph.txt', label_flag=True, remove_isolated=True, different_size=True, iso_level=10, node_size=40):
    """Reading data from file and draw the graph.If not exists, create the file and re-scratch data from net"""
    print "Generating graph..."
    try:
        with open(filename, 'r') as f:
            G = p.load(f)
    except:
        G = getgraph(uid)
        with open(filename, 'w') as f:
            p.dump(G, f)
    #nx.draw(G)
    # Judge whether remove the isolated point from graph
    if remove_isolated is True:
        H = nx.empty_graph()
        for SG in nx.connected_component_subgraphs(G):
            if SG.number_of_nodes() > iso_level:
                H = nx.union(SG, H)
        G = H
    # Ajust graph for better presentation
    if different_size is True:
        L = nx.degree(G)
        G.dot_size = {}
        for k, v in L.items():
            G.dot_size[k] = v
        node_size = [G.dot_size[v] * 10 for v in G]
    pos = nx.spring_layout(G, iterations=50)
    nx.draw_networkx_edges(G, pos, alpha=0.2)
    nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color='r', alpha=0.3)
    # Judge whether shows label
    if label_flag is True:
        nx.draw_networkx_labels(G, pos, alpha=0.5)
    #nx.draw_graphviz(G)
    plt.show()

    return G

if __name__ == "__main__":
    G = draw_graph(UID, filename='graph.txt', label_flag=LABEL_FLAG, remove_isolated=REMOVE_ISOLATED, different_size=DIFFERENT_SIZE, iso_level=ISO_LEVEL, node_size=NODE_SIZE)
