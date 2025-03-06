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

    def _get_type(self, prim):
        """Retrieve the 'type' attribute from the prim's attributes scope."""
        attributes_scope = prim.GetChild("attributes")
        if attributes_scope:
            type_attr = attributes_scope.GetAttribute("type")
            if type_attr and type_attr.HasAuthoredValue():
                return type_attr.Get()
        return None

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
                    old_val = counters.get(type_code, 0)
                    counters[type_code] = old_val + 1
                    idx = counters[type_code]

                    # Push (type_code, idx) onto the stack
                    stack.append((type_code, idx))
                    prefix = "".join(f"{code}{num}" for (code, num) in stack)

                    xname_attr = attributes_scope.GetAttribute("xname")
                    if not xname_attr:
                        xname_attr = attributes_scope.CreateAttribute("xname", Sdf.ValueTypeNames.String)
                    xname_attr.Set(prefix)
                    print(f"[exadigit.data_loader] Assigned xname '{prefix}' to container {prim.GetPath()}")

                    # Store in lookup dictionary
                    self.lookup_dict[prefix] = prim

                    # Process children with a **fresh counter dictionary** (ensures nodes within each container are correctly numbered)
                    child_counters = {}
                    for child in prim.GetChildren():
                        if child.GetName() != "Phys_Rep":
                            self._assign_xnames_recursive(child, stack, child_counters)

                    # Pop from the stack when done (restores correct hierarchy state)
                    stack.pop()
                    return  # Return early so children are not re-processed below

                else:
                    # Leaf type
                    old_val = counters.get(type_code, 0)
                    counters[type_code] = old_val + 1
                    idx = counters[type_code]

                    # Build prefix from the stack
                    prefix = "".join(f"{code}{num}" for (code, num) in stack)
                    leaf_xname = f"{prefix}{type_code}{idx}"

                    xname_attr = attributes_scope.GetAttribute("xname")
                    if not xname_attr:
                        xname_attr = attributes_scope.CreateAttribute("xname", Sdf.ValueTypeNames.String)
                    xname_attr.Set(leaf_xname)
                    print(f"[exadigit.data_loader] Assigned xname '{leaf_xname}' to leaf {prim.GetPath()}")

                    # Store in lookup dictionary
                    self.lookup_dict[leaf_xname] = prim

        # Process any children not handled above (i.e., no 'attributes' or container logic)
        for child in prim.GetChildren():
            if child.GetName() != "Phys_Rep":
                self._assign_xnames_recursive(child, stack, counters)

    def refresh_scene(self):
        """Rebuild xname assignments and lookup dictionary."""
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
        """Propagate data efficiently using lookup dictionary."""
        print("[exadigit.data_loader] Starting data propagation...")
        # STRESS TEST
        test_data = {
                        # ROW 1
                        "x1n1": {"power": -1.0},
                        "x1n2": {"power": -1.0},
                        "x1n3": {"power": -1.0},
                        "x1n4": {"power": -1.0},
                        "x2n3a1": {"power": -1.0},
                        "x2n3a2": {"power": -1.0},
                        "x2n3a3": {"power": -1.0},
                        "x2n3a4": {"power": -1.0},
                        "x5": {"power": -1.0},
                        "x7n1": {"power": -1.0},
                        "x7n3": {"power": -1.0},
                        "x10": {"power": -1.0},
                        "x14n2": {"power": -1.0},
                        "x14n4": {"power": -1.0},
                        "x16n1": {"power": -1.0},
                        "x16n2": {"power": -1.0},
                        "x16n3": {"power": -1.0},
                        "x16n4": {"power": -1.0},

                        # ROW 2
                        "x18": {"power": -1.0},
                        "x19": {"power": -1.0},
                        "x20": {"power": -1.0},
                        "x21": {"power": -1.0},
                        "x25n1": {"power": -1.0},
                        "x25n2": {"power": -1.0},
                        "x25n3": {"power": -1.0},
                        "x25n4": {"power": -1.0},
                        "x30n1": {"power": -1.0},
                        "x30n4": {"power": -1.0},

                        # ROW 3
                        "x38n1": {"power": -1.0},
                        "x38n2": {"power": -1.0},
                        "x38n3": {"power": -1.0},
                        "x38n4": {"power": -1.0},
                        "x40n1": {"power": -1.0},
                        "x40n2": {"power": -1.0},
                        "x40n3": {"power": -1.0},
                        "x40n4": {"power": -1.0},
                        "x45": {"power": -1.0},
                        "x46": {"power": -1.0},
                        "x49n2a1": {"power": -1.0},
                        "x49n2a3": {"power": -1.0},
                        "x52n3a1": {"power": -1.0},
                        "x52n3a2": {"power": -1.0},
                        "x52n3a3": {"power": -1.0},
                        "x52n3a4": {"power": -1.0}
                    }
        for xname, values in test_data.items():
            prim = self.lookup_dict.get(xname)
            if prim:
                attributes_scope = prim.GetChild("attributes")
                if attributes_scope:
                    for key, value in values.items():
                        attr = attributes_scope.GetAttribute(key)
                        if not attr:
                            attr = attributes_scope.CreateAttribute(key, Sdf.ValueTypeNames.Double)
                        attr.Set(value)
                        print(f"[exadigit.data_loader] Updated '{key}' for {xname} with value {value}")

                # Apply material logic (example)
                material_path = "/World/Looks/RedMat"
                self._apply_material(prim, material_path, stronger=True)
        print("[exadigit.data_loader] Data propagation completed.")

    def _apply_material(self, prim, material_path, stronger=True):
        """Apply material to a prim."""
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

    def on_shutdown(self):
        print("[exadigit.data_loader] Extension shutdown")
