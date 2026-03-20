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

## 📚 参考文献

1. **Bartel CJ, et al. (2019)** - New tolerance factor to predict the stability of perovskite oxides and halides. *Science Advances*, 5, eaav0693.
2. **ML Extended Shannon Radii** - Extending Shannon's Ionic Radii Database Using Machine Learning. `ShData.xlsx`

---
**Powered by Qwen3.5-9B + LM Studio + ML Extended Shannon Radii** 🔬✨
