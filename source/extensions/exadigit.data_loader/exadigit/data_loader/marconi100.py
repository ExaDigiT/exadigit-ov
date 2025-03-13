class Marconi100DataLoader:
    """Handles data parsing and xname mapping for the Marconi100 system."""

    def __init__(self, name_mapper):
        self.name_mapper = name_mapper  # Use NameMapper for xname lookups

    def parse_cdu_response(self, response):
        """Parses CDU response and maps xnames for Marconi100."""
        parsed_data = {}

        for item in response.get("results", []):
            xname = self.name_mapper.map_cdu_xname(item["id"])  # Marconi100-specific mapping
            parsed_data[xname] = {
                "power": item.get("power", -1.0),
                "temperature": item.get("temperature", 75.0),
                "status": item.get("status", "unknown"),
            }

        return parsed_data

    def parse_cep_response(self, response):
        """Parses CEP response and maps xnames for Marconi100."""
        parsed_data = {}

        for item in response.get("results", []):
            xname = self.name_mapper.map_cep_xname(item["id"])  # Marconi100-specific mapping
            parsed_data[xname] = {
                "power": item.get("power", -1.0),
                "temperature": item.get("temperature", 75.0),
                "status": item.get("status", "unknown"),
            }

        return parsed_data
