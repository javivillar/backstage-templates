"""Print the OpenAPI document of the API: python -m ${{ values.name }}.openapi > openapi.json

The frontend generates its types from that file, so the two sides cannot drift apart.
"""

import json

from refresquito_fastapi import Settings

from .main import build

if __name__ == "__main__":
    print(json.dumps(build(Settings(app_name="${{ values.name }}", log_level="ERROR")).openapi(), indent=2, sort_keys=True))
