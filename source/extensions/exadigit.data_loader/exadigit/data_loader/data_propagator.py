from pxr import Sdf, UsdShade


class DataPropagator:
    def __init__(self, name_mapper):
        """Initializes DataPropagator with access to NameMapper's lookup_dict."""
        self.lookup_dict = name_mapper.lookup_dict

    def update_attributes(self, prim, values):
        """Updates attributes on a prim."""
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

    def propagate_data(self, data):
        """Propagates data to the scene using lookup_dict."""
        for xname, values in data.items():
            prim = self.lookup_dict.get(xname)
            if prim:
                self.update_attributes(prim, values)
