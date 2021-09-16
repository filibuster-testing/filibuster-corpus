import os, sys
import json
import time

parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_path)

from telemetry.app import app


file_path = "{}/logs.json".format(parent_path)

def test_telemetry_success():
    client = app.test_client()
    reply = client.post("/", json={"time":time.time()})
    assert reply.status_code == 200

    with open(file_path, "r") as f:
        stats = json.load(f)
        log = stats["logs"][-1]
        assert log['time'] < time.time()
