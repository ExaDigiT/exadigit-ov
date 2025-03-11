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

    def post_simulation_run(self, simulation_params):
        """Runs a simulation by sending a POST request to the Simulation Server API."""
        response = self.make_request("/simulation/run", method="POST", payload=simulation_params)

        if response is None:
            print("[simulation_server_client] No response received. The request might be malformed.")
        else:
            print(f"[simulation_server_client] Response: {response}")

        return response

    def get_simulation_list(self, fields=None, limit=None, offset=None):
        """Fetches the list of available simulations with correct field formatting."""
        query_params = []

        if fields:
            # Convert list of fields into a single comma-separated string
            query_params.append(f"fields={','.join(fields)}")

        if limit is not None:
            query_params.append(f"limit={limit}")
        if offset is not None:
            query_params.append(f"offset={offset}")

        query_string = "?" + "&".join(query_params) if query_params else ""
        url = f"/simulation/list{query_string}"

        print(f"[simulation_server_client] Making request to: {self.base_url}{url}")

        response = self.make_request(url, method="GET")

        if response is None:
            print("[simulation_server_client] ERROR: No response received (possible malformed request).")
        else:
            print(f"[simulation_server_client] Received response: {response}")

        return response


    def get_simulation(self, simulation_id):
        """Fetches details of a specific simulation."""
        return self.make_request(f"/simulation/{simulation_id}")

    def get_simulation_cooling_cdu(self, simulation_id):
        """Retrieves cooling CDU data for a given simulation."""
        return self.make_request(f"/simulation/{simulation_id}/cooling/cdu")

    def get_simulation_cooling_cep(self, simulation_id):
        """Retrieves cooling CEP data for a given simulation."""
        return self.make_request(f"/simulation/{simulation_id}/cooling/cep")

    def get_simulation_scheduler_jobs(self, simulation_id):
        """Retrieves job scheduler data for a simulation."""
        return self.make_request(f"/simulation/{simulation_id}/scheduler/jobs")

    def get_simulation_scheduler_job_power_history(self, simulation_id, job_id):
        """Fetches power history for a specific job within a simulation."""
        return self.make_request(f"/simulation/{simulation_id}/scheduler/jobs/{job_id}/power-history")

    def get_simulation_scheduler_system(self, simulation_id):
        """Retrieves system scheduler data for a simulation."""
        return self.make_request(f"/simulation/{simulation_id}/scheduler/system")

    def get_system_info(self, system_name):
        """Fetches system information."""
        return self.make_request(f"/system-info/{system_name}")
