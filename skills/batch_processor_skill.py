from typing import Dict, Any, List
from skills.skill_base import BaseSkill, SkillMetadata, SkillResult
from tolerance_factor import ToleranceFactorCalculator

class BatchProcessorSkill(BaseSkill):
    def __init__(self):
        self.calculator = ToleranceFactorCalculator()
        super().__init__()

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="batch_processor",
            description="Process multiple materials for comparison and ranking based on stability",
            keywords=["batch", "multiple", "compare", "rank", "list", "all", "screening"],
            parameters={
                "formulas": "List of chemical formulas"
            },
            examples=[
                "Batch analyze: CsPbI3, CsPbBr3, MAPbI3",
                "Compare multiple materials",
                "Screen stable materials"
            ]
        )

    async def execute(self, context: Dict[str, Any]) -> SkillResult:
        formulas = context.get("formulas", [])

        if not formulas:
            design_text = context.get("generated_design", "")
            formulas = self._extract_multiple_formulas(design_text)

        if not formulas:
            return SkillResult(
                success=False,
                data=None,
                message="No materials found"
            )

        try:
            results = []
            for formula in formulas:
                stability = self.calculator.predict_stability(formula)
                results.append({
                    "formula": formula,
                    "tau": stability.get("tau"),
                    "goldschmidt_t": stability.get("goldschmidt_t"),
                    "mu": stability.get("mu"),
                    "stable": stability.get("tau", 999) < 4.18 if stability.get("tau") else False
                })

            results.sort(key=lambda x: x["tau"] if x["tau"] else 999)

            self.add_to_context(context, "batch_results", results)

            return SkillResult(
                success=True,
                data={
                    "results": results,
                    "total": len(results),
                    "stable_count": sum(1 for r in results if r["stable"])
                },
                message=f"Batch analysis completed: {len(results)} materials processed"
            )

        except Exception as e:
            return SkillResult(
                success=False,
                data=None,
                message=f"Batch processing failed: {str(e)}"
            )

    def _extract_multiple_formulas(self, text: str) -> List[str]:
        import re

        patterns = [
            r'([A-Z][a-z]?\d*[A-Z][a-z]?\d*[IOBrClFS]\d*)',
        ]

        formulas = set()
        for pattern in patterns:
            matches = re.findall(pattern, text)
            formulas.update(matches)

        return list(formulas)
