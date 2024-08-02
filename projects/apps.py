from django.apps import AppConfig
import signal
import atexit
from .utils import register_service, deregister_service
import logging

logger = logging.getLogger(__name__)

class ProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects'
    
    def ready(self):
        # Register the service when the app is ready
        self.register_service_with_retries()

        # Deregister the service on shutdown
        def handle_shutdown(*args, **kwargs):
            deregister_service()
        
        # Use atexit to deregister on normal exit
        atexit.register(handle_shutdown)
        
        # Handle termination signals to deregister on abrupt shutdown
        signal.signal(signal.SIGTERM, handle_shutdown)
        signal.signal(signal.SIGINT, handle_shutdown)
    
    def register_service_with_retries(self, retries=3):
        for attempt in range(retries):
            try:
                register_service()
                break
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to register service on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    continue
                else:
                    logger.critical("Could not register service after several attempts. Exiting.")
                    exit(1)
