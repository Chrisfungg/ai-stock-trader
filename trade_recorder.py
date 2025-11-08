#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI交易结果记录工具
用于手动记录实际交易结果，评估AI推荐的准确性
"""

import sqlite3
import sys
from datetime import datetime
from typing import List, Dict, Optional

class TradeRecorder:
    """交易结果记录器"""
    
    def __init__(self, db_path: str = "ai_trading_v13.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
    
    def get_pending_trades(self) -> List[Dict]:
        """获取待记录结果的交易"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT id, stock_code, stock_name, buy_price, sell_target, 
                   stop_loss, expected_return, confidence, trade_date
            FROM ai_recommendations
            WHERE actual_return IS NULL
            ORDER BY trade_date DESC, id DESC
            LIMIT 20
        ''')
        
        rows = cursor.fetchall()
        
        return [
            {
                'id': r[0],
                'code': r[1],
                'name': r[2],
                'buy_price': r[3],
                'sell_target': r[4],
                'stop_loss': r[5],
                'expected_return': r[6],
                'confidence': r[7],
                'trade_date': r[8]
            }
            for r in rows
        ]
    
    def record_trade_result(self, trade_id: int, actual_buy: float,
                           actual_sell: float, notes: str = ""):
        """记录交易实际结果"""
        # 计算实际收益
        actual_return = ((actual_sell - actual_buy) / actual_buy) * 100
        result = 'win' if actual_return > 0 else 'loss'
        
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE ai_recommendations
            SET actual_return = ?,
                result = ?
            WHERE id = ?
        ''', (actual_return, result, trade_id))
        
        self.conn.commit()
        
        return actual_return, result
    
    def get_ai_performance(self) -> Dict:
        """获取AI推荐绩效"""
        cursor = self.conn.cursor()
        
        # 总体统计
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                AVG(CASE WHEN result = 'win' THEN 1.0 ELSE 0.0 END) * 100 as win_rate,
                AVG(actual_return) as avg_return,
                SUM(actual_return) as total_return,
                MIN(actual_return) as worst_trade,
                MAX(actual_return) as best_trade
            FROM ai_recommendations
            WHERE actual_return IS NOT NULL
        ''')
        
        stats = cursor.fetchone()
        
        # 按信心度分组统计
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN confidence >= 0.8 THEN 'high'
                    WHEN confidence >= 0.6 THEN 'medium'
                    ELSE 'low'
                END as conf_level,
                COUNT(*) as count,
                AVG(CASE WHEN result = 'win' THEN 1.0 ELSE 0.0 END) * 100 as win_rate,
                AVG(actual_return) as avg_return
            FROM ai_recommendations
            WHERE actual_return IS NOT NULL
            GROUP BY conf_level
        ''')
        
        by_confidence = cursor.fetchall()
        
        # 预期vs实际对比
        cursor.execute('''
            SELECT 
                expected_return,
                actual_return,
                ABS(expected_return - actual_return) as error
            FROM ai_recommendations
            WHERE actual_return IS NOT NULL
            ORDER BY id DESC
            LIMIT 10
        ''')
        
        recent_accuracy = cursor.fetchall()
        
        return {
            'total_trades': stats[0] if stats[0] else 0,
            'win_rate': stats[1] if stats[1] else 0,
            'avg_return': stats[2] if stats[2] else 0,
            'total_return': stats[3] if stats[3] else 0,
            'worst_trade': stats[4] if stats[4] else 0,
            'best_trade': stats[5] if stats[5] else 0,
            'by_confidence': by_confidence,
            'recent_accuracy': recent_accuracy
        }
    
    def show_pending_trades(self):
        """显示待记录的交易"""
        trades = self.get_pending_trades()
        
        if not trades:
            print("\n✅ 没有待记录的交易")
            return None
        
        print("\n" + "=" * 80)
        print("📋 待记录的AI推荐交易")
        print("=" * 80)
        
        for i, trade in enumerate(trades, 1):
            print(f"\n[{i}] {trade['name']}({trade['code']}) - {trade['trade_date']}")
            print(f"    买入价: {trade['buy_price']:.2f}元")
            print(f"    目标价: {trade['sell_target']:.2f}元")
            print(f"    止损价: {trade['stop_loss']:.2f}元")
            print(f"    AI预期: +{trade['expected_return']:.2f}%")
            print(f"    信心度: {trade['confidence']:.0%}")
        
        return trades
    
    def interactive_record(self):
        """交互式记录"""
        trades = self.show_pending_trades()
        
        if not trades:
            return
        
        print("\n" + "=" * 80)
        print("请选择要记录的交易（输入序号，0退出）:")
        
        try:
            choice = int(input(">>> "))
            
            if choice == 0:
                return
            
            if choice < 1 or choice > len(trades):
                print("❌ 无效的选择")
                return
            
            trade = trades[choice - 1]
            
            print(f"\n记录 {trade['name']}({trade['code']}) 的实际结果:")
            print(f"AI建议买入价: {trade['buy_price']:.2f}元")
            
            # 输入实际买入价
            buy_input = input(f"实际买入价（回车使用{trade['buy_price']:.2f}）: ").strip()
            actual_buy = trade['buy_price'] if not buy_input else float(buy_input)
            
            # 输入实际卖出价
            sell_input = input("实际卖出价: ").strip()
            if not sell_input:
                print("❌ 必须输入卖出价")
                return
            actual_sell = float(sell_input)
            
            # 备注
            notes = input("备注（可选）: ").strip()
            
            # 保存
            actual_return, result = self.record_trade_result(
                trade['id'], actual_buy, actual_sell, notes
            )
            
            print("\n" + "=" * 80)
            print("✅ 记录成功！")
            print("=" * 80)
            print(f"买入: {actual_buy:.2f}元")
            print(f"卖出: {actual_sell:.2f}元")
            print(f"实际收益: {actual_return:+.2f}%")
            print(f"结果: {'✅ 盈利' if result == 'win' else '❌ 亏损'}")
            print(f"AI预期: +{trade['expected_return']:.2f}%")
            print(f"预测误差: {abs(actual_return - trade['expected_return']):.2f}%")
            
        except ValueError:
            print("❌ 输入格式错误")
        except KeyboardInterrupt:
            print("\n取消")
    
    def show_performance(self):
        """显示AI绩效"""
        perf = self.get_ai_performance()
        
        print("\n" + "=" * 80)
        print("📊 AI推荐绩效报告")
        print("=" * 80)
        
        if perf['total_trades'] == 0:
            print("\n暂无已完成的交易记录")
            return
        
        print(f"\n【总体表现】")
        print(f"总交易次数: {perf['total_trades']}次")
        print(f"胜率: {perf['win_rate']:.1f}%")
        print(f"平均收益: {perf['avg_return']:+.2f}%")
        print(f"累计收益: {perf['total_return']:+.2f}%")
        print(f"最佳交易: {perf['best_trade']:+.2f}%")
        print(f"最差交易: {perf['worst_trade']:+.2f}%")
        
        print(f"\n【按信心度统计】")
        for conf_level, count, win_rate, avg_return in perf['by_confidence']:
            level_name = {
                'high': '高信心(≥80%)',
                'medium': '中信心(60-80%)',
                'low': '低信心(<60%)'
            }.get(conf_level, conf_level)
            
            print(f"{level_name}:")
            print(f"  交易数: {count}次")
            print(f"  胜率: {win_rate:.1f}%")
            print(f"  平均收益: {avg_return:+.2f}%")
        
        print(f"\n【最近10次预测准确度】")
        print(f"{'AI预期':<10} {'实际':<10} {'误差':<10}")
        print("-" * 35)
        for expected, actual, error in perf['recent_accuracy']:
            print(f"{expected:+6.2f}%    {actual:+6.2f}%    {error:5.2f}%")
        
        # 评估
        print(f"\n【AI能力评估】")
        if perf['win_rate'] >= 70:
            print("✅ 优秀 - 胜率≥70%，AI推荐质量很高")
        elif perf['win_rate'] >= 60:
            print("👍 良好 - 胜率60-70%，AI推荐可靠")
        elif perf['win_rate'] >= 50:
            print("⚠️  及格 - 胜率50-60%，需要优化")
        else:
            print("❌ 不佳 - 胜率<50%，建议暂停或调整策略")
        
        if perf['avg_return'] >= 1.0:
            print("✅ 收益优秀 - 平均收益≥1.0%")
        elif perf['avg_return'] >= 0.5:
            print("👍 收益良好 - 平均收益0.5-1.0%")
        elif perf['avg_return'] >= 0:
            print("⚠️  收益偏低 - 平均收益<0.5%")
        else:
            print("❌ 整体亏损 - 需要立即调整")
    
    def close(self):
        """关闭连接"""
        self.conn.close()


def main():
    """主菜单"""
    recorder = TradeRecorder()
    
    while True:
        print("\n" + "=" * 80)
        print("📝 AI交易结果记录工具")
        print("=" * 80)
        print("\n1. 记录交易结果")
        print("2. 查看AI绩效")
        print("3. 查看待记录交易")
        print("0. 退出")
        
        try:
            choice = input("\n请选择功能: ").strip()
            
            if choice == '1':
                recorder.interactive_record()
            elif choice == '2':
                recorder.show_performance()
            elif choice == '3':
                recorder.show_pending_trades()
                input("\n按回车继续...")
            elif choice == '0':
                print("\n👋 再见！")
                break
            else:
                print("❌ 无效选择")
                
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")
    
    recorder.close()


if __name__ == "__main__":
    main()
