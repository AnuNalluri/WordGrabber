import json
import os
from os import listdir
from os.path import isfile, join

data_dir = os.environ["DATA_DIR"]

data_files = [f for f in listdir(data_dir) if isfile(join(data_dir, f)) and f is not None]
print(data_files)
for host in data_files:
	final_dict = {}
	with open(data_dir + host, "r") as content_file:
		content = content_file.read()
	dicts = content.split("\n~~~~~~\n")[:-1]
	
	count = 0
	for dictionary in dicts:
		outlinks = json.loads(dictionary)["outlinks"]
		for outlink in outlinks:
			if outlink in final_dict.keys():
				final_dict[outlink] += 1
			else:
				final_dict[outlink] = 1
		count += 1

	if None in final_dict:
		final_dict.pop(None)
	with open(data_dir + "edges", "a+") as graph_host_file:
		graph_host_file.write("hostname,outlink,count")
		for key in final_dict:
			print(key)
			graph_host_file.write(host + "," + key + "," +  str(final_dict[key]) + "\n")

