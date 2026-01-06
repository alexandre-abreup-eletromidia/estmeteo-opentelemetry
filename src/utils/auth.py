import logging
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from src import config

def get_google_credentials() -> Credentials:
    """Get or refresh Google OAuth2 credentials."""
    creds = None
    token_path = Path(config.GOOGLE_TOKEN_PATH)
    creds_path = Path(config.GOOGLE_CREDENTIALS_PATH)
    
    # Configure logging
    logger = logging.getLogger(__name__)

    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), config.SCOPES)
            logger.info("Loaded credentials from token file")
        except Exception as e:
            logger.warning(f"Error loading token: {e}")
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                logger.info("Refreshing expired token...")
                creds.refresh(Request())
            except Exception as e:
                logger.error(f"Error refreshing token: {e}")
                creds = None
        
        if not creds:
            if not creds_path.exists():
                raise FileNotFoundError(f"Credentials file not found at: {creds_path}")
                
            logger.info("Starting new OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), config.SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json())
        logger.info(f"Saved new token to {token_path}")
    
    return creds
