#!/bin/bash
# AI Stock Trader V13 一键部署脚本
# 适用于Debian 11/12系统

echo "=========================================="
echo "  AI Stock Trader V13 一键部署"
echo "=========================================="
echo ""

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  请不要使用root用户运行此脚本"
    echo "   使用普通用户运行: bash deploy.sh"
    exit 1
fi

# 1. 更新系统
echo "[1/5] 更新系统包..."
sudo apt update -qq
echo "✅ 系统更新完成"

# 2. 安装Python3和pip
echo ""
echo "[2/5] 安装Python3和pip..."
sudo apt install -y python3 python3-pip > /dev/null 2>&1
python3 --version
pip3 --version
echo "✅ Python3安装完成"

# 3. 安装Python依赖
echo ""
echo "[3/5] 安装Python依赖包..."
echo "   这可能需要几分钟..."
pip3 install --user tushare pandas numpy requests > /dev/null 2>&1
echo "✅ Python依赖安装完成"

# 4. 设置权限
echo ""
echo "[4/5] 设置文件权限..."
chmod +x ai_stock_trader_v13.py
chmod +x trade_recorder.py
chmod +x test_system.py
echo "✅ 权限设置完成"

# 5. 运行测试
echo ""
echo "[5/5] 运行系统测试..."
python3 test_system.py

echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""
echo "📚 使用指南:"
echo "   1. 查看文档: cat README.md"
echo "   2. 运行系统: python3 ai_stock_trader_v13.py"
echo "   3. 记录结果: python3 trade_recorder.py"
echo "   4. 系统测试: python3 test_system.py"
echo ""
echo "⚠️  重要提示:"
echo "   - 首次运行请先执行系统测试"
echo "   - 建议小仓位测试"
echo "   - 所有交易需人工确认"
echo ""
echo "🎉 祝你交易顺利！"
