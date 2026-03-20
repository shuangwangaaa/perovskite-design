import asyncio
import sys
from agent import PerovskiteAgent
from design_workflow import DesignWorkflow

def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   🧪 钙钛矿逆向设计系统 (多模式)                                     ║
║   Perovskite Inverse Design System                                   ║
║   Powered by Qwen3.5-9B + Multi-Skill System                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)

def print_help():
    print("""
📖 Agent命令帮助:
═══════════════════════════════════════════════════════════════════════

🎯 设计模式1 - 交互式设计（推荐）:
   输入: "开始设计" 或 "design"
   → Agent会逐步询问您的需求
   → 自动迭代优化直到通过验证

🎯 设计模式2 - 快速查询:
   "检查CsPbI3的稳定性"
   "批量分析CsPbI3, CsPbBr3, MAPbI3"

🎯 设计模式3 - 自然语言设计:
   "设计一个1.6eV能隙的钙钛矿材料"
   "推荐高稳定性的无铅材料"

═══════════════════════════════════════════════════════════════════════

📋 系统命令:
   /help     - 显示此帮助
   /skills   - 列出所有可用技能
   /design   - 启动交互式设计工作流
   /history  - 显示执行历史
   /clear    - 清除历史
   /quit     - 退出程序
""")

async def run_interactive_design():
    print("\n" + "="*70)
    print("🚀 启动交互式设计工作流")
    print("="*70)

    workflow = DesignWorkflow()
    await workflow.start_interactive_design()

async def main():
    print_banner()
    print_help()

    agent = PerovskiteAgent()
    agent.initialize()

    while True:
        try:
            user_input = input("\n🎯 您: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['/quit', '/exit', 'q']:
                print("\n👋 再见！感谢使用钙钛矿逆向设计系统！")
                break

            elif user_input.lower() in ['/help', '/h', '?']:
                print_help()
                continue

            elif user_input.lower() in ['/skills', '/list']:
                print("\n📦 可用技能:")
                for skill in agent.get_available_skills():
                    print(f"\n  [{skill['name']}]")
                    print(f"    描述: {skill['description']}")
                    print(f"    关键词: {', '.join(skill['keywords'])}")
                print()
                continue

            elif user_input.lower() in ['/history', '/hist']:
                agent.list_history()
                continue

            elif user_input.lower() in ['/clear', '/cls']:
                agent.execution_history.clear()
                print("✅ 历史已清除\n")
                continue

            elif user_input.lower() in ['/design', '开始设计', 'start design']:
                await run_interactive_design()
                continue

            if user_input.startswith('/'):
                print(f"⚠️  未知命令: {user_input}")
                print("   输入 /help 查看可用命令\n")
                continue

            is_design_intent = any(k in user_input.lower() for k in [
                '设计', 'generate', 'design', 'create', '推荐', '推荐'
            ])

            if is_design_intent and len(user_input) < 50:
                print("\n💡 检测到设计意图，启动交互式设计工作流...")
                await run_interactive_design()
            else:
                result = await agent.run(user_input)

                if result["success"]:
                    print("\n" + "="*70)
                    print("✅ Agent处理完成！")
                    print("="*70)

        except KeyboardInterrupt:
            print("\n\n👋 已退出")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
