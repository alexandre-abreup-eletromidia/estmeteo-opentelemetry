import logging
import sys
from src.utils import get_google_credentials

# Configure basic logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

if __name__ == "__main__":
    print("----------------------------------------------------------------")
    print("  estmeteo-opentelemetry - Google OAuth2 Setup")
    print("----------------------------------------------------------------")
    try:
        creds = get_google_credentials()
        print("\n[SUCCESS] Authentication completed successfully!")
        print(f"[INFO] Token saved.")
    except Exception as e:
        print(f"\n[ERROR] Authentication failed: {e}")
        sys.exit(1)
