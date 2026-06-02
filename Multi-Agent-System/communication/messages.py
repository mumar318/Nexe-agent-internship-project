# communication/messages.py — Message schema for inter-agent communication

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MessageType(str, Enum):
    TASK_PLAN       = "task_plan"        # Orchestrator broadcasts the plan
    TASK_DELEGATION = "task_delegation"  # Orchestrator delegates a step to an agent
    TASK_RESULT     = "task_result"      # Agent returns result to orchestrator
    TASK_COMPLETE   = "task_complete"    # Orchestrator broadcasts completion
    STATUS_UPDATE   = "status_update"    # Any agent broadcasts a status update
    ERROR           = "error"            # Agent reports an error


@dataclass
class Message:
    sender:    str
    recipient: str          # agent_id or "broadcast"
    msg_type:  MessageType
    payload:   dict[str, Any]
    msg_id:    str   = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str   = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "msg_id":    self.msg_id,
            "sender":    self.sender,
            "recipient": self.recipient,
            "msg_type":  self.msg_type.value,
            "payload":   self.payload,
            "timestamp": self.timestamp,
        }
