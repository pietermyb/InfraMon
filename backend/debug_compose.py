
import asyncio
import logging
from app.services.docker_service import DockerService
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_octopus():
    print("--- Starting Debug ---")
    service = DockerService(db=None) # DB not needed for this check
    
    try:
        # Get container directly
        container = service.client.containers.get("OctopusDeploy")
        print(f"Found container: {container.name} ({container.id[:12]})")
        
        attrs = container.attrs
        labels = attrs.get("Config", {}).get("Labels", {})
        
        print("\n--- Labels ---")
        for k, v in labels.items():
            if "compose" in k:
                print(f"{k}: {v}")
                
        print("\n--- Mounts ---")
        for m in attrs.get("Mounts", []):
            if m.get("Type") == "bind":
                print(f"Source: {m.get('Source')} -> Target: {m.get('Destination')}")

        print("\n--- Testing find_compose_file ---")
        compose_file = await service.find_compose_file(container)
        print(f"RESULT: {compose_file}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_octopus())
