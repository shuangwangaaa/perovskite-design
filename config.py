API_BASE_URL = "http://localhost:1234/v1"
MODEL_NAME = "qwen/qwen3.5-9b"
TEMPERATURE = 0.7
MAX_TOKENS = 2000

PEROVSKITE_TEMPLATES = {
    "ABX3": {
        "description": "经典钙钛矿结构",
        "A": ["Ca", "Sr", "Ba", "Pb", "Cs", "MA", "FA"],
        "B": ["Ti", "Zr", "Hf", "Sn", "Pb", "Si"],
        "X": ["O", "S", "Se", "Cl", "Br", "I"]
    }
}

PROPERTY_RANGES = {
    "band_gap": {"min": 0.5, "max": 3.5, "unit": "eV", "description": "能隙"},
    "energy_above_hull": {"min": 0, "max": 0.2, "unit": "eV/atom", "description": "热力学稳定性"},
    "absorption_max": {"min": 1e5, "max": 1e6, "unit": "cm⁻¹", "description": "最大吸收系数"},
    "absorption_mean": {"min": 1e4, "max": 5e5, "unit": "cm⁻¹", "description": "平均吸收系数"}
}

SYSTEM_PROMPT = """你是一位专业的钙钛矿光伏材料科学家。你擅长根据目标物理化学属性设计新型钙钛矿材料。

请根据用户提供的目标属性，生成符合要求的钙钛矿材料设计方案。

输出格式要求：
1. 给出完整的化学式（如：CsPbI3, MAPbBr3等）
2. 解释为什么这个材料能满足目标属性
3. 提供关键的晶体结构参数估算
4. 讨论材料合成的可行性

注意：
- 钙钛矿通式为ABX3，其中A位通常为大半径阳离子（如Cs⁺, MA⁺, FA⁺）
- B位为小半径阳离子（如Pb²⁺, Sn²⁺, Ti⁴⁺）
- X位为卤素离子（如I⁻, Br⁻, Cl⁻）或氧离子（O²⁻）
"""
