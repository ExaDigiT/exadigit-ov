# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import omni.ext
import omni.ui as ui
from .window import DataLoaderWindow
from .name_mapper import NameMapper
from .data_propagator import DataPropagator
from .simulation_server_client import SimulationServerClient
from .simulation import Simulation
import omni.usd
import os
import json

class DataLoaderExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        print("[exadigit.data_loader] Extension startup")

        # Initialize core modules
        self.name_mapper = NameMapper()
        self.data_propagator = DataPropagator(self.name_mapper)
        self.sim_client = SimulationServerClient()

        # Initialize variables
        self.sim_list = None
        self.selected_sim = None

        print("[exadigit.data_loader] Fetching initial simulation list on startup...")
        self.get_simulation_list()

        # Create UI Window
        self._window = DataLoaderWindow("ExaDigiT", self, width=400, height=400)

    def refresh_scene(self):
        """Refresh the scene and rebuild xname mapping."""
        print("[exadigit.data_loader] Refreshing scene...")
        self.name_mapper.refresh_scene()

    def propagate_data(self):
        """Propagate test data."""
        print("[exadigit.data_loader] Propagating data...")
        test_data = self.generate_test_data()  # Generates test data
        self.data_propagator.propagate_data(test_data)

    ### WRAPPERS FOR SIMULATION SERVER CALLS ###
    def run_simulation(self, simulation_params):
        """
        Runs a user-defined simulation by calling the Simulation Server API.
        """
        print("[exadigit.data_loader] Running simulation with user-defined parameters...")
        response = self.sim_client.post_simulation_run(simulation_params)

        if not response:
            print("[exadigit.data_loader] Failed to run simulation")


    def get_simulation_list(self):
        """Fetches a list of available simulations and stores them as objects."""
        print("[exadigit.data_loader] Running get simulation list API call...")

        # Fetch response from the API
        response = self.sim_client.get_simulation_list(limit=10)

        if response and "results" in response:
            self.sim_list = []  # Clear existing list before populating
            for item in response["results"]:
                sim = Simulation(
                    sim_id=item.get("id"),
                    system=item.get("system"),
                    start=item.get("start")
                )
                self.sim_list.append(sim)

            print(f"Stored {len(self.sim_list)} simulations: {self.sim_list}")
        else:
            print("[exadigit.data_loader] Failed to fetch simulation list or empty response.")

    def get_simulation_details(self, simulation_id):
        """Fetch details of a specific simulation."""
        print(f"[exadigit.data_loader] Fetching details for simulation ID: {simulation_id}")
        response = self.sim_client.get_simulation(simulation_id)
        print(f"Simulation Details: {response}")

    def get_simulation_cooling_cdu(self, simulation_id):
        """Fetch cooling CDU data for a simulation."""
        print(f"[exadigit.data_loader] Fetching cooling CDU data for simulation ID: {simulation_id}")
        response = self.sim_client.get_simulation_cooling_cdu(simulation_id)
        print(f"Cooling CDU Data: {response}")

    def get_simulation_scheduler_jobs(self, simulation_id):
        """Fetch scheduler jobs for a simulation."""
        print(f"[exadigit.data_loader] Fetching scheduler jobs for simulation ID: {simulation_id}")
        response = self.sim_client.get_simulation_scheduler_jobs(simulation_id)
        print(f"Scheduler Jobs: {response}")

    def get_system_info(self, system_name):
        """Fetch system info from the API."""
        print(f"[exadigit.data_loader] Fetching system info for: {system_name}")
        response = self.sim_client.get_system_info(system_name)
        print(f"System Info: {response}")

    def generate_test_data(self):
        """Generates structured test data."""
        test_data = {}
        for cab in range(1, 3):  # Example: Two cabinets (x1, x2)
            test_data[f"x{cab}"] = {"power": -1.0, "temperature": 75.0, "status": "active"}
            for node in range(1, 5):  # 4 nodes per cabinet
                node_key = f"x{cab}n{node}"
                test_data[node_key] = {"power": -1.0, "temperature": 75.0, "status": "active"}
                test_data[f"{node_key}p1"] = {"power": -1.0, "temperature": 75.0, "status": "active"}

                for acc in range(1, 5):  # 4 accelerators per node
                    test_data[f"{node_key}a{acc}"] = {"power": -1.0, "temperature": 75.0, "status": "active"}

                for drive in range(1, 9):  # 8 drives per node
                    test_data[f"{node_key}d{drive}"] = {"power": -1.0, "temperature": 75.0, "status": "active"}
        return test_data

    def create_test_simulation(self):
        """Creates a test simulation with required parameters."""
        print("[exadigit.data_loader] Running test simulation creation...")

        simulation_params = {
            "start": "2025-03-10T12:00:00Z",  # ISO 8601 format
            "end": "2025-03-10T14:00:00Z",
            "system": "fugaku",  # One of the allowed values

            "scheduler": {
                "enabled": True,
                "jobs_mode": "random",  # Change to "custom" if providing a job list
                "seed": 12345,  # Optional but good for consistency
                "num_jobs": 10  # Required when jobs_mode is "random"
            },

            "cooling": {
                "enabled": False  # Default is false, but explicitly setting it
            }
        }

        response = self.sim_client.post_simulation_run(simulation_params)

        if response:
            print(f"Test Simulation Created: {response}")
        else:
            print("[exadigit.data_loader] Failed to create test simulation")

    def on_shutdown(self):
        print("[exadigit.data_loader] Extension shutdown")
        if self._window:
            self._window.destroy()
            self._window = None
