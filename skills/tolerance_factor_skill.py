from typing import Dict, Any
from skills.skill_base import BaseSkill, SkillMetadata, SkillResult
from tolerance_factor import ToleranceFactorCalculator

class ToleranceFactorSkill(BaseSkill):
    def __init__(self):
        self.calculator = ToleranceFactorCalculator()
        super().__init__()

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="tolerance_factor",
            description="Calculate tolerance factor (tau, Goldschmidt t, octahedral mu) to predict perovskite stability",
            keywords=["tolerance", "stability", "tau", "goldschmidt", "predict", "validate", "verify", "check"],
            parameters={
                "formula": "Chemical formula string (e.g., CsPbI3)"
            },
            examples=[
                "Calculate tolerance factor for CsPbI3",
                "Check stability of MAPbI3",
                "Verify material stability"
            ]
        )

    async def execute(self, context: Dict[str, Any]) -> SkillResult:
        formula = context.get("formula")
        design_text = context.get("generated_design")

        if not formula and not design_text:
            return SkillResult(
                success=False,
                data=None,
                message="Need formula or design text"
            )

        try:
            if formula:
                result = self.calculator.predict_stability(formula)
            elif design_text:
                formula = self._extract_formula(design_text)
                if formula:
                    result = self.calculator.predict_stability(formula)
                else:
                    return SkillResult(
                        success=False,
                        data=None,
                        message="Cannot extract formula from design"
                    )

            self.add_to_context(context, "stability_analysis", result)
            self.add_to_context(context, "formula", formula)

            return SkillResult(
                success=True,
                data={
                    "formula": formula,
                    "stability": result,
                    "tau": result.get("tau"),
                    "goldschmidt_t": result.get("goldschmidt_t"),
                    "mu": result.get("mu")
                },
                message=f"Stability analysis completed for {formula}"
            )

        except Exception as e:
            return SkillResult(
                success=False,
                data=None,
                message=f"Analysis failed: {str(e)}"
            )

    def _extract_formula(self, text: str) -> str:
        import re

        patterns = [
            r'([A-Z][a-z]?\d*[A-Z][a-z]?\d*[IOBrClFS]\d*)',
            r'(Cs|Rb|K|Na|Li|MA|FA)\s*([A-Z][a-z]?)\s*([IOBrClFS])\s*3',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).replace(" ", "")

        return None
