from neo4j import AsyncGraphDatabase
import os
from functools import reduce

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = AsyncGraphDatabase.driver(URI, auth=(USER, PASSWORD))
