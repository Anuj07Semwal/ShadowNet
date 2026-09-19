import os
from dotenv import load_dotenv

load_dotenv()

from neo4j import GraphDatabase

class Neo4jService:

    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.username = os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = os.environ["NEO4J_PASSWORD"]
        self.driver = None

    def _get_driver(self):
        if self.driver is None:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
            )
        return self.driver

    def close(self):
        if self.driver is not None:
            self.driver.close()
            self.driver = None

    def execute(self, query, parameters=None):
        try:
            with self._get_driver().session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception:
            return []
