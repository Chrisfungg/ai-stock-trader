#!/bin/bash
#========================================================
#   AI Stock Trader V13 一键安装脚本
#   支持：Debian 11/12, Ubuntu 20.04/22.04
#   使用方法：bash <(curl -Ls https://raw.githubusercontent.com/YOUR_USERNAME/ai-stock-trader/main/install.sh)
#========================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目信息
REPO_URL="https://github.com/YOUR_USERNAME/ai-stock-trader.git"
INSTALL_DIR="$HOME/ai-stock-trader"
VERSION="v13.0"

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 打印横幅
print_banner() {
    clear
    echo -e "${BLUE}"
    echo "=========================================="
    echo "   AI Stock Trader V13 一键安装"
    echo "   基于 DeepSeek AI + Tushare Pro"
    echo "=========================================="
    echo -e "${NC}"
}

# 检查系统
check_system() {
    print_info "检查系统环境..."
    
    # 检查是否为root
    if [ "$EUID" -eq 0 ]; then
        print_error "请不要使用root用户运行此脚本"
        print_info "使用普通用户运行: bash install.sh"
        exit 1
    fi
    
    # 检查系统类型
    if [ -f /etc/debian_version ]; then
        OS="debian"
        print_success "检测到Debian/Ubuntu系统"
    else
        print_error "不支持的系统，仅支持Debian/Ubuntu"
        exit 1
    fi
    
    # 检查网络
    if ! ping -c 1 github.com &> /dev/null; then
        print_warning "无法连接到GitHub，请检查网络"
        read -p "是否继续？(y/n): " continue
        if [ "$continue" != "y" ]; then
            exit 1
        fi
    fi
}

# 安装依赖
install_dependencies() {
    print_info "安装系统依赖..."
    
    # 更新软件源
    print_info "更新软件源..."
    sudo apt update -qq
    
    # 安装必要软件
    print_info "安装Python3和git..."
    sudo apt install -y python3 python3-pip git curl wget > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        print_success "系统依赖安装完成"
    else
        print_error "系统依赖安装失败"
        exit 1
    fi
}

# 克隆仓库
clone_repository() {
    print_info "从GitHub克隆项目..."
    
    # 如果目录已存在，询问是否覆盖
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "安装目录已存在: $INSTALL_DIR"
        read -p "是否删除并重新安装？(y/n): " choice
        if [ "$choice" = "y" ]; then
            rm -rf "$INSTALL_DIR"
        else
            print_info "跳过克隆，使用现有目录"
            cd "$INSTALL_DIR"
            git pull origin main
            return 0
        fi
    fi
    
    # 克隆仓库
    git clone "$REPO_URL" "$INSTALL_DIR"
    
    if [ $? -eq 0 ]; then
        print_success "项目克隆完成"
        cd "$INSTALL_DIR"
    else
        print_error "项目克隆失败"
        print_info "请检查GitHub地址是否正确，或网络是否正常"
        exit 1
    fi
}

# 安装Python依赖
install_python_packages() {
    print_info "安装Python依赖包..."
    print_info "这可能需要3-5分钟，请耐心等待..."
    
    # 升级pip
    python3 -m pip install --upgrade pip --user -q
    
    # 安装requirements.txt中的包
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt --user -q
    else
        # 如果没有requirements.txt，手动安装
        pip3 install tushare pandas numpy requests openpyxl --user -q
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Python依赖安装完成"
    else
        print_error "Python依赖安装失败"
        exit 1
    fi
}

# 配置API密钥
configure_api_keys() {
    print_info "配置API密钥..."
    echo ""
    
    # Tushare Token
    print_info "请输入您的Tushare Pro Token:"
    print_info "（在 https://tushare.pro 注册并获取）"
    read -p "Tushare Token: " tushare_token
    
    if [ -z "$tushare_token" ]; then
        print_warning "未输入Tushare Token，使用默认值（可能无法使用）"
        tushare_token="YOUR_TUSHARE_TOKEN"
    fi
    
    # DeepSeek API Key
    print_info "请输入您的DeepSeek API Key:"
    print_info "（在 https://platform.deepseek.com 注册并获取）"
    read -p "DeepSeek API Key: " deepseek_key
    
    if [ -z "$deepseek_key" ]; then
        print_warning "未输入DeepSeek API Key，使用默认值（可能无法使用）"
        deepseek_key="YOUR_DEEPSEEK_KEY"
    fi
    
    # 写入配置文件
    cat > config.env << EOF
# AI Stock Trader V13 配置文件
# 生成时间: $(date)

# Tushare Pro Token
export TUSHARE_TOKEN="$tushare_token"

# DeepSeek API Key
export DEEPSEEK_API_KEY="$deepseek_key"

# 其他配置
export TARGET_RETURN=0.75
export MAX_HOLD_DAYS=2
export MIN_WIN_RATE=60
EOF
    
    # 修改主程序中的配置
    if [ -f "ai_stock_trader_v13.py" ]; then
        # 备份原文件
        cp ai_stock_trader_v13.py ai_stock_trader_v13.py.bak
        
        # 替换Token
        sed -i "s/TUSHARE_TOKEN = \".*\"/TUSHARE_TOKEN = \"$tushare_token\"/" ai_stock_trader_v13.py
        sed -i "s/DEEPSEEK_API_KEY = \".*\"/DEEPSEEK_API_KEY = \"$deepseek_key\"/" ai_stock_trader_v13.py
        
        print_success "API密钥配置完成"
    fi
}

# 设置权限
set_permissions() {
    print_info "设置文件权限..."
    
    chmod +x *.py 2>/dev/null
    chmod +x *.sh 2>/dev/null
    
    print_success "权限设置完成"
}

# 运行系统测试
run_system_test() {
    print_info "运行系统测试..."
    echo ""
    
    if [ -f "test_system.py" ]; then
        python3 test_system.py
        
        if [ $? -eq 0 ]; then
            print_success "系统测试通过"
        else
            print_warning "系统测试出现问题，请查看上方日志"
        fi
    else
        print_warning "未找到测试文件，跳过测试"
    fi
}

# 创建快捷命令
create_shortcuts() {
    print_info "创建快捷命令..."
    
    # 创建别名配置
    cat >> ~/.bashrc << 'EOF'

# AI Stock Trader V13 快捷命令
alias stock='cd ~/ai-stock-trader && python3 ai_stock_trader_v13.py'
alias stock-record='cd ~/ai-stock-trader && python3 trade_recorder.py'
alias stock-test='cd ~/ai-stock-trader && python3 test_system.py'
alias stock-update='cd ~/ai-stock-trader && git pull'
EOF
    
    # 使配置生效
    source ~/.bashrc 2>/dev/null || true
    
    print_success "快捷命令创建完成"
    print_info "可以使用以下命令:"
    echo "  stock        - 运行AI选股系统"
    echo "  stock-record - 记录交易结果"
    echo "  stock-test   - 系统测试"
    echo "  stock-update - 更新系统"
}

# 显示安装完成信息
show_completion() {
    echo ""
    echo -e "${GREEN}=========================================="
    echo "   安装完成！"
    echo "==========================================${NC}"
    echo ""
    echo -e "${BLUE}📍 安装位置:${NC} $INSTALL_DIR"
    echo -e "${BLUE}📚 版本:${NC} $VERSION"
    echo ""
    echo -e "${YELLOW}🚀 快速开始:${NC}"
    echo "  1. 进入目录: cd $INSTALL_DIR"
    echo "  2. 运行系统: python3 ai_stock_trader_v13.py"
    echo "  或直接使用: stock"
    echo ""
    echo -e "${YELLOW}📖 使用文档:${NC}"
    echo "  快速指南: cat QUICKSTART.md"
    echo "  完整文档: cat README.md"
    echo "  优化指南: cat OPTIMIZATION_GUIDE.md"
    echo ""
    echo -e "${YELLOW}🔧 常用命令:${NC}"
    echo "  stock        - 运行AI选股"
    echo "  stock-record - 记录结果"
    echo "  stock-test   - 系统测试"
    echo ""
    echo -e "${RED}⚠️  重要提示:${NC}"
    echo "  1. 首次使用建议小仓位测试（1000-2000元）"
    echo "  2. 严格执行止损，保护本金"
    echo "  3. 每次交易后记录实际结果"
    echo "  4. 股市有风险，投资需谨慎"
    echo ""
    echo -e "${GREEN}💰 祝你投资顺利，财富自由！${NC}"
    echo ""
}

# 主函数
main() {
    print_banner
    
    # 检查系统
    check_system
    echo ""
    
    # 安装依赖
    install_dependencies
    echo ""
    
    # 克隆仓库
    clone_repository
    echo ""
    
    # 安装Python包
    install_python_packages
    echo ""
    
    # 配置API密钥
    configure_api_keys
    echo ""
    
    # 设置权限
    set_permissions
    echo ""
    
    # 运行测试
    read -p "是否运行系统测试？(y/n): " run_test
    if [ "$run_test" = "y" ]; then
        run_system_test
    fi
    echo ""
    
    # 创建快捷命令
    create_shortcuts
    echo ""
    
    # 显示完成信息
    show_completion
}

# 错误处理
trap 'print_error "安装过程中出现错误"; exit 1' ERR

# 运行主函数
main
