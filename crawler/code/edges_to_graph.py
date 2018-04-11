import networkx as nx
import os
import tldextract
import json
#Assumes edges file has been created already.
FAKE_NEWS = set(open(os.environ["CATEGORIES"] + "fake_news_list", 'r').read().split())
REAL_NEWS = set(open(os.environ["CATEGORIES"] + "real_list", 'r').read().split())
SOC_MED = set(open(os.environ["CATEGORIES"] + "social_media_list", 'r').read().split())
id_map = {}
G = nx.DiGraph()
ban = set()
links = []
nodes = []
DATA_DIR = os.environ["DATA_DIR"]
def find_category(node):
	category = "OTHER"
	if node in FAKE_NEWS:
		category = "FAKE"
	if node in REAL_NEWS:
		category = "REAL"
	if node in SOC_MED:
		category = "SOCIAL"
	return category

with open(DATA_DIR + "edges", "r") as edge_file:
	next(edge_file)
	for edge in edge_file:
		edge_data = edge.split(",")
		G.add_edge(edge_data[0], edge_data[1], weight = int(float(edge_data[2].rstrip())))
id_ = 0
for node in G.nodes():
	outlinks_num = G.out_degree(node, weight='weight')
	inlinks_num = G.in_degree(node, weight='weight')
	outdegree = G.out_degree(node)
	indegree = G.in_degree(node)
	node_dict = {
		"outlinks_num": outlinks_num,
		"inlinks_num": inlinks_num, 
		"outdegree": outdegree,
		"indegree": indegree,
		"id": id_,
		"category": find_category(node),
		"name": node
	}
	if os.environ["WHITE_LIST"] == "1" and not find_category(node) == "FAKE" and outdegree == 0:
		ban.add(node)
		continue
	else:
		nodes.append(node_dict)
		id_map[node] = id_
		id_ += 1
for edge in G.edges(data=True):
	if edge[0] in ban or edge[1] in ban:
		continue
	edge_dict = {
		"source": id_map[edge[0]],
		"target": id_map[edge[1]],
		"source_type": find_category(edge[0]),
		"dest_type": find_category(edge[1]),
		"weight": edge[2]["weight"]
	}
	links.append(edge_dict)
final_dict = {"nodes": nodes, "links": links}
with open(DATA_DIR + "graph_file", 'w+') as outfile:
	json.dump(final_dict, outfile)



