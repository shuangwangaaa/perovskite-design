from typing import Dict, Any
from skills.skill_base import BaseSkill, SkillMetadata, SkillResult
from structure_converter import StructureConverter

class StructureAnalyzerSkill(BaseSkill):
    def __init__(self):
        self.converter = StructureConverter()
        super().__init__()

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="structure_analyzer",
            description="Analyze perovskite crystal structure, extract formula, lattice parameters, and band gap from text",
            keywords=["analyze", "structure", "crystal", "extract", "lattice", "parameters", "bandgap"],
            parameters={
                "input": "Design text or formula"
            },
            examples=[
                "Analyze crystal structure of CsPbI3",
                "Extract structure information",
                "Get lattice parameters"
            ]
        )

    async def execute(self, context: Dict[str, Any]) -> SkillResult:
        design_text = context.get("generated_design")
        formula = context.get("formula")

        if not design_text and not formula:
            return SkillResult(
                success=False,
                data=None,
                message="Need design text or formula"
            )

        try:
            summary = {'formula': formula}
            lattice = None

            if design_text:
                summary = self.converter.create_structure_summary(design_text)
                lattice = self.converter.extract_lattice_parameters(design_text)

                if formula:
                    summary['formula'] = formula
                elif summary.get('formula'):
                    formula = summary['formula']

            if formula:
                self.add_to_context(context, "formula", formula)
                self.add_to_context(context, "lattice_parameters", lattice)

            self.add_to_context(context, "structure_info", summary)

            return SkillResult(
                success=True,
                data={
                    "formula": summary.get('formula'),
                    "lattice_parameters": lattice or summary.get('lattice_parameters'),
                    "band_gap": summary.get('predicted_band_gap'),
                    "stability": summary.get('stability'),
                    "applications": summary.get('applications', [])
                },
                message="Structure analysis completed"
            )

        except Exception as e:
            return SkillResult(
                success=False,
                data=None,
                message=f"Analysis failed: {str(e)}"
            )
