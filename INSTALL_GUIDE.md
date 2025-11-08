# 🚀 AI Stock Trader V13 - 手把手安装教程

## 📋 目录

1. [上传到GitHub](#步骤1上传到github)
2. [一键安装](#步骤2一键安装推荐)
3. [手动安装](#步骤3手动安装备选)
4. [验证安装](#步骤4验证安装)
5. [首次运行](#步骤5首次运行)
6. [常见问题](#常见问题)

---

## 步骤1：上传到GitHub

### 方法A：通过GitHub网页（最简单）

#### 1.1 创建新仓库

1. 登录GitHub：https://github.com
2. 点击右上角 `+` → `New repository`
3. 填写信息：
   ```
   Repository name: ai-stock-trader
   Description: AI驱动的A股短线交易系统
   Public/Private: 选Private（私有）
   ✅ Initialize this repository with a README
   ```
4. 点击 `Create repository`

#### 1.2 上传文件

1. 在仓库页面，点击 `Add file` → `Upload files`
2. 把以下文件全部拖进去：
   ```
   ✅ ai_stock_trader_v13.py
   ✅ trade_recorder.py
   ✅ test_system.py
   ✅ deploy.sh
   ✅ install.sh
   ✅ requirements.txt
   ✅ README.md
   ✅ QUICKSTART.md
   ✅ OPTIMIZATION_GUIDE.md
   ✅ PROJECT_SUMMARY.md
   ```
3. 填写提交信息：`Initial commit - AI Stock Trader V13`
4. 点击 `Commit changes`

#### 1.3 修改install.sh中的仓库地址

1. 在GitHub仓库中，打开 `install.sh`
2. 点击编辑按钮（铅笔图标）
3. 找到第18行：
   ```bash
   REPO_URL="https://github.com/YOUR_USERNAME/ai-stock-trader.git"
   ```
4. 把 `YOUR_USERNAME` 改成你的GitHub用户名，例如：
   ```bash
   REPO_URL="https://github.com/zhangsan/ai-stock-trader.git"
   ```
5. 点击 `Commit changes`

✅ **完成！你的项目已经上传到GitHub了！**

---

### 方法B：通过命令行（高级）

```bash
# 1. 在本地创建git仓库
cd /path/to/your/files
git init

# 2. 添加所有文件
git add .

# 3. 提交
git commit -m "Initial commit - AI Stock Trader V13"

# 4. 关联GitHub仓库（替换YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/ai-stock-trader.git

# 5. 推送到GitHub
git branch -M main
git push -u origin main
```

---

## 步骤2：一键安装（推荐）⭐

### 2.1 SSH登录你的VPS

```bash
ssh root@你的VPS地址
# 或
ssh 用户名@你的VPS地址
```

### 2.2 运行一键安装命令

**替换YOUR_USERNAME为你的GitHub用户名！**

```bash
bash <(curl -Ls https://raw.githubusercontent.com/YOUR_USERNAME/ai-stock-trader/main/install.sh)
```

**完整示例**（假设你的用户名是zhangsan）：
```bash
bash <(curl -Ls https://raw.githubusercontent.com/zhangsan/ai-stock-trader/main/install.sh)
```

### 2.3 按提示操作

安装脚本会自动：
1. ✅ 检查系统环境
2. ✅ 安装Python3和依赖
3. ✅ 从GitHub克隆项目
4. ✅ 安装Python包
5. ✅ 配置API密钥（需要你输入）
6. ✅ 运行系统测试
7. ✅ 创建快捷命令

**需要你输入的内容**：
```
1. Tushare Token: 粘贴你的token
2. DeepSeek API Key: 粘贴你的key
3. 是否运行测试: 输入 y
```

### 2.4 等待完成

看到这个界面就成功了：
```
==========================================
   安装完成！
==========================================

📍 安装位置: /home/username/ai-stock-trader
📚 版本: v13.0

🚀 快速开始:
  1. 进入目录: cd ~/ai-stock-trader
  2. 运行系统: python3 ai_stock_trader_v13.py
  或直接使用: stock

💰 祝你投资顺利，财富自由！
```

---

## 步骤3：手动安装（备选）

如果一键安装失败，可以手动安装：

### 3.1 克隆仓库

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/ai-stock-trader.git
cd ai-stock-trader
```

### 3.2 安装依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python3
sudo apt install -y python3 python3-pip

# 安装Python包
pip3 install -r requirements.txt --user
```

### 3.3 配置API密钥

```bash
# 编辑主程序
nano ai_stock_trader_v13.py

# 找到这两行（大约在第30-31行）：
TUSHARE_TOKEN = "cc39e6a5d5dba006b58ee20e6bfdf65d5c7c9beff2c9d48e4c6dd8f4"
DEEPSEEK_API_KEY = "sk-07dd31b978174415bb03a4e7c07a9ddd"

# 替换成你自己的
# 按 Ctrl+X，然后 Y，然后 Enter 保存
```

### 3.4 设置权限

```bash
chmod +x *.py
chmod +x *.sh
```

---

## 步骤4：验证安装

### 4.1 运行系统测试

```bash
cd ~/ai-stock-trader
python3 test_system.py
```

**期望输出**：
```
🔍 系统诊断工具
==========================================
[1/4] 测试Python依赖包...
  ✅ tushare        - Tushare Pro数据源
  ✅ pandas         - 数据处理
  ✅ numpy          - 数值计算
  ✅ requests       - HTTP请求

[2/4] 测试Tushare Pro连接...
  ✅ Tushare连接成功
  ✅ 积分等级: 2000分

[3/4] 测试DeepSeek API连接...
  ✅ DeepSeek API连接成功
  ✅ 模型: deepseek-chat

[4/4] 测试数据库...
  ✅ 数据库初始化完成

🎉 所有组件测试通过！系统可以正常运行。
```

### 4.2 如果测试失败

**问题1：Python包缺失**
```bash
pip3 install 包名 --user
```

**问题2：Tushare连接失败**
- 检查Token是否正确
- 检查网络连接

**问题3：DeepSeek连接失败**
- 检查API Key是否正确
- 检查是否能访问国外网站

---

## 步骤5：首次运行

### 5.1 直接运行

```bash
cd ~/ai-stock-trader
python3 ai_stock_trader_v13.py
```

### 5.2 或使用快捷命令（如果已安装）

```bash
stock
```

### 5.3 输入本金

```
💰 请输入投资本金:
   金额（元，回车默认6000）: 6000
   ✅ 确认: 6,000元
```

### 5.4 等待分析（3-5分钟）

系统会自动：
1. 采集市场数据
2. 筛选候选股票
3. 调用AI分析
4. 生成交易建议

### 5.5 查看结果

```
==========================================
🤖 DeepSeek AI 交易建议
==========================================

📊 市场判断: 市场温和上涨，适合交易
💡 整体信心度: 75%

✅ AI推荐: 2 只股票

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【股票1】贵州茅台(600519)
─────────────────────────────────────────

💰 交易建议:
   买入价: 1685.50元
   目标价: 1698.25元 (预期收益 0.76%)
   止损价: 1635.00元

📈 仓位配置:
   建议仓位: 40%
   买入数量: 100股
   所需资金: 168,550元

⚠️  风险评估:
   风险等级: MEDIUM
   信心度: 75%
   最大亏损: 5,050元
   持仓天数: 2天

🧠 AI分析:
   该股近期温和放量突破，量价配合良好。
   技术面显示趋势向上，支撑位稳固。
   第二天上涨概率78%，建议买入。

==========================================
```

---

## 常见问题

### Q1: 一键安装命令运行失败

**问题**：`curl: command not found` 或连接失败

**解决**：
```bash
# 先安装curl
sudo apt install curl -y

# 或手动下载脚本
wget https://raw.githubusercontent.com/YOUR_USERNAME/ai-stock-trader/main/install.sh
bash install.sh
```

### Q2: GitHub仓库无法访问

**问题**：`fatal: unable to access...`

**解决方案A**：使用Gitee镜像
```bash
# 1. 在Gitee创建仓库
# 2. 从GitHub导入
# 3. 修改install.sh中的REPO_URL为Gitee地址
```

**解决方案B**：使用代理
```bash
git config --global http.proxy http://代理地址:端口
```

**解决方案C**：手动上传
```bash
# 用FTP/SCP工具手动上传所有文件到VPS
scp *.py *.sh *.md root@VPS地址:/root/ai-stock-trader/
```

### Q3: Python包安装失败

**问题**：`error: externally-managed-environment`

**解决**：
```bash
# 方案1：使用venv
python3 -m venv ~/ai-env
source ~/ai-env/bin/activate
pip install -r requirements.txt

# 方案2：强制安装
pip3 install -r requirements.txt --user --break-system-packages
```

### Q4: 权限问题

**问题**：`Permission denied`

**解决**：
```bash
chmod +x *.py
chmod +x *.sh

# 或使用sudo（如果需要）
sudo chmod +x *.py
```

### Q5: API密钥不工作

**Tushare Token获取**：
1. 访问 https://tushare.pro
2. 注册账号
3. 进入"个人中心" → "接口Token"
4. 复制Token

**DeepSeek API Key获取**：
1. 访问 https://platform.deepseek.com
2. 注册账号
3. 进入"API Keys"
4. 创建新Key并复制

### Q6: 快捷命令不生效

**解决**：
```bash
# 重新加载bashrc
source ~/.bashrc

# 或重新登录SSH
exit
# 然后重新登录

# 如果还不行，手动添加
echo "alias stock='cd ~/ai-stock-trader && python3 ai_stock_trader_v13.py'" >> ~/.bashrc
source ~/.bashrc
```

---

## 🎯 下一步

安装完成后：

1. **阅读文档**
   ```bash
   cat ~/ai-stock-trader/QUICKSTART.md
   ```

2. **小仓位测试**
   - 第1周：模拟测试
   - 第2周：1000-2000元实测

3. **记录结果**
   ```bash
   stock-record
   ```

4. **持续优化**
   - 查看AI准确度
   - 根据表现调整

---

## 📞 需要帮助？

**遇到问题**：
1. 查看日志：`tail -f ~/ai-stock-trader/trader.log`
2. 运行测试：`stock-test`
3. 查看文档：`cat README.md`

**GitHub Issues**：
https://github.com/YOUR_USERNAME/ai-stock-trader/issues

---

## ⚠️ 重要提醒

1. **保护密钥**：不要把API密钥泄露给别人
2. **小仓位测试**：先测试，后加仓
3. **严格风控**：止损必执行
4. **理性投资**：AI是工具，不是神

**祝你安装顺利，投资成功！** 🚀💰
