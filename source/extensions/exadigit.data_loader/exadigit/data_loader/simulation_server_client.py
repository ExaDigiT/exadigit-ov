import requests
import os
import json

class SimulationServerClient:
    def __init__(self, base_url="http://localhost:8080", token=None):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = token or os.getenv("RAPS_TOKEN")  # Use token from environment variable if not provided

    def make_request(self, endpoint, method="GET", payload=None):
        """
        Generalized method for making API requests to the simulation server.

        :param endpoint: API endpoint (e.g., "/api/simulation/data")
        :param method: HTTP method ("GET", "POST", "PUT", etc.)
        :param payload: JSON payload for POST/PUT requests
        :return: JSON response or None if an error occurs
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            if method == "GET":
                response = self.session.get(url, headers=headers)
            elif method in ["POST", "PUT"]:
                response = self.session.request(method, url, headers=headers, json=payload)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"[simulation_server_client] Error making request to {url}: {e}")
            return None

    def run_simulation(self, simulation_params):
        """
        Initiates a simulation by sending a POST request to the SimulationServer API.

        :param simulation_params: Dictionary containing the parameters required to run the simulation.
        :return: Response from the server indicating the status of the simulation initiation.
        """
        endpoint = "/api/simulations/run"  # Update this to the correct endpoint as specified in the API docs
        response = self.make_request(endpoint, method="POST", payload=simulation_params)
        return response
