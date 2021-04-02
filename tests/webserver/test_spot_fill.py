import json
import os
from unittest import TestCase
from unittest.mock import MagicMock, patch

import redis

with patch.dict(
    os.environ, {"TEST_SECTORS": json.dumps({"foo": [[0, 3]], "bar": [[4, 7]]})}
):
    from webserver import app
    from worker import Worker

headers = {"Accept": "application/json", "Content-type": "application/json"}
redis = redis.Redis()
worker = Worker()
worker.desk.light_up = MagicMock()


class TestSpotFill(TestCase):
    """Test `spot-fill`."""

    def setUp(self):
        """Do some initialisation."""
        redis.flushall()

    def test_easy_spot(self):
        """Test the simple case."""
        client = app.test_client()
        data = json.dumps({"colour": [123, 123, 0], "mode": "spot-fill"})
        response = client.post("/desk/light", headers=headers, data=data)

        worker.poll()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.data), {"colour": [123, 123, 0], "status": "OK"}
        )

    def test_with_parameters(self):
        """Test with params."""
        client = app.test_client()
        data = json.dumps({"colour": [10, 20, 30], "mode": "spot-fill", "delay": 0.1})
        response = client.post("/desk/light", headers=headers, data=data)

        worker.poll()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.data), {"colour": [10, 20, 30], "status": "OK"}
        )
