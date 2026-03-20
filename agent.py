from typing import Dict, Any, List
from skills.skill_registry import SkillRegistry
from skills.skill_base import SkillResult, BaseSkill
import re
import asyncio

class PerovskiteAgent:
    def __init__(self):
        self.registry = SkillRegistry()
        self.context = {}
        self.execution_history = []

    def initialize(self):
        from skills.skill_registry import register_all_skills
        print("\n" + "="*70)
        print("🔧 初始化钙钛矿逆向设计Agent")
        print("="*70)
        register_all_skills()
        print(f"\n✅ Agent初始化完成")
        print(f"📦 可用技能: {len(self.registry.list_skills())}")
        for skill_name in self.registry.list_skills():
            info = self.registry.get_skill_info(skill_name)
            print(f"   • {skill_name}: {info['description'][:50]}...")
        print("="*70 + "\n")

    def extract_formula_from_text(self, text: str) -> str:
        patterns = [
            r'([A-Z][a-z]?\d*[A-Z][a-z]?\d*[IOBrClFS]\d*)',
            r'(Cs|Rb|K|Na|Li|MA|FA)\s*([A-Z][a-z]?)\s*([IOBrClFS])\s*3',
            r'([A-Z][a-z]{1,2})\s*([A-Z][a-z]{1,2})\s*([IOBrClFS])\s*3',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                formula = match.group(0).replace(" ", "")
                if re.match(r'^[A-Z][a-z]?\d*[A-Z][a-z]?\d*[IOBrClFS]\d*$', formula):
                    return formula

        return None

    def extract_multiple_formulas(self, text: str) -> List[str]:
        pattern = r'([A-Z][a-z]?\d*[A-Z][a-z]?\d*[IOBrClFS]\d*)'
        matches = re.findall(pattern, text)
        formulas = []
        for m in matches:
            if re.match(r'^[A-Z][a-z]?\d*[A-Z][a-z]?\d*[IOBrClFS]\d*$', m):
                formulas.append(m)
        return formulas

    def plan(self, user_input: str) -> tuple[List[str], Dict]:
        skill_plan = []
        context = {"original_input": user_input, "input": user_input}

        user_lower = user_input.lower()

        formula = self.extract_formula_from_text(user_input)
        if formula:
            context["formula"] = formula

        formulas = self.extract_multiple_formulas(user_input)
        if formulas:
            context["formulas"] = formulas

        if any(k in user_lower for k in ["generate", "design", "create", "设计", "生成"]):
            if "perovskite_generator" not in skill_plan:
                skill_plan.append("perovskite_generator")

        if any(k in user_lower for k in ["tolerance", "stability", "check", "verify", "predict", "validate", "稳定性", "检查", "验证"]):
            if "tolerance_factor" not in skill_plan:
                skill_plan.append("tolerance_factor")

        if any(k in user_lower for k in ["structure", "analyze", "analysis", "lattice", "晶体", "结构"]):
            if "structure_analyzer" not in skill_plan:
                skill_plan.append("structure_analyzer")

        if any(k in user_lower for k in ["poscar", "vasp", "export", "generate file", "文件", "导出"]):
            if "poscar_generator" not in skill_plan:
                skill_plan.append("poscar_generator")

        if any(k in user_lower for k in ["batch", "multiple", "compare", "rank", "screening", "all", "批量", "多个", "比较"]):
            if "batch_processor" not in skill_plan:
                skill_plan.insert(0, "batch_processor")

        if any(k in user_lower for k in ["ask", "explain", "why", "what", "how", "为什么", "如何", "解释"]):
            if "llm_interface" not in skill_plan:
                skill_plan.append("llm_interface")

        if not skill_plan:
            skill_plan = ["perovskite_generator", "tolerance_factor"]

        return skill_plan, context

    async def execute_skill(self, skill_name: str, context: Dict) -> SkillResult:
        skill = self.registry.get_skill(skill_name)
        if not skill:
            return SkillResult(
                success=False,
                data=None,
                message=f"Skill '{skill_name}' not found"
            )

        print(f"\n{'─'*60}")
        print(f"⚙️  执行技能: {skill.metadata.name}")
        print(f"{'─'*60}")

        result = await skill.execute(context)

        skill.log_execution(context, result)

        status = "✅" if result.success else "❌"
        print(f"{status} {result.message}")

        return result

    async def run(self, user_input: str) -> Dict[str, Any]:
        self.context = {"original_input": user_input}

        print(f"\n{'='*70}")
        print(f"🎯 用户请求: {user_input}")
        print(f"{'='*70}")

        skill_plan, initial_context = self.plan(user_input)
        self.context.update(initial_context)

        print(f"\n📋 执行计划: {' → '.join(skill_plan)}")

        for skill_name in skill_plan:
            result = await self.execute_skill(skill_name, self.context)

            if not result.success:
                print(f"⚠️  技能 {skill_name} 执行失败，跳过")
                continue

            if skill_name == "tolerance_factor" and "stability_analysis" in self.context:
                self._display_stability_result(self.context)

            elif skill_name == "batch_processor" and "batch_results" in self.context:
                self._display_batch_result(self.context["batch_results"])

            elif skill_name == "poscar_generator" and "poscar_file" in self.context:
                print(f"📁 文件已保存: {self.context['poscar_file']}")

        self.execution_history.append({
            "input": user_input,
            "plan": skill_plan,
            "context": self.context.copy()
        })

        return {
            "success": True,
            "context": self.context,
            "plan_executed": skill_plan
        }

    def _display_stability_result(self, context: Dict):
        stability = context.get("stability_analysis", {})
        formula = context.get("formula", "N/A")

        print(f"\n{'='*70}")
        print(f"🔬 稳定性分析结果: {formula}")
        print(f"{'='*70}")

        if stability.get("tau"):
            tau = stability["tau"]
            status = "✅" if tau < 4.18 else "⚠️"
            print(f"\nτ容忍因子: {tau:.3f} {status}")
            if tau < 4.18:
                print("  → 预测为稳定钙钛矿")
            else:
                print("  → 可能不稳定")

        if stability.get("goldschmidt_t"):
            t = stability["goldschmidt_t"]
            status = "✅" if 0.8 <= t <= 1.0 else "⚠️"
            print(f"\nGoldschmidt t: {t:.3f} {status}")
            if 0.8 <= t <= 1.0:
                print("  → 在理想范围内")

        if stability.get("mu"):
            mu = stability["mu"]
            status = "✅" if 0.414 <= mu <= 0.732 else "⚠️"
            print(f"\n八面体μ: {mu:.3f} {status}")
            if 0.414 <= mu <= 0.732:
                print("  → 八面体几何合理")

        if stability.get("recommendations"):
            print(f"\n💡 建议:")
            for rec in stability["recommendations"]:
                print(f"   • {rec}")

        print(f"{'='*70}\n")

    def _display_batch_result(self, results: List[Dict]):
        print(f"\n{'='*70}")
        print(f"📊 批量分析结果 ({len(results)} 种材料)")
        print(f"{'='*70}")
        print(f"{'排名':<4} {'化学式':<15} {'τ':<10} {'Goldschmidt t':<15} {'状态'}")
        print("-"*70)

        for i, r in enumerate(results, 1):
            tau_str = f"{r['tau']:.3f}" if r.get("tau") else "N/A"
            t_str = f"{r['goldschmidt_t']:.3f}" if r.get("goldschmidt_t") else "N/A"
            status = "✅ 稳定" if r.get("stable") else "⚠️ 不稳定"

            print(f"{i:<4} {r['formula']:<15} {tau_str:<10} {t_str:<15} {status}")

        stable_count = sum(1 for r in results if r.get("stable"))
        print(f"\n📈 统计: {stable_count}/{len(results)} 种材料预测为稳定")
        print(f"{'='*70}\n")

    def get_available_skills(self) -> List[Dict]:
        skills = []
        for name in self.registry.list_skills():
            skills.append(self.registry.get_skill_info(name))
        return skills

    def list_history(self):
        print(f"\n{'='*70}")
        print(f"📜 执行历史 ({len(self.execution_history)} 条记录)")
        print(f"{'='*70}")

        for i, record in enumerate(self.execution_history, 1):
            print(f"\n[{i}] {record['input'][:60]}...")
            print(f"    技能: {' → '.join(record['plan'])}")

        print(f"{'='*70}\n")
