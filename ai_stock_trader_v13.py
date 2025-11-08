#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI驱动A股短线交易系统 V13
基于DeepSeek AI + Tushare Pro数据
目标：每日0.5%+收益，T+1短线交易
"""

import os
import sys
import json
import time
import sqlite3
import warnings
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import tushare as ts
import pandas as pd
import numpy as np
import requests

warnings.filterwarnings('ignore')

# ==================== 配置类 ====================
class Config:
    """系统配置"""
    # API配置
    TUSHARE_TOKEN = "cc39e6a5d5dba006b58ee20e6bfdf65d5c7c9beff2c9d48e4c6dd8f4"
    DEEPSEEK_API_KEY = "sk-07dd31b978174415bb03a4e7c07a9ddd"
    DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
    
    # 交易配置
    TARGET_RETURN = 0.75  # 目标收益率(%)
    MAX_HOLD_DAYS = 2     # 最大持仓天数(T+1实际是2天)
    MIN_WIN_RATE = 60     # 最小胜率要求(%)
    
    # 风险控制
    STOP_LOSS_RATIO = -3.0   # 止损比例(%)
    MAX_POSITION_RATIO = 0.9  # 最大仓位比例
    
    # 数据库
    DB_PATH = "ai_trading_v13.db"
    
    # 输出目录
    OUTPUT_DIR = "ai_reports_v13"


# ==================== DeepSeek API客户端 ====================
class DeepSeekClient:
    """DeepSeek API客户端"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(self, messages: List[Dict[str, str]], 
                       temperature: float = 0.3,
                       max_tokens: int = 4000) -> Optional[str]:
        """调用DeepSeek聊天API"""
        try:
            url = f"{self.base_url}/chat/completions"
            payload = {
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "response_format": {"type": "json_object"}  # 强制JSON输出
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            return content
            
        except Exception as e:
            print(f"❌ DeepSeek API调用失败: {e}")
            return None


# ==================== 提示词工程 ====================
class PromptEngine:
    """AI提示词工程"""
    
    @staticmethod
    def build_system_prompt() -> str:
        """构建系统提示词 - A股专家"""
        return """# 角色定位
你是一位专业的A股短线交易专家AI，专注于T+1日内波段交易策略。

# 核心任务（最重要）
你的唯一目标是：**选出明天大概率上涨的股票**

⚠️ 关键点：
- T+1意味着今天买入，明天才能卖出
- 所以不是看"今天是否强势"，而是预测"明天是否上涨"
- 今天涨停的股票，明天可能下跌
- 今天小涨的股票，明天可能继续涨

# 交易环境
- **市场**: 中国A股市场
- **交易制度**: T+1（当天买入，次日才能卖出）
- **交易时间**: 9:30-11:30, 13:00-15:00
- **涨跌幅限制**: 主板±10%，科创板/创业板±20%
- **交易成本**: 佣金约0.025%，印花税0.1%（卖出）
- **目标收益**: 每笔交易0.75%-1.0%+
- **交易周期**: 1-2天（第1天买入，第2天卖出）

# 决策动作
你需要从候选股票中做出以下决策：
1. **select**: 选择推荐的股票（1-3只）
2. **reject**: 拒绝所有股票（市场环境不佳时）

# 输出格式（必须返回有效JSON）
```json
{
  "action": "select" | "reject",
  "recommendations": [
    {
      "stock_code": "股票代码",
      "stock_name": "股票名称",
      "buy_price": 建议买入价,
      "sell_target": 目标卖出价,
      "stop_loss": 止损价,
      "position_ratio": 仓位比例(0-1),
      "confidence": 信心度(0-1),
      "holding_days": 预计持仓天数(1-2),
      "expected_return": 预期收益率(%),
      "risk_level": "low" | "medium" | "high",
      "reasoning": "选股理由（简明扼要，200字内）"
    }
  ],
  "market_view": "市场整体判断",
  "risk_warning": "风险提示",
  "total_confidence": 整体信心度(0-1)
}
```

# 决策框架

## 核心原则：预测明天，而非总结今天

⚠️ 常见错误：
- ❌ "今天涨了5%，技术指标很好" → 明天可能回调
- ❌ "RSI超买，但还在涨" → 追高风险大
- ✅ "今天温和放量突破，明天有望继续" → 这才是好标的

## 判断"明天上涨概率"的关键要素：

### 1. 量价配合（最重要）
   - 今天放量上涨 + 温和涨幅(1-5%) = 明天大概率继续
   - 今天缩量上涨 或 巨量上涨(>7%) = 明天可能回调
   - 看"next_day_up_prob"指标，优先选择>70%的

### 2. 位置判断
   - 在相对低位突破 > 在高位盘整
   - 刚突破20日线 > 已经远离均线
   - 接近但未触及前期高点 = 有空间

### 3. 趋势延续性
   - 连续2-3天温和上涨 > 单日暴涨
   - 趋势刚启动 > 趋势末端
   - 看"trend_strength"和"breakout_potential"

### 4. 市场环境
   - 大盘上涨 + 板块轮动到该股 = 最佳
   - 大盘下跌但该股逆势 = 需谨慎（可能是诱多）

### 5. 避免追高（关键）
   - 今天涨幅>7%的股票，一般不选（明天回调概率大）
   - 今天涨停的股票，绝对不选（除非特殊情况）
   - RSI>75的股票，谨慎选择

## 原有决策框架

1. **技术面分析**：
   - 趋势：价格相对均线位置（突破/支撑）
   - 动量：RSI、MACD、KDJ指标状态
   - 量能：成交量放大、量比指标
   - 形态：是否突破关键阻力位

2. **资金面分析**：
   - 主力资金净流入情况
   - 大单买入占比
   - 机构持仓变化

3. **基本面筛选**：
   - 避免ST、*ST股票
   - 排除近期暴雷公司
   - 优选行业景气度高的板块

4. **风险控制**：
   - 单只股票仓位不超过40%
   - 确保止损位合理（-3%左右）
   - 预期收益/风险比至少2:1

5. **市场环境**：
   - 大盘趋势（上证指数方向）
   - 板块轮动情况
   - 市场情绪指标

# 关键原则
1. **预测明天，不是总结今天**：重点看"第二天上涨概率"指标
2. **宁缺毋滥**：没有高确定性机会时，选择reject
3. **避免追高**：今天涨幅>7%的一般不要，涨停的绝不要
4. **风险第一**：严格设置止损，保护本金
5. **量价配合**：放量+温和涨幅 > 缩量or暴涨
6. **顺势而为**：不逆大盘趋势操作
7. **快进快出**：T+1特性决定必须快速决策
8. **诚实评估**：confidence要真实反映把握程度

# 注意事项
⚠️ A股特殊性：
- 不能做空，只能做多
- 当天买入不能当天卖出（T+1）
- 注意涨跌停板限制
- 考虑交易成本（至少0.75%才覆盖成本）

现在，请基于下方提供的市场数据和候选股票，做出你的交易决策。"""

    @staticmethod
    def build_user_prompt(market_data: Dict, candidates: List[Dict], 
                         performance: Dict) -> str:
        """构建用户提示词 - 实时数据"""
        
        # 市场概况
        market_section = f"""
# 市场环境状况

## 大盘指数
- **上证指数**: {market_data['sh_index']['current']:.2f} 
  (涨跌: {market_data['sh_index']['change']:.2f}%, 
   5日均线: {market_data['sh_index']['ma5']:.2f}, 
   20日均线: {market_data['sh_index']['ma20']:.2f})
- **价格位置**: 
  相对MA5: {market_data['sh_index'].get('price_vs_ma5', 0):.2f}%, 
  相对MA20: {market_data['sh_index'].get('price_vs_ma20', 0):.2f}%
- **成交量**: {market_data['sh_index']['volume']:.0f}万手 
  (量比: {market_data['sh_index']['volume_ratio']:.2f}x)
- **涨跌分布**: 上涨{market_data['market_breadth']['up']}只 / 
  下跌{market_data['market_breadth']['down']}只 / 
  平盘{market_data['market_breadth']['flat']}只

## 市场判断（重要）
- **趋势评估**: {market_data.get('market_trend', '未知')} (评分: {market_data.get('trend_score', 50)}/100)
- **短期走势**: {market_data.get('short_trend', '未知')} (近3日累计: {market_data.get('recent_3_change', 0):.2f}%)
- **情绪评分**: {market_data['sentiment_score']:.0f}/100
- **主力动向**: {market_data['main_flow_direction']}
- **热点板块**: {', '.join(market_data['hot_sectors'][:3])}

⚠️ **交易建议**: {market_data.get('trading_advice', '正常交易')}
{'🚫 建议今日不操作！市场环境不佳，等待更好时机。' if not market_data.get('suitable_for_trading', True) else '✅ 市场环境适合交易'}

## 技术指标
- **RSI(14)**: {market_data['sh_index'].get('rsi', 0):.1f}
- **MACD**: {market_data['sh_index'].get('macd', 0):.2f}
"""

        # 候选股票
        candidates_section = "\n# 候选股票列表\n\n"
        for i, stock in enumerate(candidates, 1):
            candidates_section += f"""
## 候选{i}: {stock['name']}({stock['code']})

### 基础信息
- **当前价**: {stock['current_price']:.2f}元
- **涨跌幅**: {stock['change_pct']:.2f}%
- **成交量**: {stock['volume']:.0f}手 (量比: {stock['volume_ratio']:.2f}x)
- **换手率**: {stock['turnover']:.2f}%
- **流通市值**: {stock['market_cap']:.2f}亿元
- **所属板块**: {stock['sector']}

### 技术指标
- **MA5**: {stock['ma5']:.2f}元 | **MA10**: {stock['ma10']:.2f}元 | **MA20**: {stock['ma20']:.2f}元
- **RSI(7)**: {stock['rsi7']:.1f} | **RSI(14)**: {stock['rsi14']:.1f}
- **MACD**: {stock['macd']:.3f} | **信号线**: {stock['macd_signal']:.3f}
- **KDJ**: K={stock['kdj_k']:.1f}, D={stock['kdj_d']:.1f}, J={stock['kdj_j']:.1f}
- **BOLL**: 上轨{stock['boll_upper']:.2f}, 中轨{stock['boll_mid']:.2f}, 下轨{stock['boll_lower']:.2f}

### 资金流向
- **主力净流入**: {stock['main_inflow']:.2f}万元
- **大单买入**: {stock['big_buy_ratio']:.1f}%
- **散户净流入**: {stock['retail_inflow']:.2f}万元

### 技术形态
- **形态描述**: {stock['pattern']}
- **支撑位**: {stock['support']:.2f}元
- **阻力位**: {stock['resistance']:.2f}元

### 综合评分
- **技术评分**: {stock['tech_score']:.0f}/100
- **资金评分**: {stock['capital_score']:.0f}/100
- **基本面评分**: {stock['fundamental_score']:.0f}/100
- **总评分**: {stock['total_score']:.0f}/100

### ⭐ 第二天上涨概率预测（关键）
- **综合上涨概率**: {stock['next_day_up_prob']:.1f}% {'🔥' if stock['next_day_up_prob'] > 70 else ''}
- **量价配合度**: {stock['volume_price_match']:.0%} {'✓' if stock['volume_price_match'] > 0.7 else ''}
- **趋势强度**: {stock['trend_strength']:.0%}
- **位置优势**: {stock['position_score']:.0%} (越高越好)
- **突破潜力**: {stock['breakout_potential']:.0%}

---
"""

        # 历史绩效
        performance_section = f"""
# 系统历史绩效

- **总交易次数**: {performance['total_trades']}次
- **胜率**: {performance['win_rate']:.1f}%
- **平均收益**: {performance['avg_return']:.2f}%
- **累计收益**: {performance['total_return']:.2f}%
- **最大回撤**: {performance['max_drawdown']:.2f}%
- **夏普比率**: {performance['sharpe_ratio']:.2f}
- **连续盈利**: {performance['consecutive_wins']}次
- **连续亏损**: {performance['consecutive_losses']}次

⚠️ 如果连续亏损≥3次，建议暂停交易或降低仓位
"""

        # 组合完整提示词
        full_prompt = market_section + candidates_section + performance_section
        full_prompt += "\n请基于以上数据，做出你的交易决策（返回JSON格式）："
        
        return full_prompt


# ==================== 数据采集器 ====================
class DataCollector:
    """Tushare数据采集"""
    
    def __init__(self, token: str):
        self.pro = ts.pro_api(token)
        ts.set_token(token)
    
    def get_market_overview(self) -> Dict:
        """获取市场概况"""
        try:
            # 上证指数数据
            today = datetime.now().strftime('%Y%m%d')
            df_index = self.pro.index_daily(ts_code='000001.SH', 
                                           end_date=today, 
                                           fields='trade_date,close,pct_chg,vol,amount')
            
            if df_index.empty:
                return self._get_default_market_data()
            
            df_index = df_index.sort_values('trade_date')
            latest = df_index.iloc[-1]
            
            # 计算均线
            df_index['ma5'] = df_index['close'].rolling(5).mean()
            df_index['ma20'] = df_index['close'].rolling(20).mean()
            
            # === 关键：判断市场趋势 ===
            # 1. 短期趋势（最近3天）
            recent_3_change = df_index['pct_chg'].iloc[-3:].sum()
            short_trend = "上涨" if recent_3_change > 0 else "下跌"
            
            # 2. 价格相对均线位置
            price_vs_ma5 = (latest['close'] - df_index['ma5'].iloc[-1]) / df_index['ma5'].iloc[-1] * 100
            price_vs_ma20 = (latest['close'] - df_index['ma20'].iloc[-1]) / df_index['ma20'].iloc[-1] * 100
            
            # 3. 趋势强度
            if latest['close'] > df_index['ma5'].iloc[-1] > df_index['ma20'].iloc[-1]:
                market_trend = "强势上涨"
                trend_score = 80
            elif latest['close'] > df_index['ma5'].iloc[-1]:
                market_trend = "温和上涨"
                trend_score = 60
            elif latest['close'] < df_index['ma5'].iloc[-1] < df_index['ma20'].iloc[-1]:
                market_trend = "弱势下跌"
                trend_score = 20
            else:
                market_trend = "震荡整理"
                trend_score = 50
            
            # 市场宽度
            df_all = ts.get_today_all()
            market_breadth = {
                'up': len(df_all[df_all['changepercent'] > 0]),
                'down': len(df_all[df_all['changepercent'] < 0]),
                'flat': len(df_all[df_all['changepercent'] == 0])
            }
            
            # 情绪评分（优化版）
            up_ratio = market_breadth['up'] / (market_breadth['up'] + market_breadth['down'] + 1)
            volume_factor = min(latest['vol'] / df_index['vol'].mean(), 1.5) / 1.5  # 量能因子
            sentiment_score = (up_ratio * 0.6 + volume_factor * 0.4 + trend_score / 100 * 0.0) * 100
            
            # === 判断是否适合交易（关键）===
            suitable_for_trading = True
            trading_advice = "正常交易"
            
            if sentiment_score < 30:
                suitable_for_trading = False
                trading_advice = "市场情绪低迷，建议观望"
            elif trend_score < 40 and recent_3_change < -3:
                suitable_for_trading = False
                trading_advice = "市场持续下跌，建议空仓"
            elif up_ratio < 0.3:
                suitable_for_trading = False
                trading_advice = "普跌行情，不宜操作"
            
            # 主力流向
            main_flow = "净流入" if latest['amount'] > df_index['amount'].mean() else "净流出"
            
            # 热点板块（简化，实际可用行业板块API）
            hot_sectors = ["新能源", "半导体", "人工智能"]
            
            return {
                'sh_index': {
                    'current': latest['close'],
                    'change': latest['pct_chg'],
                    'volume': latest['vol'] / 10000,  # 转换为万手
                    'volume_ratio': latest['vol'] / df_index['vol'].mean(),
                    'ma5': df_index['ma5'].iloc[-1],
                    'ma20': df_index['ma20'].iloc[-1],
                    'rsi': self._calculate_rsi(df_index['close'].values),
                    'macd': 0,  # 简化
                    'price_vs_ma5': price_vs_ma5,
                    'price_vs_ma20': price_vs_ma20
                },
                'market_breadth': market_breadth,
                'sentiment_score': sentiment_score,
                'main_flow_direction': main_flow,
                'hot_sectors': hot_sectors,
                'market_trend': market_trend,
                'trend_score': trend_score,
                'short_trend': short_trend,
                'recent_3_change': recent_3_change,
                'suitable_for_trading': suitable_for_trading,
                'trading_advice': trading_advice
            }
            
        except Exception as e:
            print(f"⚠️ 市场数据获取失败: {e}")
            return self._get_default_market_data()
    
    def _get_default_market_data(self) -> Dict:
        """默认市场数据"""
        return {
            'sh_index': {
                'current': 3000, 'change': 0, 'volume': 100000,
                'volume_ratio': 1.0, 'ma5': 3000, 'ma20': 3000,
                'rsi': 50, 'macd': 0
            },
            'market_breadth': {'up': 2000, 'down': 2000, 'flat': 500},
            'sentiment_score': 50,
            'main_flow_direction': '观望',
            'hot_sectors': ['未知']
        }
    
    def get_candidate_stocks(self, num: int = 20) -> List[Dict]:
        """获取候选股票（严格筛选，提高质量）"""
        try:
            today = datetime.now().strftime('%Y%m%d')
            df = ts.get_today_all()
            
            # 第一轮：基础过滤（排除垃圾股）
            df = df[
                (df['changepercent'] > 0.5) &  # 涨幅>0.5%（有一定强度）
                (df['changepercent'] < 7.0) &  # 涨幅<7%（避免追高）
                (df['trade'] > 8) &  # 价格>8元（避免低价股）
                (df['trade'] < 100) &  # 价格<100元（避免超高价股）
                (df['mktcap'] > 50) &  # 市值>50亿（避免小盘股）
                (df['mktcap'] < 3000) &  # 市值<3000亿（避免超级大盘股）
                (df['volume'] > 10000) &  # 成交量>1万手（有活跃度）
                (~df['name'].str.contains('ST|退|险'))  # 排除ST、退市、风险股
            ].copy()
            
            # 第二轮：强势特征筛选（关键！）
            df = df[
                (df['turnoverratio'] > 1.0) &  # 换手率>1%（有资金关注）
                (df['turnoverratio'] < 15) &  # 换手率<15%（避免过度炒作）
            ].copy()
            
            # 计算量比（需要获取昨日成交量）
            # 这里简化，实际应该查询历史数据
            df['volume_ratio_estimate'] = df['volume'] / df['volume'].mean()
            df = df[df['volume_ratio_estimate'] > 1.2].copy()  # 量比>1.2（放量）
            
            # 按涨幅排序
            df = df.sort_values('changepercent', ascending=False).head(num)
            
            candidates = []
            for _, row in df.iterrows():
                stock_data = self._enrich_stock_data(row)
                if stock_data:
                    candidates.append(stock_data)
            
            return candidates[:num]
            
        except Exception as e:
            print(f"⚠️ 候选股票获取失败: {e}")
            return []
    
    def _enrich_stock_data(self, row: pd.Series) -> Optional[Dict]:
        """丰富股票数据"""
        try:
            code = row['code']
            ts_code = f"{code}.{'SH' if code.startswith('6') else 'SZ'}"
            
            # 获取历史数据计算技术指标
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=60)).strftime('%Y%m%d')
            
            df_daily = self.pro.daily(ts_code=ts_code, 
                                     start_date=start_date, 
                                     end_date=end_date)
            
            if df_daily.empty or len(df_daily) < 20:
                return None
            
            df_daily = df_daily.sort_values('trade_date')
            
            # 计算技术指标
            close_prices = df_daily['close'].values
            volumes = df_daily['vol'].values
            
            # 均线
            ma5 = pd.Series(close_prices).rolling(5).mean().iloc[-1]
            ma10 = pd.Series(close_prices).rolling(10).mean().iloc[-1]
            ma20 = pd.Series(close_prices).rolling(20).mean().iloc[-1]
            
            # RSI
            rsi7 = self._calculate_rsi(close_prices, period=7)
            rsi14 = self._calculate_rsi(close_prices, period=14)
            
            # MACD
            macd, signal = self._calculate_macd(close_prices)
            
            # KDJ
            kdj_k, kdj_d, kdj_j = self._calculate_kdj(df_daily)
            
            # BOLL
            boll_upper, boll_mid, boll_lower = self._calculate_boll(close_prices)
            
            # 支撑阻力
            support = close_prices[-20:].min()
            resistance = close_prices[-20:].max()
            
            # 形态识别（简化）
            pattern = self._identify_pattern(close_prices, ma5, ma10, ma20)
            
            # === 关键：预测第二天上涨概率 ===
            # 1. 量价配合度
            price_momentum = (close_prices[-1] - close_prices[-5]) / close_prices[-5]
            volume_momentum = volumes[-1] / np.mean(volumes[-5:])
            volume_price_match = 1.0 if (price_momentum > 0 and volume_momentum > 1.2) else 0.5
            
            # 2. 趋势强度（连续几天上涨）
            consecutive_up = 0
            for i in range(len(close_prices)-1, max(0, len(close_prices)-6), -1):
                if i > 0 and close_prices[i] > close_prices[i-1]:
                    consecutive_up += 1
                else:
                    break
            trend_strength = min(consecutive_up / 3, 1.0)  # 归一化到0-1
            
            # 3. 位置（是否在相对低位）
            current_position = (close_prices[-1] - support) / (resistance - support + 0.01)
            position_score = 1.0 - current_position  # 越低越好
            
            # 4. 突破概率（接近但未突破阻力位）
            distance_to_resistance = (resistance - close_prices[-1]) / close_prices[-1]
            breakout_potential = 1.0 if (0 < distance_to_resistance < 0.03) else 0.5
            
            # 综合预测得分
            next_day_up_probability = (
                volume_price_match * 0.3 +
                trend_strength * 0.3 +
                position_score * 0.2 +
                breakout_potential * 0.2
            ) * 100
            
            # 评分（简化）
            tech_score = self._calculate_tech_score(rsi14, macd, kdj_k, close_prices[-1], ma20)
            
            return {
                'code': code,
                'name': row['name'],
                'current_price': row['trade'],
                'change_pct': row['changepercent'],
                'volume': row['volume'],
                'volume_ratio': row['volume'] / (volumes.mean() + 1),
                'turnover': row.get('turnoverratio', 0),
                'market_cap': row['mktcap'],
                'sector': row.get('industry', '未知'),
                'ma5': ma5,
                'ma10': ma10,
                'ma20': ma20,
                'rsi7': rsi7,
                'rsi14': rsi14,
                'macd': macd,
                'macd_signal': signal,
                'kdj_k': kdj_k,
                'kdj_d': kdj_d,
                'kdj_j': kdj_j,
                'boll_upper': boll_upper,
                'boll_mid': boll_mid,
                'boll_lower': boll_lower,
                'pattern': pattern,
                'support': support,
                'resistance': resistance,
                'main_inflow': 0,  # 需要资金流API
                'big_buy_ratio': 0,
                'retail_inflow': 0,
                'tech_score': tech_score,
                'capital_score': 50,  # 简化
                'fundamental_score': 50,  # 简化
                'total_score': tech_score * 0.5 + 50 * 0.5,
                # === 新增：第二天上涨概率（关键指标）===
                'next_day_up_prob': next_day_up_probability,
                'volume_price_match': volume_price_match,
                'trend_strength': trend_strength,
                'position_score': position_score,
                'breakout_potential': breakout_potential
            }
            
        except Exception as e:
            return None
    
    @staticmethod
    def _calculate_rsi(prices: np.ndarray, period: int = 14) -> float:
        """计算RSI"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def _calculate_macd(prices: np.ndarray) -> tuple:
        """计算MACD"""
        if len(prices) < 26:
            return 0.0, 0.0
        
        ema12 = pd.Series(prices).ewm(span=12).mean()
        ema26 = pd.Series(prices).ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        
        return macd.iloc[-1], signal.iloc[-1]
    
    @staticmethod
    def _calculate_kdj(df: pd.DataFrame) -> tuple:
        """计算KDJ"""
        if len(df) < 9:
            return 50.0, 50.0, 50.0
        
        low_list = df['low'].rolling(9).min()
        high_list = df['high'].rolling(9).max()
        
        rsv = (df['close'] - low_list) / (high_list - low_list + 0.00001) * 100
        k = rsv.ewm(com=2).mean()
        d = k.ewm(com=2).mean()
        j = 3 * k - 2 * d
        
        return k.iloc[-1], d.iloc[-1], j.iloc[-1]
    
    @staticmethod
    def _calculate_boll(prices: np.ndarray, period: int = 20) -> tuple:
        """计算布林带"""
        if len(prices) < period:
            mid = prices[-1]
            return mid * 1.02, mid, mid * 0.98
        
        sma = pd.Series(prices).rolling(period).mean().iloc[-1]
        std = pd.Series(prices).rolling(period).std().iloc[-1]
        
        upper = sma + 2 * std
        lower = sma - 2 * std
        
        return upper, sma, lower
    
    @staticmethod
    def _identify_pattern(prices: np.ndarray, ma5: float, 
                         ma10: float, ma20: float) -> str:
        """识别技术形态"""
        current = prices[-1]
        
        if current > ma5 > ma10 > ma20:
            return "多头排列"
        elif current < ma5 < ma10 < ma20:
            return "空头排列"
        elif current > ma5 and prices[-2] < prices[-5]:
            return "突破上涨"
        elif current < ma20 and prices[-1] > prices[-2]:
            return "反弹修复"
        else:
            return "震荡整理"
    
    @staticmethod
    def _calculate_tech_score(rsi: float, macd: float, kdj_k: float,
                             price: float, ma20: float) -> float:
        """计算技术评分"""
        score = 50  # 基础分
        
        # RSI评分
        if 30 < rsi < 70:
            score += 15
        elif rsi < 30:
            score += 10  # 超卖
        
        # MACD评分
        if macd > 0:
            score += 15
        
        # KDJ评分
        if 20 < kdj_k < 80:
            score += 10
        
        # 趋势评分
        if price > ma20:
            score += 10
        
        return min(100, max(0, score))


# ==================== 数据库管理 ====================
class DatabaseManager:
    """数据库管理"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # AI决策记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                action TEXT NOT NULL,
                market_view TEXT,
                total_confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # AI推荐股票表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_id INTEGER,
                stock_code TEXT NOT NULL,
                stock_name TEXT,
                buy_price REAL,
                sell_target REAL,
                stop_loss REAL,
                position_ratio REAL,
                confidence REAL,
                expected_return REAL,
                risk_level TEXT,
                reasoning TEXT,
                actual_return REAL,
                result TEXT,
                trade_date TEXT,
                FOREIGN KEY (decision_id) REFERENCES ai_decisions(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_decision(self, decision: Dict, date_str: str) -> int:
        """保存AI决策"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ai_decisions 
            (date, action, market_view, total_confidence)
            VALUES (?, ?, ?, ?)
        ''', (
            date_str,
            decision['action'],
            decision.get('market_view', ''),
            decision.get('total_confidence', 0)
        ))
        
        decision_id = cursor.lastrowid
        
        # 保存推荐股票
        for stock in decision.get('recommendations', []):
            cursor.execute('''
                INSERT INTO ai_recommendations
                (decision_id, stock_code, stock_name, buy_price, sell_target,
                 stop_loss, position_ratio, confidence, expected_return,
                 risk_level, reasoning, trade_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                decision_id,
                stock['stock_code'],
                stock['stock_name'],
                stock['buy_price'],
                stock['sell_target'],
                stock['stop_loss'],
                stock['position_ratio'],
                stock['confidence'],
                stock['expected_return'],
                stock['risk_level'],
                stock['reasoning'],
                date_str
            ))
        
        conn.commit()
        conn.close()
        
        return decision_id
    
    def get_performance_stats(self) -> Dict:
        """获取绩效统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查询所有已完成的交易
        cursor.execute('''
            SELECT actual_return, result
            FROM ai_recommendations
            WHERE actual_return IS NOT NULL
            ORDER BY id DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'avg_return': 0,
                'total_return': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'consecutive_wins': 0,
                'consecutive_losses': 0
            }
        
        returns = [r[0] for r in results]
        wins = [r for r in returns if r > 0]
        
        # 计算连续盈亏
        consecutive_wins = 0
        consecutive_losses = 0
        current_streak = 0
        for _, result in results:
            if result == 'win':
                if current_streak >= 0:
                    current_streak += 1
                else:
                    current_streak = 1
            else:
                if current_streak <= 0:
                    current_streak -= 1
                else:
                    current_streak = -1
            
            consecutive_wins = max(consecutive_wins, current_streak)
            consecutive_losses = max(consecutive_losses, abs(min(0, current_streak)))
        
        # 计算夏普比率（简化）
        avg_return = np.mean(returns)
        std_return = np.std(returns) if len(returns) > 1 else 1
        sharpe = (avg_return / std_return) if std_return > 0 else 0
        
        return {
            'total_trades': len(results),
            'win_rate': (len(wins) / len(results)) * 100,
            'avg_return': avg_return,
            'total_return': sum(returns),
            'max_drawdown': min(returns) if returns else 0,
            'sharpe_ratio': sharpe,
            'consecutive_wins': consecutive_wins,
            'consecutive_losses': consecutive_losses
        }


# ==================== AI交易系统主类 ====================
class AIStockTrader:
    """AI驱动的股票交易系统"""
    
    def __init__(self, capital: float):
        self.capital = capital
        self.config = Config()
        
        # 初始化组件
        self.deepseek = DeepSeekClient(
            self.config.DEEPSEEK_API_KEY,
            self.config.DEEPSEEK_BASE_URL
        )
        self.data_collector = DataCollector(self.config.TUSHARE_TOKEN)
        self.db = DatabaseManager(self.config.DB_PATH)
        self.prompt_engine = PromptEngine()
        
        # 创建输出目录
        os.makedirs(self.config.OUTPUT_DIR, exist_ok=True)
    
    def run(self):
        """运行AI交易系统"""
        print("\n" + "=" * 80)
        print(" " * 20 + "🤖 AI驱动选股系统 V13")
        print(" " * 15 + "Powered by DeepSeek AI + Tushare Pro")
        print("=" * 80)
        print(f"\n💰 投资本金: {self.capital:,.0f}元")
        print(f"🎯 目标收益: {self.config.TARGET_RETURN}%+")
        print(f"📅 交易模式: T+1短线")
        
        # 第1步：采集市场数据
        print("\n[1/4] 📊 采集市场数据...")
        market_data = self.data_collector.get_market_overview()
        print(f"      上证指数: {market_data['sh_index']['current']:.2f} "
              f"({market_data['sh_index']['change']:+.2f}%)")
        print(f"      市场情绪: {market_data['sentiment_score']:.0f}/100")
        
        # 第2步：获取候选股票
        print("\n[2/4] 🔍 筛选候选股票...")
        candidates = self.data_collector.get_candidate_stocks(num=15)
        print(f"      找到 {len(candidates)} 只候选股票")
        
        if not candidates:
            print("\n⚠️ 未找到符合条件的候选股票")
            return
        
        # 第3步：AI决策
        print("\n[3/4] 🤖 DeepSeek AI分析中...")
        performance = self.db.get_performance_stats()
        
        decision = self._make_ai_decision(market_data, candidates, performance)
        
        if not decision:
            print("\n❌ AI决策失败")
            return
        
        # 第4步：展示结果
        print("\n[4/4] 📋 生成交易建议...")
        self._display_decision(decision, market_data)
        
        # 保存记录
        date_str = datetime.now().strftime('%Y-%m-%d')
        self.db.save_decision(decision, date_str)
        self._save_report(decision, market_data)
        
        print("\n✅ AI分析完成！")
    
    def _make_ai_decision(self, market_data: Dict, 
                          candidates: List[Dict],
                          performance: Dict) -> Optional[Dict]:
        """调用AI做出决策"""
        try:
            # 构建提示词
            system_prompt = self.prompt_engine.build_system_prompt()
            user_prompt = self.prompt_engine.build_user_prompt(
                market_data, candidates, performance
            )
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # 调用DeepSeek API
            print("      调用DeepSeek API...")
            response = self.deepseek.chat_completion(messages)
            
            if not response:
                return None
            
            # 解析JSON响应
            decision = json.loads(response)
            
            # 验证决策
            if not self._validate_decision(decision):
                print("      ⚠️ AI返回的决策格式不正确")
                return None
            
            print(f"      ✓ AI决策: {decision['action']}")
            if decision['action'] == 'select':
                print(f"      ✓ 推荐 {len(decision['recommendations'])} 只股票")
            
            return decision
            
        except json.JSONDecodeError as e:
            print(f"      ❌ JSON解析失败: {e}")
            print(f"      原始响应: {response[:200]}...")
            return None
        except Exception as e:
            print(f"      ❌ AI决策失败: {e}")
            traceback.print_exc()
            return None
    
    def _validate_decision(self, decision: Dict) -> bool:
        """验证决策格式"""
        required_keys = ['action', 'recommendations', 'market_view', 'total_confidence']
        
        if not all(k in decision for k in required_keys):
            return False
        
        if decision['action'] not in ['select', 'reject']:
            return False
        
        if decision['action'] == 'select' and not decision['recommendations']:
            return False
        
        return True
    
    def _display_decision(self, decision: Dict, market_data: Dict):
        """展示AI决策"""
        print("\n" + "=" * 80)
        print("🤖 DeepSeek AI 交易建议")
        print("=" * 80)
        
        print(f"\n📊 市场判断: {decision['market_view']}")
        print(f"💡 整体信心度: {decision['total_confidence']:.0%}")
        
        if decision.get('risk_warning'):
            print(f"⚠️  风险提示: {decision['risk_warning']}")
        
        if decision['action'] == 'reject':
            print("\n🚫 AI建议: 今日不操作")
            print("   理由: 市场环境不佳或无明显机会")
            return
        
        # 显示推荐股票
        print(f"\n✅ AI推荐: {len(decision['recommendations'])} 只股票\n")
        
        for i, stock in enumerate(decision['recommendations'], 1):
            print("━" * 80)
            print(f"\n【股票{i}】{stock['stock_name']}({stock['stock_code']})")
            print("─" * 80)
            
            # 买卖建议
            print(f"\n💰 交易建议:")
            print(f"   买入价: {stock['buy_price']:.2f}元")
            print(f"   目标价: {stock['sell_target']:.2f}元 "
                  f"(预期收益 {stock['expected_return']:.2f}%)")
            print(f"   止损价: {stock['stop_loss']:.2f}元")
            
            # 仓位配置
            amount = self.capital * stock['position_ratio']
            shares = int(amount / (stock['buy_price'] * 100)) * 100
            actual_amount = shares * stock['buy_price']
            
            print(f"\n📈 仓位配置:")
            print(f"   建议仓位: {stock['position_ratio']:.0%}")
            print(f"   买入数量: {shares}股")
            print(f"   所需资金: {actual_amount:,.0f}元")
            
            # 风险评估
            max_loss = (stock['buy_price'] - stock['stop_loss']) * shares
            print(f"\n⚠️  风险评估:")
            print(f"   风险等级: {stock['risk_level'].upper()}")
            print(f"   信心度: {stock['confidence']:.0%}")
            print(f"   最大亏损: {max_loss:,.0f}元")
            print(f"   持仓天数: {stock['holding_days']}天")
            
            # AI分析
            print(f"\n🧠 AI分析:")
            print(f"   {stock['reasoning']}")
        
        print("\n" + "=" * 80)
        print("📅 操作流程:")
        print("   今晚: AI分析完成 ✅")
        print("   明日09:30: 开盘后挂单买入（建议价格附近）")
        print("   明日收盘: 持仓观察（T+1不能卖）")
        print("   后天: 达到目标价或止损价时卖出")
        print("=" * 80)
    
    def _save_report(self, decision: Dict, market_data: Dict):
        """保存报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(
            self.config.OUTPUT_DIR,
            f"AI_Decision_{timestamp}.txt"
        )
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"AI驱动选股系统 V13 - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                f.write(f"本金: {self.capital:,.0f}元\n")
                f.write("=" * 80 + "\n\n")
                
                f.write("【市场环境】\n")
                f.write(f"上证指数: {market_data['sh_index']['current']:.2f} "
                       f"({market_data['sh_index']['change']:+.2f}%)\n")
                f.write(f"市场情绪: {market_data['sentiment_score']:.0f}/100\n\n")
                
                f.write("【AI决策】\n")
                f.write(f"行动: {decision['action']}\n")
                f.write(f"市场判断: {decision['market_view']}\n")
                f.write(f"整体信心: {decision['total_confidence']:.0%}\n\n")
                
                if decision['action'] == 'select':
                    f.write("【推荐股票】\n")
                    for i, stock in enumerate(decision['recommendations'], 1):
                        f.write(f"\n{i}. {stock['stock_name']}({stock['stock_code']})\n")
                        f.write(f"   买入: {stock['buy_price']:.2f}元\n")
                        f.write(f"   目标: {stock['sell_target']:.2f}元 "
                               f"(+{stock['expected_return']:.2f}%)\n")
                        f.write(f"   止损: {stock['stop_loss']:.2f}元\n")
                        f.write(f"   仓位: {stock['position_ratio']:.0%}\n")
                        f.write(f"   信心: {stock['confidence']:.0%}\n")
                        f.write(f"   理由: {stock['reasoning']}\n")
            
            print(f"\n✅ 报告已保存: {filename}")
            
        except Exception as e:
            print(f"\n⚠️ 报告保存失败: {e}")


# ==================== 主函数 ====================
def main():
    """主函数"""
    try:
        print("\n" + "=" * 80)
        print(" " * 25 + "🚀 AI交易系统 V13")
        print(" " * 18 + "基于DeepSeek AI + Tushare Pro")
        print("=" * 80)
        
        # 获取本金
        print("\n💰 请输入投资本金:")
        capital_input = input("   金额（元，回车默认6000）: ").strip()
        capital = 6000 if not capital_input else float(capital_input)
        
        if capital < 1000:
            print("   ⚠️ 本金至少1000元")
            return
        
        print(f"   ✅ 确认: {capital:,.0f}元")
        
        # 运行AI交易系统
        trader = AIStockTrader(capital)
        trader.run()
        
        print("\n🎉 分析完成！祝投资顺利！")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断")
    except Exception as e:
        print(f"\n❌ 系统错误: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
