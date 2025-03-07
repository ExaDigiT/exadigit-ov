import json
import os
from pxr import Usd, Sdf
import omni.ext
import omni.usd

class NameMapper:
    def __init__(self):
        """Initializes NameMapper and loads xnames mapping."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(current_dir, "xnames_map.json"), "r") as f:
            self.xnames_map = json.load(f)

        self.lookup_dict = {}  # Stores xname-to-prim mappings

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
