"""
GPT Trading Strategy - ตัวอย่างการใช้งาน
วิธีการตั้งค่าและใช้งานกลยุทธ์ใหม่ที่ใช้ GPT API
"""

# 1. การตั้งค่า API Key
"""
ขั้นตอนการตั้งค่า GPT API:

1. สมัครสมาชิก OpenAI: https://platform.openai.com/
2. สร้าง API Key ใหม่
3. เพิ่ม API Key ใน LiveTradingConfig.py:
   
   GPT_API_KEY = 'sk-your-api-key-here'
   
4. ตั้งค่า billing ใน OpenAI account
5. ทดสอบการเชื่อมต่อ
"""

# 2. การรันระบบ
"""
python LiveTrading.py
"""

# 3. ตัวอย่างการวิเคราะห์ที่ GPT จะได้รับ
example_gpt_input = {
    "symbol": "BTCUSDT",
    "current_price": 58910,
    "timeframe": "1H",
    "indicators": {
        "EMA": {
            "20": 58750,
            "50": 58200,
            "200": 57500
        },
        "RSI": 71,
        "ATR": 450,
        "Volume_Ratio": 1.5
    },
    "market_structure": {
        "BOS": "BULLISH_BOS",
        "FVG": {
            "type": "BULLISH",
            "mid_price": 58900,
            "top": 59000,
            "bottom": 58800
        },
        "Swing_Highs": [(100, 59200), (150, 59500)],
        "Swing_Lows": [(80, 58000), (120, 58300)]
    },
    "news": {
        "high_impact_news": False,
        "safe_to_trade": True
    },
    "request": "วิเคราะห์ความน่าจะเป็นของ A+ Setup และให้คะแนน Confidence Score พร้อมแนะนำ Entry/SL/TP"
}

# 4. ตัวอย่างผลลัพธ์จาก GPT
example_gpt_output = {
    "confidence_score": 82,
    "setup_type": "LONG", 
    "entry_price": 58910,
    "stop_loss": 58650,
    "take_profit": 59690,
    "risk_reward": 3.0,
    "analysis": "Strong bullish setup with multiple confluences: Bullish BOS confirmed, price at FVG mid-level, EMA alignment bullish, RSI showing momentum but not overbought. Volume supporting the move.",
    "confluences": [
        "Bullish BOS confirmed",
        "Price at FVG mid-level", 
        "EMA 20 > EMA 50 > EMA 200",
        "RSI in momentum zone (71)",
        "Volume 1.5x average",
        "No major news impact"
    ],
    "warnings": [
        "RSI approaching overbought - watch for reversal signals",
        "Monitor volume for continuation"
    ]
}

# 5. การตรวจสอบสถานะการทำงาน
"""
# ในระหว่างการทำงาน คุณสามารถดูสถานะได้จาก log:

INFO: GPT Analysis for BTCUSDT: Confidence 82%, Direction: 1
INFO: GPT LONG Setup - Confidence: 82%
INFO: Trade opened successfully on BTCUSDT

# หรือใช้ฟังก์ชันตรวจสอบ:
stats = bot.get_gpt_analysis_summary()
print(f"Confidence: {stats['confidence_score']}%")
print(f"Setup: {stats['setup_type']}")
print(f"Analysis: {stats['analysis']}")
"""

# 6. การปรับแต่งพารามิเตอร์
"""
ในไฟล์ LiveTradingConfig.py คุณสามารถปรับแต่ง:

# ความมั่นใจขั้นต่ำ
MIN_CONFIDENCE_SCORE = 75  # ปรับเป็น 80 สำหรับการเทรดที่เข้มงวดขึ้น

# Risk Reward
MIN_RISK_REWARD = 3.0      # ปรับเป็น 2.5 หรือ 4.0 ตามความต้องการ

# การจำกัดการแพ้
MAX_DAILY_LOSSES = 3       # ปรับตามความเสี่ยงที่รับได้

# เหรียญที่เทรด  
symbols_to_trade = ['BTCUSDT', 'ETHUSDT']  # เพิ่มหรือลดเหรียญ
"""

# 7. การ Backtest กลยุทธ์
"""
# สำหรับ backtesting ใช้ฟังก์ชัน simulate mode:
python back_testing/Backtester.py

# หรือเรียกใช้ใน code:
from TradingStrats import backtest_gpt_strategy

results = backtest_gpt_strategy(Close, High, Low, Volume, start_index=200)
"""

# 8. การแก้ไขปัญหาทั่วไป
"""
GPT Trading Strategy - ตัวอย่างการใช้งาน
วิธีการตั้งค่าและใช้งานกลยุทธ์ใหม่ที่ใช้ GPT API
"""

# 1. การตั้งค่า API Key
"""
ขั้นตอนการตั้งค่า GPT API:

1. สมัครสมาชิก OpenAI: https://platform.openai.com/
2. สร้าง API Key ใหม่
3. เพิ่ม API Key ใน LiveTradingConfig.py:
   
   GPT_API_KEY = 'sk-your-api-key-here'
   
4. ตั้งค่า billing ใน OpenAI account
5. ทดสอบการเชื่อมต่อ
"""

# 2. การรันระบบ
"""
python LiveTrading.py
"""

# 3. ตัวอย่างการวิเคราะห์ที่ GPT จะได้รับ
example_gpt_input = {
    "symbol": "BTCUSDT",
    "current_price": 58910,
    "timeframe": "1H",
    "indicators": {
        "EMA": {
            "20": 58750,
            "50": 58200,
            "200": 57500
        },
        "RSI": 71,
        "ATR": 450,
        "Volume_Ratio": 1.5
    },
    "market_structure": {
        "BOS": "BULLISH_BOS",
        "FVG": {
            "type": "BULLISH",
            "mid_price": 58900,
            "top": 59000,
            "bottom": 58800
        },
        "Swing_Highs": [(100, 59200), (150, 59500)],
        "Swing_Lows": [(80, 58000), (120, 58300)]
    },
    "news": {
        "high_impact_news": False,
        "safe_to_trade": True
    },
    "request": "วิเคราะห์ความน่าจะเป็นของ A+ Setup และให้คะแนน Confidence Score พร้อมแนะนำ Entry/SL/TP"
}

# 4. ตัวอย่างผลลัพธ์จาก GPT
example_gpt_output = {
    "confidence_score": 82,
    "setup_type": "LONG", 
    "entry_price": 58910,
    "stop_loss": 58650,
    "take_profit": 59690,
    "risk_reward": 3.0,
    "analysis": "Strong bullish setup with multiple confluences: Bullish BOS confirmed, price at FVG mid-level, EMA alignment bullish, RSI showing momentum but not overbought. Volume supporting the move.",
    "confluences": [
        "Bullish BOS confirmed",
        "Price at FVG mid-level", 
        "EMA 20 > EMA 50 > EMA 200",
        "RSI in momentum zone (71)",
        "Volume 1.5x average",
        "No major news impact"
    ],
    "warnings": [
        "RSI approaching overbought - watch for reversal signals",
        "Monitor volume for continuation"
    ]
}

# 5. การตรวจสอบสถานะการทำงาน
"""
# ในระหว่างการทำงาน คุณสามารถดูสถานะได้จาก log:

INFO: GPT Analysis for BTCUSDT: Confidence 82%, Direction: 1
INFO: GPT LONG Setup - Confidence: 82%
INFO: Trade opened successfully on BTCUSDT

# หรือใช้ฟังก์ชันตรวจสอบ:
stats = bot.get_gpt_analysis_summary()
print(f"Confidence: {stats['confidence_score']}%")
print(f"Setup: {stats['setup_type']}")
print(f"Analysis: {stats['analysis']}")
"""

# 6. การปรับแต่งพารามิเตอร์
"""
ในไฟล์ LiveTradingConfig.py คุณสามารถปรับแต่ง:

# ความมั่นใจขั้นต่ำ
MIN_CONFIDENCE_SCORE = 75  # ปรับเป็น 80 สำหรับการเทรดที่เข้มงวดขึ้น

# Risk Reward
MIN_RISK_REWARD = 3.0      # ปรับเป็น 2.5 หรือ 4.0 ตามความต้องการ

# การจำกัดการแพ้
MAX_DAILY_LOSSES = 3       # ปรับตามความเสี่ยงที่รับได้

# เหรียญที่เทรด  
symbols_to_trade = ['BTCUSDT', 'ETHUSDT']  # เพิ่มหรือลดเหรียญ
"""

# 7. การ Backtest กลยุทธ์
"""
# สำหรับ backtesting ใช้ฟังก์ชัน simulate mode:
python back_testing/Backtester.py

# หรือเรียกใช้ใน code:
from TradingStrats import backtest_gpt_strategy

results = backtest_gpt_strategy(Close, High, Low, Volume, start_index=200)
"""

# 8. การแก้ไขปัญหาทั่วไป
troubleshooting_guide = """
ปัญหาที่อาจพบ และวิธีแก้ไข:

1. GPT API Error:
   - ตรวจสอบ API Key ถูกต้อง
   - ตรวจสอบ credit balance ใน OpenAI account
   - ลองลด GPT_MODEL เป็น 'gpt-3.5-turbo'

2. No trades generated:
   - ลด MIN_CONFIDENCE_SCORE
   - ตรวจสอบข้อมูลตลาดเพียงพอ (ต้องมี 200+ candles)
   - เช็ก log สำหรับ error messages

3. Too many API calls:
   - เพิ่ม cache time
   - ลด frequency ของการเรียก GPT
   - ใช้ gpt-3.5-turbo แทน gpt-4

4. Poor performance:
   - ปรับ MIN_CONFIDENCE_SCORE ให้สูงขึ้น
   - เพิ่มจำนวน confluences ที่ต้องการ
   - ทดสอบใน paper trading ก่อน

5. High API costs:
   - ใช้ cache สำหรับ similar market conditions
   - ลดความถี่ในการเรียก GPT
   - ใช้ gpt-3.5-turbo สำหรับ basic analysis
"""

# 9. การติดตามประสิทธิภาพ
performance_monitoring = """
การติดตาม KPIs สำคัญ:

1. Win Rate: เป้าหมาย 60%+
2. Average RR: เป้าหมาย 1:3+
3. GPT Confidence vs Actual Results
4. API Cost per Trade
5. Daily/Weekly PnL

# ดู stats ใน log หรือใช้:
trading_stats = TS.get_trading_stats()
print(f"Daily losses: {trading_stats['daily_losses']}")
print(f"Trading allowed: {trading_stats['trading_allowed']}")
"""

# 10. เทคนิคการ Optimize
optimization_tips = """
เทคนิคการปรับปรุงประสิทธิภาพ:

1. Confluence Scoring:
   - เพิ่มน้ำหนักให้ indicators ที่สำคัญ
   - ใช้ multiple timeframe analysis
   
2. Dynamic Parameters:
   - ปรับ confidence threshold ตาม market volatility
   - ใช้ ATR สำหรับ dynamic position sizing

3. Market Regime Filter:
   - หลีกเลี่ยงการเทรดในตลาดไร้ทิศทาง
   - เพิ่มโอกาสในตลาดมี trend ชัด

4. News Integration:
   - เชื่อมต่อ economic calendar API
   - หลีกเลี่ยงเทรดก่อน/หลังข่าวแรง

5. Portfolio Management:
   - diversify ข้าม multiple pairs
   - correlation analysis ระหว่างเหรียญ
"""

# 11. การ Scale Up
scaling_guide = """
เมื่อผลลัพธ์ดีแล้ว สามารถ scale up:

1. เพิ่มจำนวนเหรียญ:
   symbols_to_trade = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT']

2. เพิ่ม position size:
   order_size = 5.0  # จาก 2.5% เป็น 5%

3. เพิ่ม max positions:
   max_number_of_positions = 5  # จาก 3 เป็น 5

4. ใช้ multiple timeframes:
   - 1h สำหรับ main signals
   - 4h สำหรับ trend confirmation
   - 15m สำหรับ precise entry

5. Advanced Risk Management:
   - Position correlation limits
   - Sector exposure limits
   - Volatility-based sizing
"""

# 12. Sample Daily Checklist
daily_checklist = """
เช็กลิสต์รายวันสำหรับ GPT Trading:

□ ตรวจสอบ GPT API status & credit balance
□ Review overnight news และ economic calendar
□ เช็กสถานะ active positions
□ ตรวจสอบ daily P&L vs targets
□ Review GPT confidence scores vs actual results
□ Update symbol watchlist หากจำเป็น
□ Monitor system logs สำหรับ errors
□ Backup trading data และ configurations

Weekly Review:
□ Analyze win/loss patterns
□ Review GPT prompt effectiveness  
□ Update confidence thresholds หากจำเป็น
□ Performance comparison vs benchmark
□ Cost analysis (API costs vs profits)
"""

# 13. Emergency Procedures
emergency_procedures = """
กระบวนการฉุกเฉิน:

1. หาก GPT API down:
   - System จะใช้ fallback strategy อัตโนมัติ
   - หรือสามารถเปลี่ยนเป็น manual mode

2. หากมี unexpected losses:
   - ตรวจสอบ daily loss limit
   - Review recent GPT analyses
   - พิจารณาหยุดเทรดชั่วคราว

3. หาก system error:
   - เช็ก log files
   - Restart system หากจำเป็น
   - Switch เป็น paper trading mode

4. Market crash scenarios:
   - System จะหยุดเทรดอัตโนมัติ
   - Close positions หาก SL ไม่ทำงาน
   - Review risk parameters
"""

print("""
🚀 GPT Trading Strategy Setup Complete!

Next Steps:
1. Set your GPT_API_KEY in LiveTradingConfig.py
2. Test in paper trading mode first  
3. Start with small position sizes
4. Monitor GPT analysis quality
5. Gradually scale up as confidence builds

Remember: GPT วิเคราะห์ได้ดีมาก แต่ยังคงต้องใช้ Risk Management ที่ดี!
""")