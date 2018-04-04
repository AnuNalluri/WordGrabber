import networkx as nx
import os
import tldextract
#Assumes edges file and node metadata file have been created properly already

data_dir = os.environ["DATA_DIR"]
white_list = {"www.infowars.com", "www.naturalnews.com", "www.rt.com", "http://70news.wordpress.com/", "http://www.americannews.com/", "http://www.beforeitsnews.com/", "http://www.celebtricity.com/", "http://www.conservative101.com/", "http://www.dailybuzzlive.com/", "http://www.dcgazette.com/", "http://www.disclose.tv/", "http://www.firebrandleft.com/",  "http://www.globalresearch.ca/", "http://www.gossipmillsa.com/", "gummypost.com/", "http://www.liberalsociety.com/", "http://www.libertywriters.com/", "http://en.mediamass.net/", "nationalreport.net/", "http://www.neonnettle.com/", "http://www.newsbreakshere.com/", "http://www.thenewyorkevening.com/", "http://www.now8news.com/", "drudgereport.com/", "http://www.stuppid.com/"," http://worldnewsdailyreport.com/","http://yournewswire.com/"}

white_list_domains = {tldextract.extract(url).domain for url in white_list}
G = nx.DiGraph()

with open(data_dir + "edges", "r") as edge_file:
    next(edge_file)
    for edge in edge_file:
        edge_data = edge.split(",")
        G.add_edge(edge_data[0], edge_data[1], weight = int(float(edge_data[2])))
undesired_leaves =  [x for x in G.nodes() if G.out_degree(x)==0 and x not in white_list_domains]
while (len(undesired_leaves) > 0):
    for leaf in undesired_leaves:
        G.remove_node(leaf)
    undesired_leaves =  [x for x in G.nodes() if G.out_degree(x)==0 and x not in white_list_domains]
with open(data_dir + "edges_new", "a+") as new_edge_file:
    new_edge_file.write("hostname,outlink,count\n")
    for edge in G.edges(data="weight"):
        new_edge_file.write(edge[0] + "," + edge[1] + "," +  str(edge[2]) + "\n") 

