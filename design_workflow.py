import asyncio
from typing import Dict, Any, List, Optional
from tolerance_factor import ToleranceFactorCalculator
from structure_converter import StructureConverter

class DesignWorkflow:
    def __init__(self):
        self.calculator = ToleranceFactorCalculator()
        self.converter = StructureConverter()
        self.max_iterations = 5
        self.target_stability_threshold = 4.18

    async def start_interactive_design(self):
        print("\n" + "="*70)
        print("🎯 交互式钙钛矿设计工作流")
        print("="*70)
        print("我将帮您设计满足特定需求的钙钛矿材料")
        print("请告诉我您的需求，我会逐步引导您完成设计\n")

        requirements = await self._collect_requirements()

        if not requirements:
            print("未收集到有效需求，退出设计流程")
            return None

        return await self._design_loop(requirements)

    async def _collect_requirements(self) -> Dict[str, Any]:
        requirements = {}

        print("\n" + "-"*70)
        print("📋 需求收集")
        print("-"*70)

        print("\n请输入您的需求（直接回车使用默认值，按'q'退出）：\n")

        band_gap = input("1. 能隙目标 (eV) [默认: 无指定, 范围0.5-4.0]: ").strip()
        if band_gap.lower() == 'q':
            return {}
        if band_gap:
            try:
                val = float(band_gap)
                if 0.5 <= val <= 4.0:
                    requirements['band_gap'] = val
                    print(f"   ✓ 能隙设置为: {val} eV")
                else:
                    print("   ⚠️ 能隙超出范围，使用默认值")
            except ValueError:
                print("   ⚠️ 无效输入，使用默认值")

        stability_priority = input("2. 稳定性优先级 (高/中/低) [默认: 高]: ").strip()
        if stability_priority.lower() == 'q':
            return {}
        if stability_priority in ['高', '中', '低']:
            requirements['stability_priority'] = stability_priority
            print(f"   ✓ 稳定性优先级: {stability_priority}")
        elif stability_priority.lower() in ['h', 'm', 'l']:
            priorities = {'h': '高', 'm': '中', 'l': '低'}
            requirements['stability_priority'] = priorities[stability_priority.lower()]
            print(f"   ✓ 稳定性优先级: {requirements['stability_priority']}")

        application = input("3. 应用场景 [太阳能电池/LED/光电探测器] [默认: 太阳能电池]: ").strip()
        if application.lower() == 'q':
            return {}
        if application:
            requirements['application'] = application
            print(f"   ✓ 应用场景: {application}")
        else:
            requirements['application'] = '太阳能电池'
            print(f"   ✓ 应用场景: 太阳能电池")

        lead_free = input("4. 是否需要无铅材料 (y/n) [默认: n]: ").strip()
        if lead_free.lower() == 'q':
            return {}
        if lead_free.lower() == 'y':
            requirements['lead_free'] = True
            print("   ✓ 无铅材料")
        else:
            requirements['lead_free'] = False

        print("\n" + "-"*70)
        print("📊 需求汇总:")
        print("-"*70)
        if 'band_gap' in requirements:
            print(f"  • 能隙目标: {requirements['band_gap']} eV")
        print(f"  • 稳定性优先级: {requirements.get('stability_priority', '高')}")
        print(f"  • 应用场景: {requirements.get('application', '太阳能电池')}")
        print(f"  • 无铅材料: {'是' if requirements.get('lead_free') else '否'}")
        print("-"*70)

        confirm = input("\n确认以上需求？(y/n) [默认: y]: ").strip()
        if confirm.lower() == 'n':
            print("请重新输入需求...")
            return await self._collect_requirements()

        return requirements

    async def _design_loop(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        print("\n" + "="*70)
        print("🔄 开始迭代设计")
        print("="*70)

        for iteration in range(1, self.max_iterations + 1):
            print(f"\n{'='*70}")
            print(f"📐 第 {iteration} 次迭代")
            print(f"{'='*70}")

            design = await self._generate_design(requirements, iteration)

            if not design:
                print("生成失败")
                continue

            print("\n" + "-"*70)
            print("📋 生成的材料设计:")
            print("-"*70)
            print(design['design_text'][:500] if len(design['design_text']) > 500 else design['design_text'])

            formula = self._extract_formula(design['design_text'])
            if not formula:
                print("\n⚠️ 无法提取化学式，跳过验证")
                continue

            print(f"\n🔬 提取的化学式: {formula}")
            print("⏳ 正在验证稳定性...")

            stability = self.calculator.predict_stability(formula)

            print("\n" + "="*70)
            print("📊 稳定性验证结果")
            print("="*70)
            print(f"化学式: {formula}")
            print(f"A位: {stability['composition']['A']}, B位: {stability['composition']['B']}, X位: {stability['composition']['X']}")

            passed = True
            issues = []

            if stability['tau']:
                print(f"\nτ容忍因子: {stability['tau']:.3f}")
                if stability['tau'] < self.target_stability_threshold:
                    print("  ✅ τ < 4.18 - 预测为稳定钙钛矿")
                else:
                    print("  ❌ τ > 4.18 - 可能不稳定")
                    passed = False
                    issues.append(f"τ值过高 ({stability['tau']:.3f})")
            else:
                issues.append("无法计算τ")

            if stability['goldschmidt_t']:
                print(f"\nGoldschmidt t: {stability['goldschmidt_t']:.3f}")
                if 0.8 <= stability['goldschmidt_t'] <= 1.0:
                    print("  ✅ 在理想范围内 (0.8-1.0)")
                else:
                    print("  ⚠️ 偏离理想范围")
                    issues.append(f"Goldschmidt t偏离理想值 ({stability['goldschmidt_t']:.3f})")

            if stability['mu']:
                print(f"\n八面体μ: {stability['mu']:.3f}")
                if 0.414 <= stability['mu'] <= 0.732:
                    print("  ✅ 八面体几何合理")
                else:
                    print("  ⚠️ 八面体几何可能不稳定")
                    issues.append(f"八面体μ不合理 ({stability['mu']:.3f})")

            design['stability'] = stability
            design['formula'] = formula

            if passed:
                print("\n" + "="*70)
                print("🎉 设计验证通过！")
                print("="*70)
                self._print_final_result(design, requirements)
                return design
            else:
                print("\n" + "="*70)
                print("⚠️ 设计未通过验证")
                print("="*70)
                print("问题:")
                for issue in issues:
                    print(f"  • {issue}")

                if iteration < self.max_iterations:
                    print(f"\n🔄 将根据反馈重新设计... (剩余 {self.max_iterations - iteration} 次机会)")
                    requirements['feedback'] = "; ".join(issues)
                    requirements['previous_design'] = design['design_text']
                else:
                    print("\n❌ 已达到最大迭代次数，设计未能通过验证")

        return None

    async def _generate_design(self, requirements: Dict, iteration: int) -> Dict[str, Any]:
        from llm_client import LLMClient
        from config import SYSTEM_PROMPT

        llm = LLMClient()

        prompt_parts = []

        if iteration == 1:
            prompt_parts.append("请设计一种钙钛矿材料，满足以下要求：")
        else:
            prompt_parts.append(f"请重新设计一种钙钛矿材料。上一次设计存在问题: {requirements.get('feedback', '需要优化')}")
            prompt_parts.append("\n请生成一个新的设计方案。")

        if 'band_gap' in requirements:
            prompt_parts.append(f"\n- 能隙目标: {requirements['band_gap']} eV")

        prompt_parts.append(f"- 应用场景: {requirements.get('application', '太阳能电池')}")

        if requirements.get('lead_free'):
            prompt_parts.append("- 必须是无铅材料（不含Pb）")

        stability_priority = requirements.get('stability_priority', '高')
        if stability_priority == '高':
            prompt_parts.append("- 必须具有高稳定性")

        prompt_parts.append("\n请提供：")
        prompt_parts.append("1. 化学式")
        prompt_parts.append("2. 设计理由")
        prompt_parts.append("3. 预测的物理化学性质")
        prompt_parts.append("4. 稳定性分析")

        prompt = "\n".join(prompt_parts)

        try:
            design_text = llm.chat(prompt, SYSTEM_PROMPT)
            return {"design_text": design_text}
        except Exception as e:
            print(f"❌ LLM调用失败: {e}")
            return {}

    def _extract_formula(self, text: str) -> Optional[str]:
        import re

        patterns = [
            r'([A-Z][a-z]?\d*[A-Z][a-z]?\d*[IOBrClFS]\d*)',
            r'([A-Z][a-z]{1,2})\s*([A-Z][a-z]{1,2})\s*([IOBrClFS])\s*3',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                formula = match.group(0).replace(" ", "")
                if re.match(r'^[A-Z][a-z]?\d*[A-Z][a-z]?\d*[IOBrClFS]\d*$', formula):
                    return formula

        return None

    def _print_final_result(self, design: Dict, requirements: Dict):
        print("\n" + "="*70)
        print("✅ 最终设计方案")
        print("="*70)

        print(f"\n📝 化学式: {design['formula']}")

        stability = design['stability']
        print(f"\n📊 稳定性指标:")
        if stability['tau']:
            print(f"   • τ容忍因子: {stability['tau']:.3f} < 4.18 ✅")
        if stability['goldschmidt_t']:
            print(f"   • Goldschmidt t: {stability['goldschmidt_t']:.3f}")
        if stability['mu']:
            print(f"   • 八面体μ: {stability['mu']:.3f}")

        print(f"\n📋 设计方案:")
        print(design['design_text'][:800])

        generate_poscar = input("\n是否生成VASP POSCAR文件？(y/n) [默认: y]: ").strip()
        if generate_poscar.lower() != 'n':
            poscar = self.converter.generate_poscar(design['formula'])
            filename = f"POSCAR_{design['formula']}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(poscar)
            print(f"✅ POSCAR文件已保存: {filename}")

        save_design = input("\n是否保存完整设计方案？(y/n) [默认: y]: ").strip()
        if save_design.lower() != 'n':
            filename = f"design_{design['formula']}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"钙钛矿逆向设计方案\n")
                f.write(f"{'='*50}\n\n")
                f.write(f"化学式: {design['formula']}\n")
                f.write(f"\n稳定性指标:\n")
                f.write(f"  τ = {design['stability'].get('tau', 'N/A')}\n")
                f.write(f"  Goldschmidt t = {design['stability'].get('goldschmidt_t', 'N/A')}\n")
                f.write(f"  μ = {design['stability'].get('mu', 'N/A')}\n")
                f.write(f"\n完整设计方案:\n")
                f.write(design['design_text'])
            print(f"✅ 设计方案已保存: {filename}")

        print("\n" + "="*70)


async def interactive_main():
    workflow = DesignWorkflow()
    result = await workflow.start_interactive_design()

    if result:
        print("\n🎉 设计完成！")
    else:
        print("\n👋 再见！")


if __name__ == "__main__":
    asyncio.run(interactive_main())
