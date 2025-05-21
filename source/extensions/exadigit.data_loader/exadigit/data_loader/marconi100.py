class Marconi100DataLoader:
    """Handles data parsing and xname mapping for the Marconi100 system."""

    def __init__(self, name_mapper):
        self.name_mapper = name_mapper  # Use NameMapper for xname lookups

    def parse_cdu_response(self, response):
        """Parses CDU response and maps xnames for Marconi100."""
        parsed_data = {}

        print("CDU RESPONSE:")
        print(response)

        for item in response.get("data", []):
            print(item["name"])
            print()
            # xname = self.name_mapper.map_cdu_xname(item["name"])  # Marconi100-specific mapping
            # parsed_data[xname] = {
            #     "power": item.get("power", -1.0),
            #     "temperature": item.get("temperature", 75.0),
            #     "status": item.get("status", "unknown"),
            # }

            # In this part of the code you would just need to parse the "data" field of response then make sure the
            # format of parsed_data matches the format of your lookup map. The response from the simulation server looks
            # like this:
            #             'data': [
            # {'timestamp': '2020-06-10T09:00:00.000Z', 'name': 'cdu01', 'row': 0, 'col': 1, 'rack_1_power': 12.365200000000002, 'rack_2_power': 12.365200000000002, 'rack_3_power': 12.365200000000002, 'total_power': 37.095600000000005, 'rack_1_loss': 0.0, 'rack_2_loss': 0.0, 'rack_3_loss': 0.0, 'total_loss': 0.0, 'work_done_by_cdup': None, 'rack_return_temp': None, 'rack_supply_temp': None, 'rack_supply_pressure': None, 'rack_return_pressure': None, 'rack_flowrate': None, 'facility_return_temp': None, 'facility_supply_temp': None, 'facility_supply_pressure': None, 'facility_return_pressure': None, 'facility_flowrate': None},

            # {'timestamp': '2020-06-10T09:00:00.000Z', 'name': 'cdu02', 'row': 0, 'col': 2, 'rack_1_power': 12.365200000000002, 'rack_2_power': 12.365200000000002, 'rack_3_power': 12.365200000000002, 'total_power': 37.095600000000005, 'rack_1_loss': 0.0, 'rack_2_loss': 0.0, 'rack_3_loss': 0.0, 'total_loss': 0.0, 'work_done_by_cdup': None, 'rack_return_temp': None, 'rack_supply_temp': None, 'rack_supply_pressure': None, 'rack_return_pressure': None, 'rack_flowrate': None, 'facility_return_temp': None, 'facility_supply_temp': None, 'facility_supply_pressure': None, 'facility_return_pressure': None, 'facility_flowrate': None},...}

            # So in the end based on the knowledge of your system you'd need parsed_data to look something like this:
            # parsed_data = {x1 : {"power": value of rack_1_power, ... "rack_supply_temp": value of rack_supply_temp for x1}, ..., },
            #               {x2 : {"power": value of rack_1_power, ... "rack_supply_temp": value of rack_supply_temp for x2}, ..., },
            #               {xn: {"power": value of rack_1_power, ... "rack_supply_temp": value of rack_supply_temp for xn}, ..., },

        return parsed_data

    # def parse_cep_response(self, response):
    #     """Parses CEP response and maps xnames for Marconi100."""
    #     parsed_data = {}

    #     for item in response.get("data", []):
    #         xname = self.name_mapper.map_cep_xname(item["name"])  # Marconi100-specific mapping
    #         parsed_data[xname] = {
    #             "power": item.get("power", -1.0),
    #             "temperature": item.get("temperature", 75.0),
    #             "status": item.get("status", "unknown"),
    #         }

    #    return parsed_data
