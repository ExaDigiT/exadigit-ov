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


class DataLoader(omni.ext.IExt):
    """This extension dynamically propagates multiple attributes, handles various data types, and updates materials based on conditions with optimized hierarchical traversal and dynamic material adjustments."""

    def on_startup(self, _ext_id):
        """Called every time the extension is activated."""
        print("[exadigit.data_loader] Extension startup")

        self._test_data = {
            "x1n1p1": {"power": 50.0, "utilization": 25, "status": "active"},
            "x1n1a1": {"power": -10.0, "utilization": 80, "status": "inactive"},
            "x1n1a2": {"power": 20.0, "utilization": 80, "status": "inactive"},
            "x1n1a3": {"power": 30.0, "utilization": 80, "status": "inactive"},
            "x1n1a4": {"power": -30.0, "utilization": 80, "status": "inactive"}
        }

        self._window = ui.Window("Data Loader", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                ui.Label("Click 'Propagate Data' to update attributes and materials.")
                ui.Button("Propagate Data", clicked_fn=self.propagate_data)

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

                    # Apply material conditionally with weaker binding if power is positive
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
