from typing import Dict, List, Type
from skills.skill_base import BaseSkill, SkillMetadata

class SkillRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._skills = {}
            cls._instance._initialized = False
        return cls._instance

    def register(self, skill_class: Type[BaseSkill]):
        skill = skill_class()
        self._skills[skill.metadata.name] = skill
        print(f"[OK] Registered skill: {skill.metadata.name}")

    def get_skill(self, name: str) -> BaseSkill:
        return self._skills.get(name)

    def get_all_skills(self) -> Dict[str, BaseSkill]:
        return self._skills.copy()

    def find_skills(self, query: str) -> List[BaseSkill]:
        scored_skills = []

        for skill in self._skills.values():
            score = skill.metadata.match_score(query)
            if score > 0:
                scored_skills.append((score, skill))

        scored_skills.sort(key=lambda x: x[0], reverse=True)
        return [skill for _, skill in scored_skills]

    def list_skills(self) -> List[str]:
        return list(self._skills.keys())

    def get_skill_info(self, name: str) -> Dict:
        skill = self._skills.get(name)
        if not skill:
            return {}

        return {
            "name": skill.metadata.name,
            "description": skill.metadata.description,
            "keywords": skill.metadata.keywords,
            "parameters": skill.metadata.parameters,
            "examples": skill.metadata.examples,
            "execution_count": len(skill.execution_history)
        }

def register_all_skills():
    from skills.perovskite_generator_skill import PerovskiteGeneratorSkill
    from skills.tolerance_factor_skill import ToleranceFactorSkill
    from skills.structure_analyzer_skill import StructureAnalyzerSkill
    from skills.poscar_generator_skill import POSCARGGeneratorSkill
    from skills.batch_processor_skill import BatchProcessorSkill
    from skills.llm_interface_skill import LLMInterfaceSkill

    registry = SkillRegistry()

    skills_to_register = [
        PerovskiteGeneratorSkill,
        ToleranceFactorSkill,
        StructureAnalyzerSkill,
        POSCARGGeneratorSkill,
        BatchProcessorSkill,
        LLMInterfaceSkill,
    ]

    for skill_class in skills_to_register:
        registry.register(skill_class)

    registry._initialized = True
    return registry
