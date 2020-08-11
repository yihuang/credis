#!/usr/bin/env python
from credis import Connection
import unittest


class TestSimple(unittest.TestCase):
    def test_simple(self):
        conn = Connection()

        assert conn.execute("SET", 1, 1) == b"OK"
        assert conn.execute("GET", 1) == b"1"

        # pipeline
        assert conn.execute_pipeline(("SET", 1, 2), ("GET", 1),) == (b"OK", b"2")

        assert conn.execute_pipeline(
            ("SET", 1, 1), ("INCR", 1), ("INCRBY", 1, 1), ("GET", 1),
        ) == (b"OK", 2, 3, b"3")

        # Connection with explicit db selection.
        conn_with_explicit_db = Connection(db=7)

        assert conn_with_explicit_db.execute("SET", 1, 1) == b"OK"
        assert conn_with_explicit_db.execute("GET", 1) == b"1"

        # pipeline
        assert conn_with_explicit_db.execute_pipeline(("SET", 1, 2), ("GET", 1),) == (
            b"OK",
            b"2",
        )

        assert conn_with_explicit_db.execute_pipeline(
            ("SET", 1, 1), ("INCR", 1), ("INCRBY", 1, 1), ("GET", 1),
        ) == (b"OK", 2, 3, b"3")
