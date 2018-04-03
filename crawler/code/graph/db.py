from neo4j.v1 import GraphDatabase
import os
"""
LOAD CSV WITH HEADERS FROM 'file:///test.csv'AS csvLine
MERGE (h:host { host_name: csvLine.hostname})
MERGE (out:host {host_name: csvLine.outlink})
"""

"""
LOAD CSV WITH HEADERS FROM 'file:///test.csv'AS csvLine
MATCH (h:host {host_name : csvLine.hostname}), (out:host {host_name : csvLine.outlink})
CREATE (h)-[r:link {weight: csvLine.count}]->(out)
"""

class Neo4JDB(object):

	def __init__(self, uri, user, password):
		self._driver = GraphDatabase.driver(uri, auth=(user, password))

	def close(self):
		self._driver.close()

	def load_csv(self, file_name):
		load_nodes_query = "LOAD CSV WITH HEADERS FROM 'file:///{}'AS csvLine ".format(file_name)\
							+ "MERGE (h:host { host_name: csvLine.hostname}) "\
							+ "MERGE (out:host {host_name: csvLine.outlink})"

		load_relationships_query = "LOAD CSV WITH HEADERS FROM 'file:///{}'AS csvLine ".format(file_name)\
				+ "MATCH (h:host {host_name : csvLine.hostname}), (out:host {host_name : csvLine.outlink}) "\
				+ "CREATE (h)-[r:link {weight: csvLine.count}]->(out)"


		with self._driver.session() as session:
			print("Session activated...")
			result = session.run(load_nodes_query)
			print("Ran first query...")
			print("Result of first query " + str(result))
			result = session.run(load_relationships_query)
			print("Result of second query " + str(result))

		return True

	def clear_db(self):
		try:
			delete_query = "MATCH (n) DETACH DELETE n"
			with self._driver.session() as session:
				result = session.run(delete_query)
			return True
		except:
			return False

	def get_all_nodes(self):
		get_all_query = "MATCH (n) RETURN (n)"
		with self._driver.session() as session:
			return session.run(get_all_query)
			 

	def get_all_relationships(self):
		get_all_query = "START n=node(*) MATCH (n)-[r]->(m) RETURN n,r,m"
		with self._driver.session() as session:
			return session.run(get_all_query)



