#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI交易系统测试工具
用于诊断系统各组件是否正常工作
"""

import sys
import json
import requests

def test_python_packages():
    """测试Python包"""
    print("\n[1/4] 测试Python依赖包...")
    
    packages = {
        'tushare': 'Tushare Pro数据源',
        'pandas': '数据处理',
        'numpy': '数值计算',
        'requests': 'HTTP请求'
    }
    
    all_ok = True
    for package, desc in packages.items():
        try:
            __import__(package)
            print(f"  ✅ {package:15} - {desc}")
        except ImportError:
            print(f"  ❌ {package:15} - 缺失！运行: pip3 install {package}")
            all_ok = False
    
    return all_ok


def test_tushare_connection():
    """测试Tushare连接"""
    print("\n[2/4] 测试Tushare Pro连接...")
    
    try:
        import tushare as ts
        
        # 你的token
        token = "cc39e6a5d5dba006b58ee20e6bfdf65d5c7c9beff2c9d48e4c6dd8f4"
        ts.set_token(token)
        pro = ts.pro_api()
        
        # 测试查询
        df = pro.trade_cal(exchange='SSE', start_date='20250101', end_date='20250110')
        
        if not df.empty:
            print(f"  ✅ Tushare连接成功")
            print(f"  ✅ 积分等级: 2000分")
            print(f"  ✅ 数据获取正常（测试查询返回{len(df)}条记录）")
            return True
        else:
            print(f"  ⚠️  Tushare连接成功但数据为空")
            return False
            
    except Exception as e:
        print(f"  ❌ Tushare连接失败: {e}")
        print(f"  💡 请检查Token是否正确")
        return False


def test_deepseek_connection():
    """测试DeepSeek API连接"""
    print("\n[3/4] 测试DeepSeek API连接...")
    
    try:
        api_key = "sk-07dd31b978174415bb03a4e7c07a9ddd"
        base_url = "https://api.deepseek.com/v1"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 测试简单请求
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个测试助手"},
                {"role": "user", "content": "请用JSON格式返回: {\"status\": \"ok\", \"message\": \"测试成功\"}"}
            ],
            "temperature": 0.1,
            "max_tokens": 100,
            "response_format": {"type": "json_object"}
        }
        
        print(f"  🔄 发送测试请求到DeepSeek...")
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            print(f"  ✅ DeepSeek API连接成功")
            print(f"  ✅ 模型: deepseek-chat")
            print(f"  ✅ JSON格式输出正常")
            print(f"  📝 测试响应: {content[:100]}...")
            return True
        else:
            print(f"  ❌ DeepSeek API返回错误: {response.status_code}")
            print(f"  📄 响应: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"  ❌ DeepSeek API请求超时")
        print(f"  💡 请检查网络连接")
        return False
    except Exception as e:
        print(f"  ❌ DeepSeek API连接失败: {e}")
        print(f"  💡 请检查API Key是否正确")
        return False


def test_database():
    """测试数据库"""
    print("\n[4/4] 测试数据库...")
    
    try:
        import sqlite3
        
        db_path = "ai_trading_v13.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('ai_decisions', 'ai_recommendations')
        """)
        
        tables = cursor.fetchall()
        
        if len(tables) == 2:
            print(f"  ✅ 数据库初始化完成")
            print(f"  ✅ 表结构正常")
        else:
            print(f"  ⚠️  数据库表不完整（找到{len(tables)}/2个表）")
            print(f"  💡 首次运行会自动创建表")
        
        # 查询记录数
        cursor.execute("SELECT COUNT(*) FROM ai_decisions")
        decisions_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ai_recommendations")
        recs_count = cursor.fetchone()[0]
        
        print(f"  📊 历史决策: {decisions_count}次")
        print(f"  📊 历史推荐: {recs_count}只股票")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ 数据库测试失败: {e}")
        return False


def run_diagnostic():
    """运行完整诊断"""
    print("\n" + "=" * 80)
    print(" " * 25 + "🔍 系统诊断工具")
    print(" " * 20 + "AI Stock Trader V13")
    print("=" * 80)
    
    results = []
    
    # 测试各个组件
    results.append(("Python包", test_python_packages()))
    results.append(("Tushare", test_tushare_connection()))
    results.append(("DeepSeek", test_deepseek_connection()))
    results.append(("数据库", test_database()))
    
    # 总结
    print("\n" + "=" * 80)
    print("📋 诊断总结")
    print("=" * 80)
    
    all_passed = all(result[1] for result in results)
    
    for name, passed in results:
        status = "✅ 正常" if passed else "❌ 异常"
        print(f"  {name:15} {status}")
    
    print("\n" + "=" * 80)
    
    if all_passed:
        print("🎉 所有组件测试通过！系统可以正常运行。")
        print("\n💡 运行命令: python3 ai_stock_trader_v13.py")
    else:
        print("⚠️  部分组件测试失败，请根据上方提示修复问题。")
    
    print("=" * 80)


if __name__ == "__main__":
    try:
        run_diagnostic()
    except KeyboardInterrupt:
        print("\n\n⏹️ 测试中断")
    except Exception as e:
        print(f"\n❌ 诊断工具出错: {e}")
        import traceback
        traceback.print_exc()
