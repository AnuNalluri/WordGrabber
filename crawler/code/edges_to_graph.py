import networkx as nx
import os
import tldextract
import json
#Assumes edges file has been created already.
DATA_DIR = os.environ["DATA_DIR"]
REAL_NEWS = set(open(os.environ["CATEGORIES"] + "real_list", 'r').read().split())
REAL_NEWS = {tldextract.extract(link).domain for link in REAL_NEWS} 	
SOC_MED = set(open(os.environ["CATEGORIES"] + "social_media_list", 'r').read().split())
SOC_MED = {tldextract.extract(link).domain for link in SOC_MED} 
FAKE_NEWS = set(open(os.environ["CATEGORIES"] + "fake_news_list", 'r').read().split())
FAKE_NEWS = {tldextract.extract(link).domain for link in FAKE_NEWS} 
id_map = {}
G = nx.DiGraph()
links = []
nodes = []
#Some graph options
trimming = False
include_only = [SOC_MED, FAKE_NEWS, REAL_NEWS]
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
if trimming:
    unwanted = [node for node in G.nodes if G.out_degree(node) == 0 and not any(node in group for group in include_only)]
    while (len(unwanted) > 0):
        print(unwanted)
        for node in unwanted:
            G.remove_node(node)
        unwanted = [node for node in G.nodes if G.out_degree(node) == 0 and not any(node in group for group in include_only)]
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
    nodes.append(node_dict)
    id_map[node] = id_
    id_ += 1
for (s,d,w) in G.edges(data='weight'):
    edge_dict = {
        "source": id_map[s],
        "target": id_map[d],
        "source_type": find_category(s),
        "dest_type": find_category(d),
        "weight": w
    }
    links.append(edge_dict)
final_dict = {"nodes": nodes, "links": links}
with open(DATA_DIR + "graph_file", 'w+') as outfile:
    json.dump(final_dict, outfile)
