from abc import ABC, abstractmethod
import time
import logging
from typing import Dict, Any, Optional
from app.orchestration.blackboard import Blackboard

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, name: str, display_name: str, icon: str, responsibility: str):
        self.name = name
        self.display_name = display_name
        self.icon = icon
        self.responsibility = responsibility
        self.status = "WAITING"
        self.latest_output: Optional[Dict[str, Any]] = None
        self.latest_timestamp: Optional[str] = None
        self.last_execution_ms: Optional[float] = None

    @abstractmethod
    async def process(self, request_id: str, blackboard: Blackboard) -> Dict[str, Any]:
        """
        Execute core agent logic and return the result dictionary.
        """
        pass

    async def execute(self, request_id: str, blackboard: Blackboard) -> Dict[str, Any]:
        """
        Wrapper that handles status tracking, timing, posting to Blackboard, and error handling.
        """
        self.status = "RUNNING"
        start_time = time.time()
        logger.info(f"Agent [{self.name}] started execution for request [{request_id}]")
        
        try:
            output = await self.process(request_id, blackboard)
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            self.last_execution_ms = elapsed_ms
            self.status = "COMPLETED"
            self.latest_output = output
            
            # Post output to Blackboard
            await blackboard.post(
                request_id=request_id,
                agent_name=self.name,
                category=self.name.replace("_agent", ""),
                output_data=output,
                status="COMPLETED"
            )
            
            logger.info(f"Agent [{self.name}] completed in {elapsed_ms}ms")
            return output
        except Exception as e:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            self.last_execution_ms = elapsed_ms
            self.status = "FAILED"
            err_output = {"error": str(e), "message": f"Execution failed in {self.name}"}
            self.latest_output = err_output
            
            await blackboard.post(
                request_id=request_id,
                agent_name=self.name,
                category=self.name.replace("_agent", ""),
                output_data=err_output,
                status="FAILED"
            )
            logger.error(f"Agent [{self.name}] encountered an error: {e}", exc_info=True)
            raise e

    def get_status_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "icon": self.icon,
            "responsibility": self.responsibility,
            "status": self.status,
            "latest_output": self.latest_output,
            "execution_time_ms": self.last_execution_ms
        }
