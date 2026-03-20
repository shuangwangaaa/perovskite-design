from typing import Dict, Any
from skills.skill_base import BaseSkill, SkillMetadata, SkillResult
from llm_client import LLMClient

class LLMInterfaceSkill(BaseSkill):
    def __init__(self):
        self.llm_client = LLMClient()
        super().__init__()

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="llm_interface",
            description="Direct interface to LLM for custom queries and analysis",
            keywords=["ask", "query", "analyze", "explain", "chat", "question", "llm", "gpt"],
            parameters={
                "prompt": "Custom prompt to send to LLM"
            },
            examples=[
                "Explain why CsPbI3 is stable",
                "Analyze advantages and disadvantages",
                "What factors affect perovskite stability?"
            ]
        )

    async def execute(self, context: Dict[str, Any]) -> SkillResult:
        prompt = context.get("prompt")
        system_prompt = context.get("system_prompt", "")

        if not prompt:
            return SkillResult(
                success=False,
                data=None,
                message="Need prompt"
            )

        try:
            print(f"Calling LLM...")
            response = self.llm_client.chat(prompt, system_prompt)

            self.add_to_context(context, "llm_response", response)

            return SkillResult(
                success=True,
                data={"response": response},
                message="LLM query completed"
            )

        except Exception as e:
            return SkillResult(
                success=False,
                data=None,
                message=f"LLM query failed: {str(e)}"
            )
