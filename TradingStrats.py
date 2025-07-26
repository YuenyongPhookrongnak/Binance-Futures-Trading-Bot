"""
GPT-Enhanced Trading Strategy
แทนที่กลยุทธ์เก่าทั้งหมดด้วยระบบใหม่ที่ใช้ GPT API วิเคราะห์ตลาด
เป้าหมาย: ระบบ Rule-based, เทรดเฉพาะ A+ Setup, ปล่อยกำไรวิ่ง
"""

import json
import requests
from LiveTradingConfig import *
from Logger import *
import pandas as pd
import numpy as np

# กำหนดค่าการตั้งค่า GPT API
GPT_API_KEY = ""  # ใส่ OpenAI API Key ที่นี่
GPT_MODEL = "gpt-3.5-turbo"
GPT_API_URL = "https://api.openai.com/v1/chat/completions"

# ค่าคงที่สำหรับกลยุทธ์
MIN_CONFIDENCE_SCORE = 75  # คะแนนความมั่นใจขั้นต่ำ (%)
MIN_RISK_REWARD = 3.0      # Risk:Reward ขั้นต่ำ 1:3
MAX_DAILY_LOSSES = 3       # หยุดเทรดหลังแพ้ 3 ครั้งในวัน
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# ตัวแปรติดตาม
daily_losses = 0
last_trade_date = None
current_symbol = "UNKNOWN"  # เพิ่มตัวแปรสำหรับติดตาม symbol ปัจจุบัน
last_gpt_analysis = None    # เก็บผลลัพธ์ GPT analysis ล่าสุด

def call_gpt_api(prompt_data):
    """
    เรียก GPT API เพื่อวิเคราะห์ตลาด
    """
    try:
        # ตรวจสอบ API Key ก่อน
        if not GPT_API_KEY or GPT_API_KEY == '':
            log.error("❌ GPT_API_KEY not set! Please add your OpenAI API key in LiveTradingConfig.py")
            log.info("💡 Get your API key from: https://platform.openai.com/account/api-keys")
            return None
            
        if GPT_API_KEY.startswith('sk-') is False:
            log.error("❌ Invalid GPT_API_KEY format! Should start with 'sk-'")
            return None
        
        headers = {
            "Authorization": f"Bearer {GPT_API_KEY}",
            "Content-Type": "application/json"
        }
        
        system_prompt = """
        คุณเป็นผู้เชี่ยวชาญด้านการวิเคราะห์ตลาด Forex/Crypto ที่มีประสบการณ์ 10+ ปี
        ทำหน้าที่วิเคราะห์ข้อมูลตลาดและให้คะแนน Confidence Score สำหรับการเข้าเทรด
        
        หลักการวิเคราะห์:
        1. Market Context (TF 4H/1H) - แนวโน้มหลัก
        2. Structure Analysis - BOS/CoC/FVG
        3. Technical Indicators - RSI/EMA/Fibonacci
        4. Support/Resistance - แนวรับ/แนวต้าน
        5. Risk Management - RR ratio
        
        ให้ผลลัพธ์เป็น JSON format:
        {
            "confidence_score": 0-100,
            "setup_type": "LONG/SHORT/NO_TRADE",
            "entry_price": float,
            "stop_loss": float,
            "take_profit": float,
            "risk_reward": float,
            "analysis": "คำอธิบายสั้นๆ",
            "confluences": ["รายการเงื่อนไขที่ตรง"],
            "warnings": ["คำเตือน (ถ้ามี)"]
        }
        """
        
        payload = {
            "model": GPT_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(prompt_data, ensure_ascii=False)}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        response = requests.post(GPT_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # แปลง JSON string เป็น dict
            try:
                analysis = json.loads(content)
                log.info(f"✅ GPT API call successful for {prompt_data.get('symbol', 'UNKNOWN')}")
                return analysis
            except json.JSONDecodeError:
                # ถ้า GPT ไม่ส่ง JSON กลับมา ลองแยกข้อมูล
                return parse_gpt_response(content)
        else:
            error_msg = ""
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            except:
                error_msg = response.text
            
            log.error(f"❌ GPT API Error {response.status_code}: {error_msg}")
            
            if response.status_code == 401:
                log.error("🔑 API Key Error - Please check your OpenAI API key:")
                log.error("   1. Go to https://platform.openai.com/account/api-keys")
                log.error("   2. Create a new API key")
                log.error("   3. Add it to LiveTradingConfig.py: GPT_API_KEY = 'sk-your-key-here'")
                log.error("   4. Make sure you have billing set up in OpenAI account")
            elif response.status_code == 429:
                log.error("⚠️ Rate limit exceeded - too many requests to GPT API")
            elif response.status_code == 403:
                log.error("🚫 Access denied - check API key permissions")
            
            return None
            
    except requests.exceptions.Timeout:
        log.error("⏰ GPT API timeout - request took too long")
        return None
    except requests.exceptions.ConnectionError:
        log.error("🌐 GPT API connection error - check internet connection")
        return None
    except Exception as e:
        log.error(f"❌ GPT API Call Failed: {e}")
        return None

def parse_gpt_response(content):
    """
    แยกข้อมูลจากคำตอบของ GPT กรณีที่ไม่ใช่ JSON
    """
    try:
        # พยายามหา JSON ในข้อความ
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        
        # ถ้าไม่เจอ JSON ให้สร้างค่าเริ่มต้น
        return {
            "confidence_score": 50,
            "setup_type": "NO_TRADE",
            "entry_price": 0,
            "stop_loss": 0,
            "take_profit": 0,
            "risk_reward": 0,
            "analysis": "Unable to parse GPT response",
            "confluences": [],
            "warnings": ["GPT Response parsing failed"]
        }
    except:
        return None

def calculate_technical_indicators(Close, High, Low, Volume, current_index):
    """
    คำนวณ Technical Indicators สำหรับส่งให้ GPT
    """
    try:
        # ใช้ pandas สำหรับคำนวณ
        close_series = pd.Series(Close)
        high_series = pd.Series(High)
        low_series = pd.Series(Low)
        volume_series = pd.Series(Volume)
        
        # EMA
        ema_20 = close_series.ewm(span=20).mean().iloc[current_index]
        ema_50 = close_series.ewm(span=50).mean().iloc[current_index]
        ema_200 = close_series.ewm(span=200).mean().iloc[current_index]
        
        # RSI
        delta = close_series.diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[current_index]
        
        # ATR สำหรับ volatility
        high_low = high_series - low_series
        high_close = (high_series - close_series.shift()).abs()
        low_close = (low_series - close_series.shift()).abs()
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=14).mean().iloc[current_index]
        
        # Volume analysis
        avg_volume = volume_series.rolling(window=20).mean().iloc[current_index]
        volume_ratio = Volume[current_index] / avg_volume if avg_volume > 0 else 1
        
        return {
            "EMA": {
                "20": float(ema_20),
                "50": float(ema_50), 
                "200": float(ema_200)
            },
            "RSI": float(current_rsi),
            "ATR": float(atr),
            "Volume_Ratio": float(volume_ratio),
            "Current_Price": float(Close[current_index])
        }
        
    except Exception as e:
        log.error(f"Technical Indicators calculation failed: {e}")
        return None

def detect_market_structure(Close, High, Low, current_index):
    """
    ตรวจหา Market Structure: BOS, CoC, FVG
    """
    try:
        # หา Swing Highs และ Swing Lows
        lookback = 5
        swing_highs = []
        swing_lows = []
        
        for i in range(lookback, current_index - lookback):
            # Swing High
            if all(High[i] > High[j] for j in range(i-lookback, i)) and \
               all(High[i] > High[j] for j in range(i+1, i+lookback+1)):
                swing_highs.append((i, High[i]))
            
            # Swing Low  
            if all(Low[i] < Low[j] for j in range(i-lookback, i)) and \
               all(Low[i] < Low[j] for j in range(i+1, i+lookback+1)):
                swing_lows.append((i, Low[i]))
        
        # ตรวจหา BOS (Break of Structure)
        bos_type = "NONE"
        if len(swing_highs) >= 2:
            last_high = swing_highs[-1][1]
            if Close[current_index] > last_high:
                bos_type = "BULLISH_BOS"
        
        if len(swing_lows) >= 2:
            last_low = swing_lows[-1][1]
            if Close[current_index] < last_low:
                bos_type = "BEARISH_BOS"
        
        # ตรวจหา FVG (Fair Value Gap)
        fvg = detect_fvg(High, Low, Close, current_index)
        
        return {
            "BOS": bos_type,
            "FVG": fvg,
            "Swing_Highs": swing_highs[-3:] if len(swing_highs) >= 3 else swing_highs,
            "Swing_Lows": swing_lows[-3:] if len(swing_lows) >= 3 else swing_lows
        }
        
    except Exception as e:
        log.error(f"Market Structure detection failed: {e}")
        return None

def detect_fvg(High, Low, Close, current_index):
    """
    ตรวจหา Fair Value Gap (FVG)
    """
    try:
        fvg_data = []
        
        # ตรวจหา FVG ย้อนหลัง 20 candles
        for i in range(max(2, current_index - 20), current_index - 1):
            if i >= 2:
                # Bullish FVG: Low[i+1] > High[i-1]
                if Low[i+1] > High[i-1]:
                    fvg_data.append({
                        "type": "BULLISH",
                        "top": Low[i+1],
                        "bottom": High[i-1],
                        "mid": (Low[i+1] + High[i-1]) / 2,
                        "index": i
                    })
                
                # Bearish FVG: High[i+1] < Low[i-1]  
                if High[i+1] < Low[i-1]:
                    fvg_data.append({
                        "type": "BEARISH", 
                        "top": Low[i-1],
                        "bottom": High[i+1],
                        "mid": (Low[i-1] + High[i+1]) / 2,
                        "index": i
                    })
        
        # หา FVG ที่ใกล้ราคาปัจจุบันที่สุด
        current_price = Close[current_index]
        closest_fvg = None
        min_distance = float('inf')
        
        for fvg in fvg_data:
            distance = abs(current_price - fvg["mid"])
            if distance < min_distance:
                min_distance = distance
                closest_fvg = fvg
        
        return closest_fvg
        
    except Exception as e:
        log.error(f"FVG detection failed: {e}")
        return None

def check_news_impact():
    """
    ตรวจสอบข่าวแรง (สำหรับอนาคตสามารถเชื่อมต่อ News API)
    """
    # ปัจจุบันคืนค่าเริ่มต้น สามารถพัฒนาต่อได้
    return {
        "high_impact_news": False,
        "news_description": "No major news detected",
        "safe_to_trade": True
    }

def gpt_enhanced_strategy(Trade_Direction, Close, High, Low, Volume, current_index):
    """
    กลยุทธ์หลักที่ใช้ GPT API วิเคราะห์ตลาด
    """
    global daily_losses, last_trade_date
    
    try:
        # ตรวจสอบ GPT API Key ก่อนใช้งาน
        if not GPT_API_KEY or GPT_API_KEY == '':
            log.warning("⚠️ GPT_API_KEY not set. Using fallback strategy.")
            return simulate_gpt_analysis(Close, High, Low, Volume, current_index)
        
        # ตรวจสอบการแพ้ 3 ครั้งในวัน
        current_date = pd.Timestamp.now().date()
        if last_trade_date != current_date:
            daily_losses = 0
            last_trade_date = current_date
        
        if daily_losses >= MAX_DAILY_LOSSES:
            log.info(f"🛑 Reached daily loss limit ({MAX_DAILY_LOSSES}). No more trades today.")
            return -99
        
        # ตรวจสอบความยาวข้อมูล
        if current_index < 200:
            log.debug("📊 Insufficient data for GPT analysis (need ≥200 candles)")
            return -99
        
        # คำนวณ Technical Indicators
        indicators = calculate_technical_indicators(Close, High, Low, Volume, current_index)
        if not indicators:
            log.warning("⚠️ Failed to calculate technical indicators")
            return -99
        
        # ตรวจหา Market Structure
        structure = detect_market_structure(Close, High, Low, current_index)
        if not structure:
            log.warning("⚠️ Failed to detect market structure")
            return -99
        
        # ตรวจสอบข่าว
        news = check_news_impact()
        if not news["safe_to_trade"]:
            log.info("📰 High impact news detected. Skipping trade.")
            return -99
        
        # เตรียมข้อมูลส่งให้ GPT
        gpt_data = {
            "symbol": current_symbol,
            "current_price": indicators["Current_Price"],
            "timeframe": "1H",
            "indicators": indicators,
            "market_structure": structure,
            "news": news,
            "request": "วิเคราะห์ความน่าจะเป็นของ A+ Setup และให้คะแนน Confidence Score พร้อมแนะนำ Entry/SL/TP"
        }
        
        # เรียก GPT API
        gpt_analysis = call_gpt_api(gpt_data)
        if not gpt_analysis:
            log.warning("🤖 GPT API call failed. Using fallback analysis.")
            # ใช้การวิเคราะห์แบบง่ายแทน
            return simulate_gpt_analysis(Close, High, Low, Volume, current_index)
        
        # เก็บผลลัพธ์สำหรับใช้ใน Bot class
        global last_gpt_analysis
        last_gpt_analysis = gpt_analysis
        
        # ประเมินผลลัพธ์จาก GPT
        confidence = gpt_analysis.get("confidence_score", 0)
        setup_type = gpt_analysis.get("setup_type", "NO_TRADE")
        risk_reward = gpt_analysis.get("risk_reward", 0)
        
        log.info(f"🤖 GPT Analysis for {current_symbol} - Confidence: {confidence}%, Setup: {setup_type}, RR: {risk_reward}")
        log.info(f"📝 Analysis: {gpt_analysis.get('analysis', 'No analysis')}")
        
        # ตรวจสอบเงื่อนไขการเข้าเทรด
        if confidence < MIN_CONFIDENCE_SCORE:
            log.info(f"📊 Confidence score {confidence}% below minimum {MIN_CONFIDENCE_SCORE}%")
            return -99
        
        if risk_reward < MIN_RISK_REWARD:
            log.info(f"📊 Risk reward {risk_reward} below minimum {MIN_RISK_REWARD}")
            return -99
        
        # กำหนดทิศทางการเทรด
        if setup_type == "LONG":
            Trade_Direction = 1
            log.info(f"🚀 GPT LONG Setup - Confidence: {confidence}%")
        elif setup_type == "SHORT":
            Trade_Direction = 0
            log.info(f"🔻 GPT SHORT Setup - Confidence: {confidence}%")
        else:
            Trade_Direction = -99
            log.info(f"⏸️ GPT recommends NO_TRADE - Confidence: {confidence}%")
        
        return Trade_Direction
        
    except Exception as e:
        log.error(f"❌ GPT Enhanced Strategy failed: {e}")
        log.info("🔄 Falling back to simple analysis")
        return simulate_gpt_analysis(Close, High, Low, Volume, current_index)

def calculate_dynamic_sl_tp(Close, High, Low, entry_price, trade_direction, structure, indicators):
    """
    คำนวณ SL/TP แบบ Dynamic ตาม Market Structure
    """
    try:
        atr = indicators["ATR"]
        current_price = Close[-1]
        
        if trade_direction == 1:  # LONG
            # SL ใต้ Support หรือ FVG
            if structure["FVG"] and structure["FVG"]["type"] == "BULLISH":
                stop_loss = structure["FVG"]["bottom"] - (atr * 0.5)
            else:
                stop_loss = entry_price - (atr * 2)
            
            # TP ที่แนวต้าน หรือ RR 1:3
            sl_distance = entry_price - stop_loss
            take_profit = entry_price + (sl_distance * 3)
            
        else:  # SHORT
            # SL เหนือ Resistance หรือ FVG
            if structure["FVG"] and structure["FVG"]["type"] == "BEARISH":
                stop_loss = structure["FVG"]["top"] + (atr * 0.5)
            else:
                stop_loss = entry_price + (atr * 2)
            
            # TP ที่แนวรับ หรือ RR 1:3
            sl_distance = stop_loss - entry_price
            take_profit = entry_price - (sl_distance * 3)
        
        return abs(entry_price - stop_loss), abs(take_profit - entry_price)
        
    except Exception as e:
        log.error(f"Dynamic SL/TP calculation failed: {e}")
        # ใช้ ATR เป็น fallback
        atr = indicators.get("ATR", Close[-1] * 0.01)
        return atr * 2, atr * 6  # SL: 2 ATR, TP: 6 ATR

# ======================== ฟังก์ชันหลักที่เรียกใช้ ========================

def GPT_Market_Analysis(Trade_Direction, Close, High, Low, Volume, current_index):
    """
    ฟังก์ชันหลักสำหรับกลยุทธ์ GPT Market Analysis
    แทนที่กลยุทธ์เก่าทั้งหมด
    """
    return gpt_enhanced_strategy(Trade_Direction, Close, High, Low, Volume, current_index)

# ======================== ฟังก์ชัน SetSLTP ใหม่ ========================

def SetSLTP(stop_loss_val_arr, take_profit_val_arr, peaks, troughs, Close, High, Low, Trade_Direction, SL_mult, TP_mult, TP_SL_choice, current_index):
    """
    ฟังก์ชัน SetSLTP ใหม่ที่ใช้ Dynamic SL/TP
    """
    try:
        # คำนวณ ATR สำหรับ Dynamic SL/TP
        if len(Close) >= 14:
            high_series = pd.Series(High)
            low_series = pd.Series(Low)
            close_series = pd.Series(Close)
            
            high_low = high_series - low_series
            high_close = (high_series - close_series.shift()).abs()
            low_close = (low_series - close_series.shift()).abs()
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=14).mean().iloc[current_index]
        else:
            atr = Close[current_index] * 0.02  # 2% fallback
        
        # ใช้ GPT-based SL/TP
        if Trade_Direction == 1:  # LONG
            stop_loss_val = atr * SL_mult * 2  # 2x ATR for SL
            take_profit_val = atr * TP_mult * 6  # 6x ATR for TP (RR 1:3)
        elif Trade_Direction == 0:  # SHORT  
            stop_loss_val = atr * SL_mult * 2
            take_profit_val = atr * TP_mult * 6
        else:
            stop_loss_val = -99
            take_profit_val = -99
        
        return stop_loss_val, take_profit_val
        
    except Exception as e:
        log.error(f"SetSLTP failed: {e}")
        # Fallback to percentage-based
        if Trade_Direction != -99:
            stop_loss_val = Close[current_index] * 0.02  # 2%
            take_profit_val = Close[current_index] * 0.06  # 6% (RR 1:3)
            return stop_loss_val, take_profit_val
        return -99, -99

# ======================== ฟังก์ชันสำหรับ tracking ผลการเทรด ========================

def update_trade_result(result):
    """
    อัพเดทผลการเทรด สำหรับติดตาม daily losses
    """
    global daily_losses
    if result == "LOSS":
        daily_losses += 1
        log.info(f"Trade loss recorded. Daily losses: {daily_losses}")

def get_trading_stats():
    """
    ดึงสถิติการเทรด
    """
    return {
        "daily_losses": daily_losses,
        "max_daily_losses": MAX_DAILY_LOSSES,
        "trading_allowed": daily_losses < MAX_DAILY_LOSSES
    }

# ======================== ฟังก์ชันสำหรับ Backtesting ========================

def backtest_gpt_strategy(Close, High, Low, Volume, start_index=200):
    """
    ทดสอบกลยุทธ์ย้อนหลัง (ไม่เรียก GPT API จริง)
    """
    signals = []
    
    for i in range(start_index, len(Close)):
        # จำลองการวิเคราะห์โดยไม่ใช้ GPT API
        signal = simulate_gpt_analysis(Close, High, Low, Volume, i)
        signals.append(signal)
    
    return signals

def simulate_gpt_analysis(Close, High, Low, Volume, current_index):
    """
    จำลองการวิเคราะห์ของ GPT สำหรับ Backtesting
    """
    try:
        # คำนวณ indicators
        indicators = calculate_technical_indicators(Close, High, Low, Volume, current_index)
        if not indicators:
            return -99
        
        # กฎง่ายๆ สำหรับ backtesting
        rsi = indicators["RSI"]
        ema_20 = indicators["EMA"]["20"]
        ema_50 = indicators["EMA"]["50"]
        current_price = Close[current_index]
        
        # Bullish setup
        if (rsi < 40 and 
            current_price > ema_20 and 
            ema_20 > ema_50 and
            Close[current_index] > Close[current_index-1]):
            return 1
        
        # Bearish setup  
        if (rsi > 60 and
            current_price < ema_20 and
            ema_20 < ema_50 and
            Close[current_index] < Close[current_index-1]):
            return 0
        
        return -99
        
    except Exception as e:
        log.error(f"Simulated GPT analysis failed: {e}")
        return -99