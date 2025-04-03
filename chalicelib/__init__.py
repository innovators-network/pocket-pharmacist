"""
Chalice Library for Pocket Pharmacist

This package contains code used with the AWS Chalice framework.
It is organized as follows:

1. Interfaces - User interface adapters
2. Orchestration - Service orchestration and flow management
3. Services - Core business services and external integration

This architecture promotes separation of concerns and makes the code more maintainable.
"""

import logging
import os

# Configure logging
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)