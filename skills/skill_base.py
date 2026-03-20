from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SkillResult:
    success: bool
    data: Any
    message: str = ""
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class SkillMetadata:
    name: str
    description: str
    keywords: List[str]
    parameters: Dict[str, str]
    examples: List[str]

    def match_score(self, query: str) -> float:
        query_lower = query.lower()
        score = 0.0

        for keyword in self.keywords:
            if keyword.lower() in query_lower:
                score += 1.0

        if any(word in query_lower for word in self.description.lower().split()):
            score += 0.5

        return score

class BaseSkill(ABC):
    def __init__(self):
        self.metadata = self.get_metadata()
        self.execution_history = []

    @abstractmethod
    def get_metadata(self) -> SkillMetadata:
        pass

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> SkillResult:
        pass

    def log_execution(self, context: Dict, result: SkillResult):
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "result": result.success,
            "message": result.message
        })

    def validate_input(self, context: Dict[str, Any], required_keys: List[str]) -> tuple[bool, str]:
        for key in required_keys:
            if key not in context:
                return False, f"Missing required parameter: {key}"
        return True, ""

    def add_to_context(self, context: Dict, key: str, value: Any):
        context[key] = value
        if "skill_outputs" not in context:
            context["skill_outputs"] = {}
        context["skill_outputs"][self.metadata.name] = value
