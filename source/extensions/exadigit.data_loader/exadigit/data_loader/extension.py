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
from pxr import Usd, UsdGeom, Sdf, UsdShade
import omni.usd
import os
import json


class DataLoader(omni.ext.IExt):
    """This extension dynamically propagates multiple attributes, assigns xnames based on hierarchy,
       and updates materials based on conditions with optimized traversal."""

    def on_startup(self, _ext_id):
        """Called every time the extension is activated."""
        print("[exadigit.data_loader] Extension startup")

        self._test_data = {
            # Make all of node 1's GPUs red
            "n1a1": {"power": -1.0},
            "n1a2": {"power": -1.0},
            "n1a3": {"power": -1.0},
            "n1a4": {"power": -1.0},

            # Make two of node 2's GPUs red
            "n2a1": {"power": -1.0},
            "n2a2": {"power": 1.0},
            "n2a3": {"power": 1.0},
            "n2a4": {"power": -1.0},

            # Make one of node 3's GPUs red
            "n3a1": {"power": -1.0},
            "n3a2": {"power": 1.0},
            "n3a3": {"power": 1.0},
            "n3a4": {"power": 1.0},
        }

        # Dynamically load the JSON from the same directory as the extension
        current_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(current_dir, "xnames_map.json"), "r") as f:
            self.xnames_map = json.load(f)

        self._window = ui.Window("Data Loader", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                ui.Label("Click 'Propagate Data' to update attributes and materials.")
                ui.Button("Propagate Data", clicked_fn=self.propagate_data)
                ui.Label("Click 'Assign Xnames' to assign xnames based on hierarchy.")
                ui.Button("Assign Xnames", clicked_fn=self.assign_xnames)

    def _assign_xnames_recursive(self, prim, stack=None, counters=None):
        """
        Recursively assign xnames by traversing the hierarchy.
        For prims marked as container types (per xnames_map), a new level is pushed on the stack
        and child counters are reset. Leaf types simply increment their counter within the current container.
        """
        if stack is None:
            stack = []  # Stack of (type_code, index) pairs representing the current hierarchy path.
        if counters is None:
            counters = {}  # Counters for types at the current level.

        attributes_scope = prim.GetChild("attributes")
        if attributes_scope:
            type_attr = attributes_scope.GetAttribute("type")
            if type_attr and type_attr.HasAuthoredValue():
                prim_type = type_attr.Get()
                # Look up the type mapping. If not found, default to code "u" and non-container.
                type_info = self.xnames_map.get(prim_type, {"code": "u", "container": False})
                type_code = type_info["code"]
                is_container = type_info.get("container", False)

                if is_container:
                    # Increment the counter for this container type at the current level.
                    counters[type_code] = counters.get(type_code, 0) + 1
                    idx = counters[type_code]
                    stack.append((type_code, idx))
                    prefix = "".join(f"{code}{num}" for (code, num) in stack)
                    xname_attr = attributes_scope.GetAttribute("xname")
                    if not xname_attr:
                        xname_attr = attributes_scope.CreateAttribute("xname", Sdf.ValueTypeNames.String)
                    xname_attr.Set(prefix)
                    print(f"[exadigit.data_loader] Assigned xname '{prefix}' to {prim.GetPath()} (container)")

                    # Process children with a fresh counter dictionary.
                    child_counters = {}
                    for child in prim.GetChildren():
                        if child.GetName() != "Phys_Rep":
                            self._assign_xnames_recursive(child, stack, child_counters)
                    stack.pop()
                    # IMPORTANT: return immediately so that children are not processed twice.
                    return
                else:
                    # Leaf type: increment its counter in the current level.
                    counters[type_code] = counters.get(type_code, 0) + 1
                    idx = counters[type_code]
                    prefix = "".join(f"{code}{num}" for (code, num) in stack)
                    leaf_xname = f"{prefix}{type_code}{idx}"
                    xname_attr = attributes_scope.GetAttribute("xname")
                    if not xname_attr:
                        xname_attr = attributes_scope.CreateAttribute("xname", Sdf.ValueTypeNames.String)
                    xname_attr.Set(leaf_xname)
                    print(f"[exadigit.data_loader] Assigned xname '{leaf_xname}' to {prim.GetPath()} (leaf)")
        # Process any children that weren't handled above.
        for child in prim.GetChildren():
            if child.GetName() != "Phys_Rep":
                self._assign_xnames_recursive(child, stack, counters)

    def assign_xnames(self):
        """Assign xnames to components based on the hierarchical mapping provided in xnames_map.json."""
        stage = omni.usd.get_context().get_stage()
        if not stage:
            print("[exadigit.data_loader] No stage loaded.")
            return
        root_prim = stage.GetDefaultPrim()
        if not root_prim:
            print("[exadigit.data_loader] No default prim found.")
            return

        print("[exadigit.data_loader] Starting xname assignment...")
        # Start with an empty stack and counter dictionary.
        self._assign_xnames_recursive(root_prim, stack=[], counters={})
        print("[exadigit.data_loader] Xname assignment completed.")

    def _apply_material(self, prim, material_path, stronger=True):
        """Apply material to a prim with configurable binding strength."""
        stage = prim.GetStage()
        material_prim = stage.GetPrimAtPath(material_path)
        if not material_prim:
            print(f"[exadigit.data_loader] Material at {material_path} not found.")
            return
        material = UsdShade.Material(material_prim)
        if material:
            binding_api = UsdShade.MaterialBindingAPI(prim)
            strength = UsdShade.Tokens.strongerThanDescendants if stronger else UsdShade.Tokens.weakerThanDescendants
            binding_api.Bind(material, strength)
            print(f"[exadigit.data_loader] Material '{material_path}' applied to {prim.GetPath()} with {'stronger' if stronger else 'weaker'} binding.")

    def _determine_value_type(self, value):
        """Determine the USD value type based on Python type."""
        if isinstance(value, int):
            return Sdf.ValueTypeNames.Int
        elif isinstance(value, float):
            return Sdf.ValueTypeNames.Double
        elif isinstance(value, str):
            return Sdf.ValueTypeNames.String
        else:
            print(f"[exadigit.data_loader] Unsupported value type for value: {value}")
            return None

    def _update_attributes(self, prim, target_xname, attributes_dict):
        """Update multiple attributes dynamically and adjust material based on power condition."""
        attributes_scope = prim.GetChild("attributes")
        if attributes_scope:
            xname_attr = attributes_scope.GetAttribute("xname")
            if xname_attr and xname_attr.HasAuthoredValue():
                xname = xname_attr.Get()
                print(f"Found xname: {xname} on {prim.GetPath()}")
                if xname == target_xname:
                    print(f"Updating attributes for {xname}")
                    for attr_name, attr_value in attributes_dict.items():
                        value_type = self._determine_value_type(attr_value)
                        if value_type:
                            existing_attr = attributes_scope.GetAttribute(attr_name)
                            if existing_attr:
                                print(f"Updating existing attribute '{attr_name}' to {attr_value}")
                                existing_attr.Set(attr_value)
                            else:
                                print(f"Creating attribute '{attr_name}' with value {attr_value}")
                                new_attr = attributes_scope.CreateAttribute(attr_name, value_type)
                                new_attr.Set(attr_value)

                    # Apply material conditionally with weaker binding if power is positive.
                    if "power" in attributes_dict:
                        power_value = attributes_dict["power"]
                        if power_value < 0:
                            self._apply_material(prim, "/World/Looks/RedMat", stronger=True)
                        else:
                            self._apply_material(prim, "/World/Looks/RedMat", stronger=False)
                    return True
        return False

    def _recursive_traverse(self, prim, data, matched_keys):
        """Recursively traverse the prim hierarchy while skipping 'Phys_Rep' payloads."""
        if len(matched_keys) == len(data):
            print("[exadigit.data_loader] All matches found. Stopping traversal.")
            return

        print(f"Traversing prim: {prim.GetPath()}")
        attributes_scope = prim.GetChild("attributes")
        if attributes_scope:
            for xname_key, attributes_dict in data.items():
                if xname_key not in matched_keys:
                    if self._update_attributes(prim, xname_key, attributes_dict):
                        matched_keys.add(xname_key)

        for child in prim.GetChildren():
            if child.GetName() == "Phys_Rep":
                print(f"Skipping 'Phys_Rep' payload at {child.GetPath()}")
                continue
            self._recursive_traverse(child, data, matched_keys)

    def propagate_data(self):
        """Triggered by the UI button to propagate data and adjust materials accordingly."""
        stage = omni.usd.get_context().get_stage()
        if not stage:
            print("[exadigit.data_loader] No stage loaded.")
            return
        print(f"[exadigit.data_loader] Stage loaded: {stage}")

        root_prim = stage.GetDefaultPrim()
        if not root_prim:
            print("[exadigit.data_loader] No default prim found.")
            return
        print(f"[exadigit.data_loader] Default prim: {root_prim.GetPath()}")

        print("[exadigit.data_loader] Starting data propagation with dynamic material adjustments...")
        matched_keys = set()
        self._recursive_traverse(root_prim, self._test_data, matched_keys)
        print("[exadigit.data_loader] Data propagation and material adjustments completed.")

    def on_shutdown(self):
        """Called every time the extension is deactivated to clean up state."""
        print("[exadigit.data_loader] Extension shutdown")
