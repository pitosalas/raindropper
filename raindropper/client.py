import os
import requests

RAINDROP_API = "https://api.raindrop.io/rest/v1"


class RaindropClient:
    # Reads RAINDROP_TOKEN from env; crashes if missing.
    def __init__(self):
        self.token = os.environ["RAINDROP_TOKEN"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def fetch_tags(self):
        # Returns list of tag objects from the Raindrop API.
        response = requests.get(f"{RAINDROP_API}/tags", headers=self.headers)
        response.raise_for_status()
        return response.json().get("items", [])
