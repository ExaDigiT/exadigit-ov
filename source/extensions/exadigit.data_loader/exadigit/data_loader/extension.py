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
from pxr import Usd, UsdGeom, Sdf
import omni.usd


class DataLoader(omni.ext.IExt):
    """This extension propagates power data to matching components based on xname."""

    def on_startup(self, _ext_id):
        """Called every time the extension is activated."""
        print("[exadigit.data_loader] Extension startup")

        self._test_data = {"x1n1p1": 50.0, "x1n1a1": -10.0}
        self._window = ui.Window("Data Loader", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                ui.Label("Click 'Propagate Data' to update power attributes.")
                ui.Button("Propagate Data", clicked_fn=self.propagate_data)

    def _update_power(self, prim, target_xname, power_value):
        """Update the power attribute if xname matches target_xname."""
        attributes_scope = prim.GetChild("attributes")
        if attributes_scope:
            xname_attr = attributes_scope.GetAttribute("xname")
            if xname_attr and xname_attr.HasAuthoredValue():
                xname = xname_attr.Get()
                print(f"Found xname: {xname} on {prim.GetPath()}")
                if xname == target_xname:
                    print(f"Updating power for {xname} to {power_value}")
                    power_attr = attributes_scope.GetAttribute("power")
                    if not power_attr:
                        power_attr = attributes_scope.CreateAttribute("power", Sdf.ValueTypeNames.Double)
                    power_attr.Set(power_value)

    def _traverse_top_level(self, prim, data):
        """Traverse only the top-level prims and deeper if 'attributes' scope exists."""
        print(f"Traversing top-level prim: {prim.GetPath()}")
        for child in prim.GetChildren():
            print(f"Checking child: {child.GetPath()}")
            attributes_scope = child.GetChild("attributes")
            if attributes_scope:
                print(f"Found 'attributes' scope in: {child.GetPath()}")
                for xname_key, power_val in data.items():
                    self._update_power(child, xname_key, power_val)

                # Traverse only direct children with 'attributes' scope
                for grandchild in child.GetChildren():
                    grandchild_scope = grandchild.GetChild("attributes")
                    if grandchild_scope:
                        print(f"Found 'attributes' scope in: {grandchild.GetPath()}")
                        for xname_key, power_val in data.items():
                            self._update_power(grandchild, xname_key, power_val)

    def propagate_data(self):
        """Triggered by the UI button to propagate power data to matching components."""
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

        print("[exadigit.data_loader] Starting data propagation...")
        self._traverse_top_level(root_prim, self._test_data)
        print("[exadigit.data_loader] Data propagation completed.")

    def on_shutdown(self):
        """Called every time the extension is deactivated to clean up state."""
        print("[exadigit.data_loader] Extension shutdown")
