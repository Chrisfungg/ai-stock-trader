# AI Stock Trader V13 快速使用指南

## 🚀 5分钟快速开始

### 第1步：上传文件到VPS

```bash
# 在你的本地电脑上，使用scp上传文件
scp ai_stock_trader_v13.py root@你的VPS地址:/root/
scp trade_recorder.py root@你的VPS地址:/root/
scp test_system.py root@你的VPS地址:/root/
scp deploy.sh root@你的VPS地址:/root/

# 或者使用FTP工具（如FileZilla）上传
```

### 第2步：登录VPS并部署

```bash
# SSH登录VPS
ssh root@你的VPS地址

# 切换到工作目录
cd /root

# 运行一键部署脚本
bash deploy.sh
```

### 第3步：运行系统

```bash
# 运行AI选股系统
python3 ai_stock_trader_v13.py

# 按提示输入本金（例如：6000）
# 等待3-5分钟，系统会完成分析
```

### 第4步：查看结果

```bash
# 查看生成的报告
ls -lh ai_reports_v13/

# 查看最新报告
cat ai_reports_v13/AI_Decision_*.txt

# 或者直接查看屏幕输出
```

### 第5步：记录实际交易结果（第二天）

```bash
# 运行交易记录工具
python3 trade_recorder.py

# 选择功能：
# 1 - 记录交易结果（输入实际买卖价）
# 2 - 查看AI绩效统计
```

## 📅 每日使用流程

### 晚上20:00（推荐时间）

```bash
# 1. 登录VPS
ssh root@你的VPS地址

# 2. 运行AI系统
python3 ai_stock_trader_v13.py

# 3. 输入本金
6000  # 或你的实际本金

# 4. 等待分析（3-5分钟）
# 系统会自动：
# - 采集市场数据
# - 筛选候选股票
# - AI决策分析
# - 生成交易建议

# 5. 查看结果
# 屏幕会显示：
# - AI推荐的股票
# - 买入价/目标价/止损价
# - 仓位配置
# - 风险评估
# - 操作流程
```

### 次日09:25（开盘前）

```
1. 查看昨晚的AI推荐
2. 准备好资金
3. 思考是否执行（最终决策权在你）
```

### 次日09:30-10:00（开盘后）

```
如果决定执行：
1. 09:30 开盘后，按AI建议的买入价挂单
2. 如果09:45还未成交，可以适当提高价格
3. 10:00前完成买入
```

### 次日15:00（当天收盘）

```
T+1规则：今天买的不能今天卖
- 持仓观察
- 关注价格变化
- 不要恐慌，明天才能卖
```

### 第3天（T+2，可卖出日）

```
09:30 开盘后观察：
- 达到目标价 → 卖出止盈
- 触及止损价 → 卖出止损
- 未达目标但不想持有 → 评估后决定

卖出后：
1. 记录实际买卖价
2. python3 trade_recorder.py
3. 选择1，输入实际价格
4. 系统自动计算收益和AI准确度
```

## 💡 实际操作建议

### 建议1：分批测试

```
第1周：用1000元小仓位测试
第2周：如果胜率>60%，增加到2000元
第3周：如果继续盈利，增加到5000元
稳定盈利后：使用全部计划资金
```

### 建议2：风险控制

```
✅ 必须执行：
- 严格按止损价止损
- 单只股票不超过总资金的40%
- 连亏3次暂停交易1周

❌ 不要做：
- 不要因为"感觉"改变AI建议的价格
- 不要在亏损时加仓"摊平成本"
- 不要因为赚钱就忽视止损
```

### 建议3：记录习惯

```
每次交易后必须记录：
1. 实际买入价
2. 实际卖出价
3. 持仓天数
4. 盈亏原因
5. 经验教训

这样AI才能不断优化！
```

## 🔧 常见问题

### Q1: 系统运行很慢怎么办？

```bash
# 检查网络连接
ping api.deepseek.com
ping tushare.pro

# 如果超时，可能是VPS网络问题
# 建议换一个网络环境好的VPS
```

### Q2: DeepSeek API调用失败

```bash
# 检查API Key是否正确
echo "sk-07dd31b978174415bb03a4e7c07a9ddd"

# 测试API连接
python3 test_system.py

# 如果持续失败，可能是：
# 1. API Key过期（需要重新申请）
# 2. API额度用完（检查DeepSeek账户）
# 3. 网络被墙（需要代理）
```

### Q3: Tushare数据获取失败

```bash
# 检查Token
# 登录 https://tushare.pro/
# 查看个人中心 -> 接口Token

# 检查积分
# 2000积分应该够用
# 如果不够，需要完成任务获取积分
```

### Q4: AI推荐的股票不靠谱

```
可能原因：
1. 市场环境变化（AI基于历史数据）
2. 样本量太小（多交易几次看整体胜率）
3. 参数需要调整（参考README优化部分）

解决方案：
1. 记录每次交易结果
2. 用trade_recorder.py查看AI准确度
3. 如果连续5次胜率<50%，暂停使用
4. 调整System Prompt或候选池参数
```

### Q5: 如何设置定时运行？

```bash
# 编辑crontab
crontab -e

# 添加定时任务（每晚20:00运行）
0 20 * * * cd /root && python3 ai_stock_trader_v13.py >> trader.log 2>&1

# 保存退出

# 查看日志
tail -f trader.log
```

### Q6: 想要更保守/激进的策略

```python
# 编辑 ai_stock_trader_v13.py

# 更保守（降低随机性）
def chat_completion(self, messages, 
                   temperature=0.1,  # 从0.3改为0.1
                   max_tokens=4000):

# 更激进（增加随机性）
def chat_completion(self, messages, 
                   temperature=0.5,  # 从0.3改为0.5
                   max_tokens=4000):
```

### Q7: AI总是选择reject，不推荐股票

```python
# 可能AI太保守，调整System Prompt

# 在 build_system_prompt() 方法中添加：
"""
# 额外指令
适度的风险是必要的，持有现金也有机会成本。
如果市场有明确的机会，不要过度谨慎。
你的目标是通过交易获得收益，而不是避免所有风险。
"""
```

## 📊 如何评估AI表现

### 良好的AI表现指标

```
✅ 胜率 ≥ 60%
✅ 平均收益 ≥ 0.75%
✅ 最大回撤 ≤ 5%
✅ 高信心(≥80%)的交易胜率 ≥ 75%
✅ 连续亏损 ≤ 3次
```

### 需要调整的信号

```
⚠️ 胜率 < 50% → 系统需要优化
⚠️ 平均收益 < 0.3% → 收益太低，不如存款
⚠️ 连续亏损 ≥ 5次 → 立即暂停交易
⚠️ AI信心度与实际表现不符 → 重新训练或调参
```

## 🎓 进阶技巧

### 技巧1：建立个人交易日志

```bash
# 创建日志目录
mkdir -p ~/trading_journal

# 每次交易后记录
echo "2025-11-08 | 股票A | 买入10.5 | 卖出10.8 | +2.8% | AI准 ✅" >> ~/trading_journal/$(date +%Y%m).txt

# 月底复盘
cat ~/trading_journal/202511.txt
```

### 技巧2：多版本对比测试

```bash
# 复制系统创建不同版本
cp ai_stock_trader_v13.py ai_stock_trader_v13_conservative.py
cp ai_stock_trader_v13.py ai_stock_trader_v13_aggressive.py

# 修改不同版本的temperature参数
# v13_conservative: temperature=0.1
# v13: temperature=0.3
# v13_aggressive: temperature=0.5

# 每晚同时运行3个版本
python3 ai_stock_trader_v13_conservative.py
python3 ai_stock_trader_v13.py
python3 ai_stock_trader_v13_aggressive.py

# 记录各版本绩效，选择最优版本
```

### 技巧3：结合你的判断

```
AI是工具，不是神：
1. AI提供建议
2. 你负责决策
3. 结合你的市场判断
4. 只做自己看得懂的票

最佳模式：
AI筛选 → 你复核 → 谨慎执行 → 严格风控
```

## 🆘 紧急情况处理

### 连续亏损时

```
1. 立即停止新交易
2. 查看 trade_recorder.py 的绩效分析
3. 找出亏损原因：
   - 市场整体下跌？
   - AI判断失误？
   - 执行偏差？
4. 调整策略或暂停1-2周
5. 小仓位重新测试
```

### 系统出错时

```bash
# 查看错误日志
tail -100 trader.log

# 重新运行测试
python3 test_system.py

# 如果还是失败
# 联系技术支持或查看错误信息
# 大概率是网络/API问题
```

## 📞 获取帮助

```
遇到问题：
1. 查看 README.md 详细文档
2. 运行 python3 test_system.py 诊断
3. 查看日志文件定位问题
4. 搜索具体错误信息

记住：
- 股市有风险，投资需谨慎
- AI是辅助工具，不是提款机
- 最终决策权和责任都在你
- 保护本金永远是第一位
```

---

**祝你使用顺利，交易盈利！** 🎉
