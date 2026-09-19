from .demo_mode import DemoManager

class AdapterManager:
    def __init__(self):
        self.demo = DemoManager()
        self.current_step = 0
        self.scenario = "Normal Traffic"
        
    def get_state(self):
        return self.demo.get_state_for_scenario(self.scenario, self.current_step)
        
    def set_scenario(self, scenario: str):
        self.scenario = scenario
        self.current_step = 0
        
    def step(self):
        self.current_step += 1
        
    def reset(self):
        self.current_step = 0
