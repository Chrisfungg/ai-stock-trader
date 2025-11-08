# 🤖 AI Stock Trader V13

> AI驱动的A股短线交易系统 - 基于DeepSeek AI + Tushare Pro

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-Private-red.svg)]()
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

---

## 🎯 项目简介

这是一个完全由AI驱动的A股短线交易系统，使用DeepSeek大模型进行市场分析和选股决策，专为T+1日内波段交易设计。

### 核心特性

- 🤖 **AI驱动决策** - DeepSeek大模型智能分析
- 📊 **实时数据** - Tushare Pro专业数据源
- 🎯 **T+1优化** - 专门适配A股交易规则
- 🛡️ **风险控制** - 多重止损+仓位管理
- 📈 **闭环反馈** - 自动评估AI准确度

### 目标收益

- **单笔目标**：0.75% - 1.0%+
- **预期胜率**：60% - 70%
- **月度收益**：10% - 15%（保守估计）

---

## 🚀 一键安装

### 前提条件

- ✅ Debian 11/12 或 Ubuntu 20.04/22.04
- ✅ 有sudo权限的用户
- ✅ 能访问GitHub
- ✅ Tushare Pro Token（2000积分）
- ✅ DeepSeek API Key

### 快速安装

**替换YOUR_USERNAME为你的GitHub用户名**：

```bash
bash <(curl -Ls https://raw.githubusercontent.com/YOUR_USERNAME/ai-stock-trader/main/install.sh)
```

**3分钟搞定**，自动完成：
- ✅ 系统依赖安装
- ✅ Python包安装
- ✅ 配置API密钥
- ✅ 系统测试
- ✅ 快捷命令创建

---

## 📚 文档

- [三步安装](三步安装.md) - 最简单的安装教程
- [详细安装指南](INSTALL_GUIDE.md) - 完整的安装文档
- [快速开始](QUICKSTART.md) - 5分钟上手指南
- [完整文档](README.md) - 技术架构详解
- [优化指南](OPTIMIZATION_GUIDE.md) - 提升胜率的关键
- [项目总结](PROJECT_SUMMARY.md) - 系统设计说明

---

## 💻 使用方法

### 基础使用

```bash
# 运行AI选股系统
stock

# 或完整命令
cd ~/ai-stock-trader
python3 ai_stock_trader_v13.py
```

### 记录交易结果

```bash
# 记录实际买卖价格
stock-record

# 查看AI准确度统计
```

### 系统测试

```bash
# 诊断系统状态
stock-test
```

### 更新系统

```bash
# 从GitHub拉取最新版本
stock-update
```

---

## 📊 系统架构

```
用户 → AI决策层 → 数据层
         ↓
    DeepSeek AI
    (市场分析 + 选股决策)
         ↓
    Tushare Pro
    (实时行情 + 技术指标)
```

### 核心优化

1. **严格候选池筛选**
   - 涨幅0.5-7%（避免追高）
   - 市值50-3000亿
   - 换手率1-15%
   - 量比>1.2

2. **第二天上涨概率预测**
   - 量价配合度
   - 趋势强度
   - 位置优势
   - 突破潜力

3. **市场环境过滤**
   - 自动判断是否适合交易
   - 大盘不好时自动空仓

4. **AI提示词优化**
   - 明确"预测明天，而非总结今天"
   - 强调避免追高

---

## ⚠️ 风险提示

1. **本系统仅供学习研究**，不构成投资建议
2. **股市有风险，投资需谨慎**
3. **建议小仓位测试**（1000-2000元起）
4. **严格执行止损**，保护本金
5. **AI不是神**，60-70%胜率已很优秀
6. **最终决策权在你**，AI只是辅助

---

## 📈 预期表现

### 保守估计

| 指标 | 目标 |
|------|------|
| 胜率 | 60-65% |
| 单笔收益 | 0.75-1.0% |
| 月收益 | 10-15% |

### 复利威力

```
起始资金：6000元
月收益：10%
预计：3-4年达到50-100万
```

---

## 🔧 技术栈

- **语言**：Python 3.7+
- **AI模型**：DeepSeek deepseek-chat
- **数据源**：Tushare Pro API
- **数据库**：SQLite3
- **数据处理**：Pandas, NumPy

---

## 📝 更新日志

### v13.0 (2025-11-08)

#### 新增功能
- ✅ DeepSeek AI决策引擎
- ✅ 第二天上涨概率预测
- ✅ 市场环境自动过滤
- ✅ 严格候选池筛选
- ✅ 一键安装脚本
- ✅ 完整文档体系

#### 优化内容
- 🔥 针对胜率低的问题全面优化
- 🔥 强化"预测明天"而非"总结今天"
- 🔥 避免追高机制
- 🔥 AI提示词工程优化

---

## 🤝 贡献

本项目为私有项目，仅供个人使用。

---

## 📞 联系方式

有问题？查看文档或Issue。

---

## 📜 许可证

Private - 仅供个人使用

---

## 🙏 致谢

- [Tushare Pro](https://tushare.pro) - 专业金融数据API
- [DeepSeek](https://www.deepseek.com) - 强大的AI大模型
- [Alpha Arena](https://nof1.ai) - AI交易系统设计灵感

---

## ⭐ Star History

如果这个项目帮到你了，给个Star吧！⭐

---

**祝你投资顺利，财富自由！** 🚀💰

*Powered by DeepSeek AI + Claude AI*
