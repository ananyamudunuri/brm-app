import os
import json
from google.cloud import secretmanager
from typing import Optional

class SecretManager:
    def __init__(self):
        self.client = None
        self.cache = {}
        
    def _get_client(self):
        """Initialize Secret Manager client"""
        if not self.client:
            try:
                self.client = secretmanager.SecretManagerServiceClient()
            except Exception as e:
                print(f"Warning: Secret Manager not available: {e}")
                self.client = None
        return self.client
    
    async def get_secret(self, secret_name: str, version: str = "latest") -> Optional[str]:
        """Fetch secret from GCP Secret Manager"""
        # Check cache first
        cache_key = f"{secret_name}:{version}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        client = self._get_client()
        if not client:
            # Fallback to environment variable or local file for development
            fallback = os.getenv(secret_name.upper().replace("-", "_"))
            if fallback:
                return fallback
            
            # Try local file for development
            try:
                with open(f"/run/secrets/{secret_name}", "r") as f:
                    value = f.read().strip()
                    self.cache[cache_key] = value
                    return value
            except:
                pass
            return None
        
        try:
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "PROJECT-A")
            secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/{version}"
            response = client.access_secret_version(request={"name": secret_path})
            value = response.payload.data.decode("UTF-8")
            
            # Cache the value
            self.cache[cache_key] = value
            return value
        except Exception as e:
            print(f"Error fetching secret {secret_name}: {e}")
            return None

secret_manager = SecretManager()