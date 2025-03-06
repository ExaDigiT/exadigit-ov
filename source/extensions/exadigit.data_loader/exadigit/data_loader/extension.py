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
from pxr import Usd, Sdf, UsdShade
import omni.usd
import os
import json


class DataLoader(omni.ext.IExt):
    def on_startup(self, _ext_id):
        print("[exadigit.data_loader] Extension startup")

        # Load xnames mapping
        current_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(current_dir, "xnames_map.json"), "r") as f:
            self.xnames_map = json.load(f)

        self.lookup_dict = {}  # Stores xname-to-prim mappings

        self._window = ui.Window("Data Loader", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                ui.Label("Click 'Refresh Scene' to rebuild xnames and lookup.")
                ui.Button("Refresh Scene", clicked_fn=self.refresh_scene)
                ui.Label("Click 'Propagate Data' to update attributes and materials.")
                ui.Button("Propagate Data", clicked_fn=self.propagate_data)

    def _assign_xnames_recursive(self, prim, stack=None, counters=None):
        if stack is None:
            stack = []
        if counters is None:
            counters = {}

        attributes_scope = prim.GetChild("attributes")
        if attributes_scope:
            type_attr = attributes_scope.GetAttribute("type")
            if type_attr and type_attr.HasAuthoredValue():
                prim_type = type_attr.Get()
                type_info = self.xnames_map.get(prim_type, {"code": "u", "container": False})
                type_code = type_info["code"]
                is_container = type_info.get("container", False)

                if is_container:
                    old_val = counters.get(type_code, 0)
                    counters[type_code] = old_val + 1
                    idx = counters[type_code]

                    stack.append((type_code, idx))
                    prefix = "".join(f"{code}{num}" for (code, num) in stack)

                    xname_attr = attributes_scope.GetAttribute("xname")
                    if not xname_attr:
                        xname_attr = attributes_scope.CreateAttribute("xname", Sdf.ValueTypeNames.String)
                    xname_attr.Set(prefix)
                    # Print statement to verify correct xname assignment
                    #print(f"[exadigit.data_loader] Assigned xname '{prefix}' to container {prim.GetPath()}")

                    self.lookup_dict[prefix] = prim

                    child_counters = {}
                    for child in prim.GetChildren():
                        if child.GetName() != "Phys_Rep":
                            self._assign_xnames_recursive(child, stack, child_counters)

                    stack.pop()
                    return

                else:
                    old_val = counters.get(type_code, 0)
                    counters[type_code] = old_val + 1
                    idx = counters[type_code]

                    prefix = "".join(f"{code}{num}" for (code, num) in stack)
                    leaf_xname = f"{prefix}{type_code}{idx}"

                    xname_attr = attributes_scope.GetAttribute("xname")
                    if not xname_attr:
                        xname_attr = attributes_scope.CreateAttribute("xname", Sdf.ValueTypeNames.String)
                    xname_attr.Set(leaf_xname)
                    # Print statement to verify correct xname assignment
                    # print(f"[exadigit.data_loader] Assigned xname '{leaf_xname}' to leaf {prim.GetPath()}")

                    self.lookup_dict[leaf_xname] = prim

        for child in prim.GetChildren():
            if child.GetName() != "Phys_Rep":
                self._assign_xnames_recursive(child, stack, counters)

    def refresh_scene(self):
        print("[exadigit.data_loader] Rebuilding xname assignments and lookup dictionary...")
        self.lookup_dict.clear()
        stage = omni.usd.get_context().get_stage()
        if not stage:
            print("[exadigit.data_loader] No stage loaded.")
            return
        root_prim = stage.GetDefaultPrim()
        if not root_prim:
            print("[exadigit.data_loader] No default prim found.")
            return
        self._assign_xnames_recursive(root_prim)
        print("[exadigit.data_loader] Xname assignment and lookup rebuild completed.")

    def propagate_data(self):
        print("[exadigit.data_loader] Starting data propagation...")
        # Data for stress-test.usd
        test_data = self.generate_test_data(52, 21, 1, 4, 8)

        # Data for test.usd
        #test_data = self.generate_test_data(2, 21, 1, 4, 8)

        for xname, values in test_data.items():
            prim = self.lookup_dict.get(xname)
            if prim:
                self._update_attributes(prim, values)
        print("[exadigit.data_loader] Data propagation completed.")

    def _update_attributes(self, prim, values):
        attributes_scope = prim.GetChild("attributes")
        if not attributes_scope:
            return

        for key, value in values.items():
            if isinstance(value, float):
                attr_type = Sdf.ValueTypeNames.Double
            elif isinstance(value, int):
                attr_type = Sdf.ValueTypeNames.Int
            elif isinstance(value, str):
                attr_type = Sdf.ValueTypeNames.String
            else:
                print(f"[exadigit.data_loader] Unsupported value type for {key}: {type(value)}")
                continue

            attr = attributes_scope.GetAttribute(key)
            if not attr:
                attr = attributes_scope.CreateAttribute(key, attr_type)
            attr.Set(value)
            # Print statement to help verify propagation
            #print(f"[exadigit.data_loader] Updated '{key}' for {prim.GetPath()} with value {value}")

        ### Commenting material change out for now, it's a bottleneck ###
        # Apply material if power is negative
        # if "power" in values and values["power"] < 0:
        #     self._apply_material(prim, "/World/Looks/RedMat")

    def _apply_material(self, prim, material_path):
        stage = prim.GetStage()
        material_prim = stage.GetPrimAtPath(material_path)
        if not material_prim:
            print(f"[exadigit.data_loader] Material at {material_path} not found.")
            return
        material = UsdShade.Material(material_prim)
        if material:
            binding_api = UsdShade.MaterialBindingAPI(prim)
            binding_api.Bind(material, UsdShade.Tokens.strongerThanDescendants)
            print(f"[exadigit.data_loader] Material '{material_path}' applied to {prim.GetPath()}")

    def generate_test_data(self, num_cabinets=2, num_nodes=21, num_processors=1, num_accelerators=4, num_disks=8):
        """
        Generates test data corresponding to every single component within the data center for stress testing.
        Includes cabinets, nodes, processors, accelerators, and disks.
        """
        test_data = {}
        values = {"power": -1.0, "temperature": 50, "status": "active"}

        for cab in range(1, num_cabinets + 1):
            cabinet_key = f"x{cab}"
            test_data[cabinet_key] = values.copy()

            for node in range(1, num_nodes + 1):
                node_key = f"x{cab}n{node}"
                test_data[node_key] = values.copy()

                # Processors
                for proc in range(1, num_processors + 1):
                    processor_key = f"{node_key}p{proc}"
                    test_data[processor_key] = values.copy()

                # Accelerators
                for acc in range(1, num_accelerators + 1):
                    accelerator_key = f"{node_key}a{acc}"
                    test_data[accelerator_key] = values.copy()

                # Disks
                for disk in range(1, num_disks + 1):
                    disk_key = f"{node_key}d{disk}"
                    test_data[disk_key] = values.copy()

        return test_data

    def on_shutdown(self):
        print("[exadigit.data_loader] Extension shutdown")
