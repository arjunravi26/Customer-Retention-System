import os
import yaml
from functools import lru_cache

@lru_cache(maxsize=1)
def load_config(config_path="/config.yaml"):
    """Load service URLs from config.yaml and override with environment variables."""
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        config = {"services": {}}

    services = config.get("services", {})

    return services

def get_service_url(service_name):
    """Get the URL for a given service."""
    services = load_config()
    return services.get(service_name, {}).get('url','')