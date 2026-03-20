from llm_client import LLMClient
from tolerance_factor import ToleranceFactorCalculator
from structure_converter import StructureConverter
from typing import Dict, Optional
import config

class PerovskiteGenerator:
    def __init__(self):
        self.llm_client = LLMClient()
        self.tolerance_calc = ToleranceFactorCalculator()
        self.structure_converter = StructureConverter()
        self.system_prompt = config.SYSTEM_PROMPT

    def validate_properties(self, properties: Dict) -> tuple[bool, str]:
        for key, value in properties.items():
            if key in config.PROPERTY_RANGES:
                range_info = config.PROPERTY_RANGES[key]
                if not (range_info["min"] <= value <= range_info["max"]):
                    return False, f"{key} 的值 {value} {range_info['unit']} 不在合理范围内 [{range_info['min']}, {range_info['max']}]"
        return True, "属性验证通过"

    def generate_from_properties(self, target_properties: Dict,
                                  additional_constraints: str = "") -> Dict:
        is_valid, msg = self.validate_properties(target_properties)
        if not is_valid:
            return {"success": False, "error": msg}

        properties_text = self._format_properties(target_properties)
        user_prompt = f"""请设计一种满足以下目标属性的钙钛矿材料：

目标属性：
{properties_text}

{additional_constraints}

请给出详细的设计方案，包括化学式、晶体结构参数和稳定性分析。"""

        print("正在调用Qwen模型生成设计方案...")
        result = self.llm_client.chat(user_prompt, self.system_prompt)

        design_result = {
            "success": True,
            "properties": target_properties,
            "design": result,
            "constraints": additional_constraints
        }

        formula = self.structure_converter.extract_formula(result)
        if formula:
            stability = self.tolerance_calc.predict_stability(formula)
            design_result["stability"] = stability
            design_result["formula"] = formula

        return design_result

    def generate_from_description(self, description: str) -> Dict:
        user_prompt = f"""用户需求描述：{description}

请作为专业的钙钛矿材料科学家，分析这个需求并设计满足要求的钙钛矿材料。
请给出：
1. 推荐的材料化学式
2. 关键物理化学属性预测
3. 设计理由
4. 稳定性分析
5. 合成建议"""

        print("正在分析需求并设计方案...")
        result = self.llm_client.chat(user_prompt, self.system_prompt)

        design_result = {
            "success": True,
            "description": description,
            "design": result
        }

        formula = self.structure_converter.extract_formula(result)
        if formula:
            stability = self.tolerance_calc.predict_stability(formula)
            design_result["stability"] = stability
            design_result["formula"] = formula

        return design_result

    def batch_generate(self, property_sets: list) -> list:
        results = []
        for i, props in enumerate(property_sets, 1):
            print(f"\n{'='*60}")
            print(f"生成方案 {i}/{len(property_sets)}")
            result = self.generate_from_properties(props)
            results.append(result)

            if "stability" in result:
                stability = result["stability"]
                tau = stability.get("tau")
                if tau:
                    print(f"\n🔬 稳定性分析:")
                    print(f"   化学式: {result.get('formula', 'N/A')}")
                    print(f"   τ = {tau:.3f}")
                    print(f"   Goldschmidt t = {stability.get('goldschmidt_t', 'N/A')}")

        return results

    def interactive_mode(self):
        print("\n" + "="*80)
        print("🧪 钙钛矿光伏器件逆向设计系统 (增强版)")
        print("="*80)
        print("\n功能：")
        print("  ✓ Qwen智能生成材料设计")
        print("  ✓ ⭐ ToleraneFactor容忍因子验证")
        print("  ✓ Goldschmidt容忍因子交叉验证")
        print("  ✓ 八面体因子μ分析")
        print()

        while True:
            try:
                user_input = input(">>> 请输入您的需求（或'quit'退出）: ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n感谢使用！再见 👋")
                    break

                if not user_input:
                    continue

                if any(keyword in user_input for keyword in ['能隙', 'band_gap', '吸收', '稳定性', '光伏', '太阳能']):
                    result = self.generate_from_description(user_input)
                else:
                    result = self.generate_from_description(user_input)

                print("\n" + "-"*80)
                print("📋 Qwen生成的设计方案:")
                print("-"*80)
                print(result['design'])

                if "stability" in result:
                    stability = result["stability"]
                    print("\n" + "="*80)
                    print("🔬 容忍因子稳定性验证")
                    print("="*80)
                    print(f"化学式: {result.get('formula', 'N/A')}")
                    print(f"组成: A={stability['composition']['A']}, "
                          f"B={stability['composition']['B']}, "
                          f"X={stability['composition']['X']}")

                    if stability['tau']:
                        print(f"\nτ容忍因子 = {stability['tau']:.3f}")
                        if stability['tau'] < 4.18:
                            print("  ✓ 预测为稳定钙钛矿")
                        else:
                            print("  ⚠️ τ > 4.18，可能不稳定")

                    if stability['goldschmidt_t']:
                        print(f"\nGoldschmidt容忍因子 t = {stability['goldschmidt_t']:.3f}")
                        if 0.8 <= stability['goldschmidt_t'] <= 1.0:
                            print("  ✓ 在理想范围内 (0.8-1.0)")
                        else:
                            print("  ⚠️ 偏离理想范围")

                    if stability['mu']:
                        print(f"\n八面体因子 μ = {stability['mu']:.3f}")
                        if 0.414 <= stability['mu'] <= 0.732:
                            print("  ✓ 八面体几何合理")
                        else:
                            print("  ⚠️ 八面体几何可能不稳定")

                    print("\n💡 建议:")
                    for rec in stability.get('recommendations', []):
                        print(f"   • {rec}")

                    print("="*80)

            except KeyboardInterrupt:
                print("\n\n已退出")
                break
            except Exception as e:
                print(f"\n错误: {e}")

    def _format_properties(self, properties: Dict) -> str:
        lines = []
        for key, value in properties.items():
            if key in config.PROPERTY_RANGES:
                info = config.PROPERTY_RANGES[key]
                lines.append(f"- {info['description']} ({key}): {value} {info['unit']}")
            else:
                lines.append(f"- {key}: {value}")
        return "\n".join(lines)
