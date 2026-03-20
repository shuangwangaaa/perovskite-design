from typing import Dict, Any
from skills.skill_base import BaseSkill, SkillMetadata, SkillResult
from llm_client import LLMClient
import config

class PerovskiteGeneratorSkill(BaseSkill):
    def __init__(self):
        self.llm_client = LLMClient()
        super().__init__()

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="perovskite_generator",
            description="Generate perovskite material designs based on target properties or descriptions",
            keywords=["generate", "design", "create", "material", "perovskite", "propose", "recommend"],
            parameters={
                "input_type": "description or properties dict",
                "mode": "description or properties"
            },
            examples=[
                "Design a perovskite for solar cells with 1.6 eV bandgap",
                "Generate a material with bandgap 1.6 eV",
                "Create a stable perovskite for indoor applications"
            ]
        )

    async def execute(self, context: Dict[str, Any]) -> SkillResult:
        required_keys = ["input"]
        valid, msg = self.validate_input(context, required_keys)
        if not valid:
            return SkillResult(success=False, data=None, message=msg)

        user_input = context["input"]
        mode = context.get("mode", "description")

        try:
            if mode == "properties":
                properties_text = self._format_properties(user_input)
                prompt = f"""Design a perovskite material meeting the following target properties:

Target Properties:
{properties_text}

Please provide a detailed design proposal including chemical formula and stability analysis."""
            else:
                prompt = f"""User Requirement: {user_input}

As a perovskite materials scientist, design a material meeting the requirement. Provide chemical formula and stability analysis."""

            print(f"Calling Qwen model...")
            design = self.llm_client.chat(prompt, config.SYSTEM_PROMPT)

            self.add_to_context(context, "generated_design", design)

            return SkillResult(
                success=True,
                data={"design": design},
                message="Successfully generated perovskite design"
            )

        except Exception as e:
            return SkillResult(success=False, data=None, message=f"Generation failed: {str(e)}")

    def _format_properties(self, properties: Dict) -> str:
        lines = []
        for key, value in properties.items():
            if key in config.PROPERTY_RANGES:
                info = config.PROPERTY_RANGES[key]
                lines.append(f"- {info['description']} ({key}): {value} {info['unit']}")
            else:
                lines.append(f"- {key}: {value}")
        return "\n".join(lines)
