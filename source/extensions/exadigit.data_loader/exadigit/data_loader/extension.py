# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import random

import omni.ext
import omni.usd

from .data_propagator import DataPropagator
from .logging_config import logger
from .marconi100 import Marconi100DataLoader
from .name_mapper import NameMapper
from .simulation import Simulation
from .simulation_server_client import SimulationServerClient
from .window import DataLoaderWindow


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
        self.system_loader = None

        print("[exadigit.data_loader] Fetching initial simulation list on startup...")
        self.get_simulation_list()

        # Create UI Window
        self._window = DataLoaderWindow("ExaDigiT", self, width=400, height=400)

    def generate_lookup(self):
        """Refresh the scene and rebuild xname mapping."""
        print("[exadigit.data_loader] Refreshing scene...")
        self.name_mapper.generate_lookup()

    def propagate_data(self):
        """Fetches CDU and CEP data and propagates only if valid."""
        logger.info("Fetching CDU and CEP data...")

        if self.selected_sim:
            cdu_response = self.sim_client.get_simulation_cooling_cdu(self.selected_sim.id)[0]
            cep_response = self.sim_client.get_simulation_cooling_cep(self.selected_sim.id)[0]

            # Validate CDU data
            # if not cdu_response or "data" not in cdu_response or not cdu_response["data"]:
            #     logger.warning("CDU data is missing or empty. Cannot propagate.")
            #     return  # Stop propagation

            # Validate CEP data
            # if not cep_response or "data" not in cep_response or not cep_response["data"]:
            #     logger.warning("CEP data is missing or empty. Cannot propagate.")
                # return  # Stop propagation

            # Future Work: Parse responses with dataloader based on selected_sim.system, return correctly mapped data
            # Map the retrieved CDU and CEP data to xnames
            mapped_data = self.map_cooling_data(cdu_response, cep_response)

            # Just use test data for now with generate_test_data
            # logger.info("Generating test data for propagation...")
            # test_data = self.generate_test_data()

            # Send the mapped data to the data propagator
            logger.info("Propagating mapped test data...")
            self.data_propagator.propagate_data(mapped_data)

            logger.info("Data successfully propagated.")
        else:
            logger.error("No simulation selected! Please select one from the Simulation List panel.")

    ### WRAPPERS FOR SIMULATION SERVER CALLS ###
    def run_simulation(self, simulation_params):
        """Runs a user-defined simulation by calling the Simulation Server API."""
        print(f"[DEBUG] Running simulation with parameters: {simulation_params}")  # Debugging line

        response = self.sim_client.post_simulation_run(simulation_params)

        if response:
            print(f"[DEBUG] Simulation Successfully Created: {response}")

            # Check if cooling exists in response
            if "config" in response and "cooling" in response["config"]:
                print(f"[DEBUG] Cooling Enabled in Response: {response['config']['cooling']['enabled']}")
            else:
                print("[DEBUG] Cooling settings not found in response.")

        else:
            print("[exadigit.data_loader] Failed to run simulation")

    def get_simulation_list(self):
        """Fetches a list of available simulations and stores them as objects."""
        logger.info("[exadigit.data_loader] Running get simulation list API call...")

        response, status_code = self.sim_client.get_simulation_list(fields=["default"], limit=10)

        if status_code == 200 and response and "results" in response:
            self.sim_list = []  # Clear existing list before populating

            for item in response["results"]:
                config = item.get("config", {})
                cooling_enabled = config.get("cooling", {}).get("enabled", False)

                sim = Simulation(
                    sim_id=item.get("id"),
                    system=item.get("system"),
                    start=item.get("start"),
                    cooling_enabled=cooling_enabled  # Store correctly extracted value
                )
                self.sim_list.append(sim)

            logger.info(f"✅ Stored {len(self.sim_list)} simulations.")

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


    # Helper methods for data generation/propagation
    def map_cooling_data(self, cdu_response, cep_response):
        # Send responses to the appropriate dataloader based on the system of the selected sim
        if self.selected_sim.system == "marconi100":
            self.system_loader = Marconi100DataLoader(self.name_mapper)

        self.system_loader.parse_cdu_response(cdu_response)
        # self.system_loader.parse_cep_response()


    def generate_test_data(self):
        """Generates structured randomized test data."""
        test_data = {}

        for cab in range(1, 3):  # Example: Two cabinets (x1, x2)
            test_data[f"x{cab}"] = {
                "power": round(random.uniform(1, 5), 2),
                "temperature": round(random.uniform(0, 100), 2),
                "status": random.choice(["active", "inactive"])
            }

            for node in range(1, 22):  # 21 nodes per cabinet
                node_key = f"x{cab}n{node}"
                test_data[node_key] = {
                    "power": round(random.uniform(-5, 5), 2),
                    "temperature": round(random.uniform(0, 100), 2),
                    "status": random.choice(["active", "inactive"])
                }
                test_data[f"{node_key}p1"] = {
                    "power": round(random.uniform(-5, 5), 2),
                    "temperature": round(random.uniform(0, 100), 2),
                    "status": random.choice(["active", "inactive"])
                }

                for acc in range(1, 5):  # 4 accelerators per node
                    test_data[f"{node_key}a{acc}"] = {
                        "power": round(random.uniform(-5, 5), 2),
                        "temperature": round(random.uniform(0, 100), 2),
                        "status": random.choice(["active", "inactive"])
                    }

                for drive in range(1, 9):  # 8 drives per node
                    test_data[f"{node_key}d{drive}"] = {
                        "power": round(random.uniform(-5, 5), 2),
                        "temperature": round(random.uniform(0, 100), 2),
                        "status": random.choice(["active", "inactive"])
                    }

        return test_data

    def on_shutdown(self):
        print("[exadigit.data_loader] Extension shutdown")
        if self._window:
            self._window.destroy()
            self._window = None
