"""
Core Library for Pocket Pharmacist

This package contains pure business logic that is not dependent on specific frameworks or services.
It provides only core functionality and integrates with external services through interfaces.

1. interfaces - Core interfaces definition
2. orchestration - Business logic orchestration
3. services - Core service implementation

This structure ensures separation of concerns and improves code reusability and testability.
"""

import logging

# Configure logging for the core library
logger = logging.getLogger(__name__)
