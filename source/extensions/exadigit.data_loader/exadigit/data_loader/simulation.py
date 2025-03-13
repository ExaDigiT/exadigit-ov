class Simulation:
    """Class representing a simulation object."""

    def __init__(self, sim_id, system, start, cooling_enabled=False):
        self.id = sim_id
        self.system = system
        self.start = start
        self.cooling_enabled = cooling_enabled

    def __repr__(self):
        return f"Simulation(id={self.id}, system={self.system}, start={self.start}, cooling_enabled={self.cooling_enabled})"
