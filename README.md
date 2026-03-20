# 钙钛矿光伏器件逆向设计系统

基于 **Qwen3.5-9B** + **LM Studio** + **ML扩展Shannon离子半径** 的智能钙钛矿材料设计工具

## 📋 系统概述

本系统集成了大语言模型和材料科学领域的容忍因子理论，实现了从自然语言描述或目标属性出发，智能生成并验证钙钛矿材料设计方案的完整流程。

### 核心功能

- 🧠 **Qwen智能生成**：利用本地部署的Qwen3.5-9B大语言模型生成材料设计方案
- 🔬 **容忍因子验证**：基于机器学习扩展的Shannon离子半径数据预测材料稳定性
- 📊 **多维度评估**：综合Goldschmidt容忍因子、八面体因子等进行多角度分析
- 🎯 **智能筛选**：根据目标属性自动筛选最优候选材料

## 🔧 环境要求

- Python 3.8+
- LM Studio（已部署Qwen3.5-9B模型）
- 必要的Python包：`requests`

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动LM Studio

1. 打开LM Studio
2. 加载Qwen3.5-9B模型
3. 点击"Start Server"启动本地API服务器
4. 确保API地址为 `http://localhost:1234`

### 3. 运行系统

```bash
python main.py
```

## 📁 项目文件结构

```
d:\项目\2025\2025校创\code\2\
├── config.py                     # 配置文件
├── llm_client.py               # LM Studio API客户端
├── perovskite_generator.py     # 钙钛矿生成器
├── structure_converter.py      # 结构转换工具
├── tolerance_factor.py         # ⭐ 容忍因子计算模块（使用ML扩展Shannon数据）
├── main.py                     # 交互界面
├── requirements.txt             # 依赖列表
├── README.md                   # 使用说明
├── ML_DATA_INFO.md             # ⭐ ML扩展数据说明
├── ShData.xlsx                 # ⭐ ML扩展Shannon离子半径数据库
└── sciadv.aav0693.pdf         # Bartel容忍因子论文
```

## 💡 协同使用建议

1. **初步筛选**：使用Qwen+τ系统快速生成和验证大量候选材料
2. **深度优化**：对高质量候选材料使用GAN进行结构优化
3. **实验验证**：对最终候选进行DFT计算和实验验证
4. **迭代改进**：将实验结果反馈给GAN继续训练

## 📚 参考文献

1. **Bartel CJ, et al. (2019)** - New tolerance factor to predict the stability of perovskite oxides and halides. *Science Advances*, 5, eaav0693.
2. **ML Extended Shannon Radii** - Extending Shannon's Ionic Radii Database Using Machine Learning. `ShData.xlsx`

---
**Powered by Qwen3.5-9B + LM Studio + ML Extended Shannon Radii** 🔬✨
