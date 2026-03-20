from typing import Dict, Any
from skills.skill_base import BaseSkill, SkillMetadata, SkillResult
from structure_converter import StructureConverter

class POSCARGGeneratorSkill(BaseSkill):
    def __init__(self):
        self.converter = StructureConverter()
        super().__init__()

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="poscar_generator",
            description="Generate VASP POSCAR file for crystal structure visualization",
            keywords=["poscar", "vasp", "cif", "structure file", "crystal", "visualization", "export"],
            parameters={
                "formula": "Chemical formula",
                "lattice": "Lattice parameters (optional)"
            },
            examples=[
                "Generate POSCAR file for CsPbI3",
                "Create VASP structure file",
                "Export crystal structure file"
            ]
        )

    async def execute(self, context: Dict[str, Any]) -> SkillResult:
        formula = context.get("formula")
        lattice = context.get("lattice_parameters")

        if not formula:
            return SkillResult(
                success=False,
                data=None,
                message="Need formula"
            )

        try:
            poscar_content = self.converter.generate_poscar(formula, lattice)

            filename = f"POSCAR_{formula}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(poscar_content)

            self.add_to_context(context, "poscar_file", filename)
            self.add_to_context(context, "poscar_content", poscar_content)

            return SkillResult(
                success=True,
                data={
                    "filename": filename,
                    "content": poscar_content,
                    "saved_path": filename
                },
                message=f"POSCAR file generated: {filename}"
            )

        except Exception as e:
            return SkillResult(
                success=False,
                data=None,
                message=f"POSCAR generation failed: {str(e)}"
            )
