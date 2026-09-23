import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()


class Neo4jClient:

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

    def verify_connection(self):
        try:
            self._get_driver().verify_connectivity()
            print("[OK] Neo4j connection successful")
            return True
        except Exception as exc:  # pragma: no cover - defensive runtime handling
            print(f"[WARN] Neo4j unavailable: {exc}")
            return False

    def execute(self, query, parameters=None):
        """
        Execute a write/query operation.

        Returns ResultSummary.
        """
        try:
            with self._get_driver().session() as session:
                result = session.run(query, parameters or {})
                return result.consume()
        except Exception as exc:
            print(f"[WARN] Neo4j query failed: {exc}")
            return None

    def execute_read(self, query, parameters=None):
        """
        Execute a read query and return all records.
        """
        try:
            with self._get_driver().session() as session:
                result = session.run(query, parameters or {})
                return list(result)
        except Exception:
            return []

    def execute_write(self, query, parameters=None):
        """
        Execute a write query.
        """
        try:
            with self._get_driver().session() as session:
                result = session.run(query, parameters or {})
                return result.consume()
        except Exception:
            return None

    def close(self):
        if self.driver is not None:
            self.driver.close()
            self.driver = None
