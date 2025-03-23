from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class ChatbotRequest:
    intent: str
    params: Dict[str, Optional[str]]

@dataclass
class ChatbotResponse:
    message: str