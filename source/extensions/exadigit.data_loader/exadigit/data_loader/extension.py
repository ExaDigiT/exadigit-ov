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

        # Create UI Window
        self._window = DataLoaderWindow("ExaDigit Data Loader", self, width=400, height=400)

    def refresh_scene(self):
        """Refresh the scene and rebuild xname mapping."""
        print("[exadigit.data_loader] Refreshing scene...")
        self.name_mapper.refresh_scene()

    def propagate_data(self):
        """Propagate test data."""
        print("[exadigit.data_loader] Propagating data...")
        test_data = self.generate_test_data()  # Generates test data
        self.data_propagator.propagate_data(test_data)

    def run_simulation_api_call(self):
        """Runs a simulation using the Simulation Server API."""
        print("[exadigit.data_loader] Running simulation API call...")
        response = self.sim_client.run_simulation()
        print(f"Simulation Response: {response}")

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

    def on_shutdown(self):
        print("[exadigit.data_loader] Extension shutdown")
        if self._window:
            self._window.destroy()
            self._window = None
