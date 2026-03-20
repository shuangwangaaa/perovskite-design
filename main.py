from perovskite_generator import PerovskiteGenerator
from structure_converter import StructureConverter
import sys

def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║    🧪 钙钛矿光伏器件逆向设计系统 (增强版)                          ║
║    Perovskite Photovoltaic Device Inverse Design System          ║
║    Powered by Qwen3.5-9B + LM Studio                            ║
║    ⭐ Integrated with ToleraneFactor Calculator                  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

def print_stability_analysis(result):
    if "stability" not in result:
        return

    stability = result["stability"]
    print("\n" + "="*80)
    print("🔬 ToleraneFactor 稳定性验证分析")
    print("="*80)
    print(f"化学式: {result.get('formula', 'N/A')}")
    print(f"组成: A={stability['composition']['A']}, "
          f"B={stability['composition']['B']}, "
          f"X={stability['composition']['X']}")

    if stability['tau']:
        print(f"\n【τ容忍因子】 = {stability['tau']:.3f}")
        if stability['tau'] < 4.18:
            print("  ✓ 预测为稳定钙钛矿")
            print("  注: τ < 4.18 表示可能形成稳定的钙钛矿结构")
        else:
            print("  ⚠️ τ > 4.18，可能不稳定")
            print("  注: 需要实验或DFT进一步验证")

    if stability['goldschmidt_t']:
        print(f"\n【Goldschmidt容忍因子】 t = {stability['goldschmidt_t']:.3f}")
        if 0.8 <= stability['goldschmidt_t'] <= 1.0:
            print("  ✓ 在理想范围内 (0.8-1.0)")
        else:
            print("  ⚠️ 偏离理想范围")

    if stability['mu']:
        print(f"\n【八面体因子】 μ = {stability['mu']:.3f}")
        if 0.414 <= stability['mu'] <= 0.732:
            print("  ✓ 八面体几何合理")
        else:
            print("  ⚠️ 八面体几何可能不稳定")

    if stability.get('recommendations'):
        print(f"\n【💡 建议】")
        for rec in stability['recommendations']:
            print(f"   • {rec}")

    print("="*80)

def print_menu():
    print("\n请选择功能：")
    print("  1. 🎯 根据目标属性生成材料（+稳定性验证）")
    print("  2. 💬 描述性需求生成材料（+稳定性验证）")
    print("  3. 📋 批量生成设计方案（+稳定性排名）")
    print("  4. 🔗 完整逆向设计（生成+验证+结构文件）")
    print("  5. 🧪 快速稳定性查询")
    print("  0. 🚪 退出程序")
    print()

def main():
    print_banner()

    generator = PerovskiteGenerator()

    if not generator.llm_client.check_connection():
        print("❌ 无法连接到LM Studio API")
        print("请确保：")
        print("  1. LM Studio已启动")
        print("  2. 已加载Qwen3.5-9B模型")
        print("  3. 已点击'Start Server'启动API服务器")
        sys.exit(1)

    print("✅ 成功连接到LM Studio API")
    available_models = generator.llm_client.get_available_models()
    if available_models:
        print(f"📦 可用模型: {', '.join(available_models)}")

    print_menu()

    while True:
        try:
            choice = input("请输入选项 [0-5]: ").strip()

            if choice == '0':
                print("\n👋 再见！")
                break

            elif choice == '1':
                target_properties = {}
                print("\n请输入目标属性（直接回车跳过该属性）：")

                band_gap = input("  能隙 (eV) [如: 1.5]: ").strip()
                if band_gap:
                    target_properties['band_gap'] = float(band_gap)

                stability = input("  离壳能量 (eV/atom) [如: 0.02]: ").strip()
                if stability:
                    target_properties['energy_above_hull'] = float(stability)

                absorption = input("  最大吸收系数 (cm⁻¹) [如: 500000]: ").strip()
                if absorption:
                    target_properties['absorption_max'] = float(absorption)

                constraints = input("\n其他约束条件（可选）: ").strip()

                if not target_properties:
                    print("⚠️ 请至少输入一个目标属性")
                    continue

                result = generator.generate_from_properties(target_properties, constraints)

                if result['success']:
                    print("\n" + "="*80)
                    print("📋 Qwen生成的设计方案:")
                    print("="*80)
                    print(result['design'])

                    print_stability_analysis(result)

            elif choice == '2':
                print("\n请描述您的需求（例如：我想设计一种用于室内光能收集的高稳定性钙钛矿材料）:")
                description = input().strip()

                if not description:
                    print("⚠️ 请输入描述")
                    continue

                result = generator.generate_from_description(description)

                if result['success']:
                    print("\n" + "="*80)
                    print("📋 Qwen分析结果:")
                    print("="*80)
                    print(result['design'])

                    print_stability_analysis(result)

            elif choice == '3':
                print("\n批量生成模式")
                print("请输入多个属性集，格式：属性1:值1,属性2:值2")
                print("输入空行结束输入\n")

                property_sets = []
                while True:
                    line = input("属性集: ").strip()
                    if not line:
                        break

                    props = {}
                    for pair in line.split(','):
                        if ':' in pair:
                            key, value = pair.split(':')
                            props[key.strip()] = float(value.strip())
                    if props:
                        property_sets.append(props)

                if not property_sets:
                    print("⚠️ 未输入有效的属性集")
                    continue

                results = generator.batch_generate(property_sets)

                print("\n" + "="*80)
                print("📊 批量生成结果 - 稳定性排名")
                print("="*80)

                ranked_results = []
                for i, result in enumerate(results, 1):
                    tau = result.get('stability', {}).get('tau') if 'stability' in result else None
                    ranked_results.append((tau, i, result))

                ranked_results.sort(key=lambda x: x[0] if x[0] else float('inf'))

                for rank, (tau, idx, result) in enumerate(ranked_results, 1):
                    print(f"\n排名 {rank}:")
                    print(f"  化学式: {result.get('formula', 'N/A')}")
                    print(f"  τ = {tau:.3f}" if tau else "  τ = N/A")
                    if tau:
                        if tau < 4.18:
                            print("  状态: ✓ 稳定")
                        else:
                            print("  状态: ⚠️ 可能不稳定")

            elif choice == '4':
                print("\n完整逆向设计流程")
                print("这将结合Qwen生成、稳定性验证和结构转换\n")

                description = input("请描述您的需求: ").strip()
                if not description:
                    continue

                result = generator.generate_from_description(description)

                if result['success']:
                    print("\n" + "="*80)
                    print("📋 Qwen生成的设计方案:")
                    print("="*80)
                    print(result['design'])

                    print_stability_analysis(result)

                    converter = StructureConverter()
                    formula = result.get('formula')

                    if formula:
                        summary = converter.create_structure_summary(result['design'])

                        print("\n" + "="*80)
                        print("🔬 结构信息提取:")
                        print("="*80)
                        print(f"化学式: {formula}")
                        print(f"晶格参数: {summary.get('lattice_parameters') or '未识别'}")
                        print(f"预测能隙: {summary.get('predicted_band_gap') or '未识别'} eV")

                        poscar = converter.generate_poscar(formula, summary.get('lattice_parameters'))
                        poscar_file = f"POSCAR_{formula}.txt"
                        with open(poscar_file, 'w', encoding='utf-8') as f:
                            f.write(poscar)
                        print(f"\n💾 VASP POSCAR文件已保存到: {poscar_file}")

            elif choice == '5':
                print("\n快速稳定性查询")
                print("输入钙钛矿化学式（如: CsPbI3）进行稳定性预测\n")

                while True:
                    formula = input("化学式 (或 'q' 返回): ").strip()

                    if formula.lower() in ['q', 'quit', 'exit']:
                        break

                    if not formula:
                        continue

                    stability = generator.tolerance_calc.predict_stability(formula)

                    print(f"\n{'='*60}")
                    print(f"材料: {stability['formula']}")
                    print(f"组成: A={stability['composition']['A']}, "
                          f"B={stability['composition']['B']}, "
                          f"X={stability['composition']['X']}")

                    if stability['tau']:
                        print(f"\nτ = {stability['tau']:.3f}")
                        if stability['tau'] < 4.18:
                            print("  ✓ 预测为稳定钙钛矿")
                        else:
                            print("  ⚠️ 可能不稳定")

                    if stability['goldschmidt_t']:
                        print(f"\nGoldschmidt t = {stability['goldschmidt_t']:.3f}")
                        if 0.8 <= stability['goldschmidt_t'] <= 1.0:
                            print("  ✓ 理想范围")

                    if stability['mu']:
                        print(f"\nμ = {stability['mu']:.3f}")
                        if 0.414 <= stability['mu'] <= 0.732:
                            print("  ✓ 八面体几何合理")

                    print()

            else:
                print("⚠️ 无效选项，请输入 0-5")
                print_menu()

        except KeyboardInterrupt:
            print("\n\n👋 已退出")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")

if __name__ == "__main__":
    main()
