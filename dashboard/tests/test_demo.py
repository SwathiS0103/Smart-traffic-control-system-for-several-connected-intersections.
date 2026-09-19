import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from demo_mode import DemoManager

def test_demo_manager():
    dm = DemoManager()
    
    # 1. Normal traffic
    data = dm.get_state_for_scenario("Normal Traffic", 0)
    assert "metrics" in data
    assert data["metrics"]["waiting_time"] == 15.0
    
    # 2. Congestion
    data = dm.get_state_for_scenario("Congestion", 10)
    assert data["events"][0]["type"] == "CONGESTION"
    
    # 3. Accident
    data = dm.get_state_for_scenario("Accident", 20)
    assert any(e["type"] == "ACCIDENT" for e in data["events"])
    
    # 4. Emergency
    data = dm.get_state_for_scenario("Emergency", 30)
    assert len(data["emergencies"]) == 1
    assert data["emergencies"][0]["vehicle_id"] == "AMB001"
