from graph.db import Neo4JDB
import os
import networkx as nx
import csv
import json

FAKE_NEWS = "red"
SOCIAL_MEDIA = "blue"

options = {
	'colored_nodes' : {
		'rt' : FAKE_NEWS,
		'70news' : FAKE_NEWS,
		'beforeitsnews' : FAKE_NEWS,
		'jimstonefreelance' : FAKE_NEWS,
		'twitter' : SOCIAL_MEDIA,
		'facebook' : SOCIAL_MEDIA,
		'google' : SOCIAL_MEDIA,
		'soundcloud' : SOCIAL_MEDIA,
		'youtube' : SOCIAL_MEDIA,
		't' : SOCIAL_MEDIA
	},
	'default_node_color' : 'green',
}

db = Neo4JDB(os.environ["NEO_DB_URL"], os.environ["NEO_DB_USER"], os.environ["NEO_DB_PASS"])
nodes = db.get_all_nodes()
relationships = db.get_all_relationships()

def in_colored_nodes(host_name):
	if host_name in options['colored_nodes']:
		return options['colored_nodes'][host_name]
	return options['default_node_color']

def to_json():
	json_dictionary = dict()
	node_list = []
	link_list = []
	node_to_index = dict()
	# nodes
	counter = 0
	for record in nodes:
		node = record["n"]
		dict_n = dict()
		host_name = node.get("host_name")
		
		dict_n["name"] = host_name
		dict_n["id"] = counter
		dict_n["color"] = in_colored_nodes(host_name)
		dict_n["size"] = 0

		node_list.append(dict_n)

		node_to_index[host_name] = counter
		counter += 1

	# links
	for record in relationships:
		relationship = record["r"]
		source = record["n"]
		target = record["m"]
		dict_r = dict()

		if source.get("host_name") == target.get("host_name"):
			continue
		
		weight = relationship.get("weight")
		source_host = node_to_index[source.get("host_name")]
		target_host = node_to_index[target.get("host_name")]
		
		dict_r["weight"] = weight
		dict_r["source"] = source_host
		dict_r["target"] = target_host

		# update number of inlinks to the node
		node_list[target_host]["size"] += int(weight)

		link_list.append(dict_r)

	json_dictionary["nodes"] = node_list 
	json_dictionary["links"] = link_list

	with open("visualize/data.json", "w") as json_file:
		json.dump(json_dictionary, json_file)

to_json()

