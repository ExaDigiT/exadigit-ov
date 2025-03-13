import os
from urllib.parse import urlencode

import requests


class SimulationServerClient:
    def __init__(self, base_url="http://localhost:8080", token=None):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = token or os.getenv("RAPS_TOKEN")  # Use token from environment variable if not provided

    def make_request(self, endpoint, method="GET", payload=None):
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        print(f"[simulation_server_client] Sending {method} request to: {url}")
        if payload:
            print(f"[simulation_server_client] Request payload: {payload}")

        try:
            if method == "GET":
                response = self.session.get(url, headers=headers)
            elif method in ["POST", "PUT"]:
                response = self.session.request(method, url, headers=headers, json=payload)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            try:
                return response.json(), response.status_code
            except ValueError:
                print(f"[simulation_server_client] ❌ Invalid JSON response from {url}: {response.text}")
                return None, response.status_code

        except requests.HTTPError as e:
            print(f"[simulation_server_client] HTTP Error {response.status_code}: {e}")
            return None, response.status_code

        except requests.RequestException as e:
            print(f"[simulation_server_client] ❌ Request Exception while calling {method} {url}")
            print(f"[simulation_server_client] Exception Details: {e}")
            return None, None

    def handle_api_response(self, response, status_code, success_message):
        """Handles API responses consistently across all requests."""
        if status_code == 200:
            print(f"[simulation_server_client] ✅ {success_message}: {response}")
        elif status_code == 422:
            print("[simulation_server_client] ⚠️ 422 Error: Unprocessable Entity. Possible malformed request.")
        elif status_code == 404:
            print("[simulation_server_client] ⚠️ 404 Error: Resource not found.")
        elif status_code is None:
            print("[simulation_server_client] ❌ ERROR: No response received (network issue or bad request).")
        else:
            print(f"[simulation_server_client] ❗ Unexpected Error {status_code}: {response}")

        return response, status_code

    def post_simulation_run(self, simulation_params):
        """Runs a simulation by sending a POST request to the Simulation Server API."""
        response, status_code = self.make_request("/simulation/run", method="POST", payload=simulation_params)
        return self.handle_api_response(response, status_code, "Simulation started successfully")

    def get_simulation_list(self, fields=None, limit=None, offset=None):
        """Fetches the list of available simulations with correct field formatting."""
        query_params = {}

        if fields:
            query_params["fields"] = ",".join(fields)

        if limit is not None:
            query_params["limit"] = limit
        if offset is not None:
            query_params["offset"] = offset

        query_string = f"?{urlencode(query_params)}" if query_params else ""
        url = f"/simulation/list{query_string}"

        response, status_code = self.make_request(url, method="GET")
        return self.handle_api_response(response, status_code, "Simulation list retrieved")

    def get_simulation(self, simulation_id):
        """Fetches details of a specific simulation."""
        response, status_code = self.make_request(f"/simulation/{simulation_id}")
        return self.handle_api_response(response, status_code, "Simulation details retrieved")

    def get_simulation_cooling_cdu(self, simulation_id):
        """Retrieves cooling CDU data for a given simulation and handles response codes."""
        response, status_code = self.make_request(f"/simulation/{simulation_id}/cooling/cdu")
        return self.handle_api_response(response, status_code, "CDU data retrieved")

    def get_simulation_cooling_cep(self, simulation_id):
        """Retrieves cooling CEP data for a given simulation."""
        response, status_code = self.make_request(f"/simulation/{simulation_id}/cooling/cep")
        return self.handle_api_response(response, status_code, "CEP data retrieved")

    def get_simulation_scheduler_jobs(self, simulation_id):
        """Retrieves job scheduler data for a simulation."""
        response, status_code = self.make_request(f"/simulation/{simulation_id}/scheduler/jobs")
        return self.handle_api_response(response, status_code, "Scheduler jobs retrieved")

    def get_simulation_scheduler_job_power_history(self, simulation_id, job_id):
        """Fetches power history for a specific job within a simulation."""
        response, status_code = self.make_request(f"/simulation/{simulation_id}/scheduler/jobs/{job_id}/power-history")
        return self.handle_api_response(response, status_code, "Job power history retrieved")

    def get_simulation_scheduler_system(self, simulation_id):
        """Retrieves system scheduler data for a simulation."""
        response, status_code = self.make_request(f"/simulation/{simulation_id}/scheduler/system")
        return self.handle_api_response(response, status_code, "System scheduler data retrieved")

    def get_system_info(self, system_name):
        """Fetches system information."""
        response, status_code = self.make_request(f"/system-info/{system_name}")
        return self.handle_api_response(response, status_code, "System info retrieved")
