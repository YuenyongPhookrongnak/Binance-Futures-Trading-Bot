API_KEY = ''
API_SECRET = ''

# GPT API Configuration
GPT_API_KEY = ''  # ใส่ OpenAI API Key ที่นี่
GPT_MODEL = 'gpt-3.5-turbo'  # หรือ 'gpt-3.5-turbo' 'gpt-4' เพื่อประหยัดค่าใช้จ่าย

# Trading Strategy Configuration
trading_strategy = 'GPT_Market_Analysis'  # กลยุทธ์หลักใหม่ที่ใช้ GPT

# GPT Strategy Parameters
MIN_CONFIDENCE_SCORE = 75  # คะแนนความมั่นใจขั้นต่ำ (%)
MIN_RISK_REWARD = 3.0      # Risk:Reward ขั้นต่ำ 1:3
MAX_DAILY_LOSSES = 3       # หยุดเทรดหลังแพ้ 3 ครั้งในวัน
GPT_TIMEOUT = 30           # Timeout สำหรับ GPT API (วินาที)

# Market Analysis Settings
ENABLE_NEWS_CHECK = True    # เปิด/ปิดการตรวจสอบข่าว
ENABLE_FVG_ANALYSIS = True  # เปิด/ปิดการวิเคราะห์ FVG
ENABLE_BOS_DETECTION = True # เปิด/ปิดการตรวจหา BOS/CoC

# Legacy Strategy Support
'''
valid options for trading_strategy are: 'GPT_Market_Analysis', 'StochRSIMACD', 'tripleEMAStochasticRSIATR', 
'tripleEMA', 'breakout', 'stochBB', 'goldenCross', 'candle_wick', 'fibMACD', 'EMA_cross', 
'heikin_ashi_ema2', 'heikin_ashi_ema', 'ema_crossover'
'''

# TP/SL Configuration
TP_SL_choice = 'Dynamic_GPT'  # ใหม่: TP/SL แบบ Dynamic จาก GPT
'''
valid options for TP_SL_choice are: 'Dynamic_GPT', '%', 'x (ATR)', 'x (Swing High/Low) level 1',
'x (Swing High/Low) level 2', 'x (Swing High/Low) level 3', 'x (Swing Close) level 1',
'x (Swing Close) level 2', 'x (Swing Close) level 3'
'''

# Risk Management
leverage = 10
order_size = 2.5  # % ของบัญชี - ลดลงเพื่อความปลอดภัย
interval = '1h'   # ใช้ 1h สำหรับการวิเคราะห์ที่มีคุณภาพ
SL_mult = 1.5     # SL multiplier สำหรับ GPT strategy
TP_mult = 3.0     # TP multiplier (RR 1:3)

# Symbol Configuration
trade_all_symbols = False  # เริ่มต้นด้วยเหรียญเฉพาะ
symbols_to_trade = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']  # เหรียญหลักที่มีสภาพคล่อง
coin_exclusion_list = ['USDCUSDT', 'BTCDOMUSDT', 'LUNAUSDT']  # เหรียญที่ไม่ต้องการเทรด

# Trading Controls
use_trailing_stop = False   # ปิดก่อน - ใช้ GPT dynamic exit แทน
trailing_stop_callback = 0.1
trading_threshold = 0.3     # % threshold สำหรับยกเลิกเทรด
use_market_orders = True    # ใช้ market orders สำหรับ execution ที่รวดเร็ว
max_number_of_positions = 3 # จำกัดจำนวนโพซิชัน
wait_for_candle_close = True

# Advanced Risk Management
auto_calculate_buffer = True
buffer = '4 hours ago'  # buffer สำหรับข้อมูลประวัติ

# Daily Trading Rules (GPT Strategy)
DAILY_PROFIT_TARGET = 5.0   # เป้าหมายกำไรรายวัน (%)
DAILY_LOSS_LIMIT = 3.0      # ขีดจำกัดขาดทุนรายวัน (%)
MAX_TRADES_PER_DAY = 5      # จำนวนเทรดสูงสุดต่อวัน

# Market Session Controls
ASIAN_SESSION = {'start': '00:00', 'end': '09:00'}     # UTC
LONDON_SESSION = {'start': '08:00', 'end': '17:00'}    # UTC  
NY_SESSION = {'start': '13:00', 'end': '22:00'}        # UTC
ACTIVE_SESSIONS = ['LONDON', 'NY']  # เทรดเฉพาะช่วงที่มีสภาพคล่อง

# News and Event Management
HIGH_IMPACT_NEWS_BUFFER = 30  # หยุดเทรดก่อน/หลังข่าวแรง (นาที)
ECONOMIC_CALENDAR_EVENTS = [
    'FOMC', 'NFP', 'CPI', 'GDP', 'ECB', 'BOE', 'BOJ'
]

# GPT Prompt Templates
GPT_ANALYSIS_PROMPT = """
Analyze the current market condition for {symbol} and provide trading recommendation.

Market Data:
- Current Price: {current_price}
- EMA 20: {ema_20}
- EMA 50: {ema_50} 
- EMA 200: {ema_200}
- RSI: {rsi}
- Volume Ratio: {volume_ratio}
- Market Structure: {structure}

Requirements:
1. Confidence Score (0-100%)
2. Setup Type (LONG/SHORT/NO_TRADE)
3. Entry, SL, TP levels
4. Risk:Reward ratio
5. Analysis reasoning
6. List of confluences
7. Warnings (if any)

Focus on A+ setups only with minimum 75% confidence and 1:3 RR.
"""

# Logging Configuration
LOG_LEVEL = 20  # INFO level
log_to_file = True
LOG_GPT_RESPONSES = True    # บันทึก GPT responses

# Performance Monitoring
ENABLE_PERFORMANCE_TRACKING = True
BACKTEST_VALIDATION = True
PAPER_TRADING_MODE = False  # เปิดเพื่อทดสอบก่อนใช้เงินจริง

# API Rate Limiting
GPT_RATE_LIMIT = 60         # จำนวนคำขอสูงสุดต่อนาที
GPT_RETRY_ATTEMPTS = 3      # จำนวนครั้งที่ลองใหม่หาก API fail

# Multiprocessing Configuration
use_multiprocessing_for_trade_execution = True

# Custom TP/SL Functions (รวม GPT)
custom_tp_sl_functions = ['USDT', 'Dynamic_GPT']

# Additional Configuration Options
make_decision_options = {
    'gpt_analysis_interval': 300,  # วิเคราะห์ด้วย GPT ทุก 5 นาที
    'cache_gpt_responses': True,   # เก็บ cache GPT responses
    'use_confluence_scoring': True, # ใช้ระบบให้คะแนน confluence
    'min_confluence_count': 3,     # จำนวน confluence ขั้นต่ำ
    'enable_market_regime_filter': True  # กรองตามสภาวะตลาด
}

# Fallback Configuration
FALLBACK_TO_SIMPLE_STRATEGY = True  # ใช้กลยุทธ์ง่ายหาก GPT fail
SIMPLE_STRATEGY_CONFIG = {
    'strategy': 'EMA_cross',
    'ema_fast': 20,
    'ema_slow': 50,
    'rsi_period': 14,
    'rsi_overbought': 70,
    'rsi_oversold': 30
}

# Notification Settings
ENABLE_TRADE_NOTIFICATIONS = True
WEBHOOK_URL = ''  # Discord/Slack webhook สำหรับการแจ้งเตือน
NOTIFICATION_EVENTS = ['TRADE_OPEN', 'TRADE_CLOSE', 'DAILY_SUMMARY', 'HIGH_CONFIDENCE_SIGNAL']

# Debug and Development
DEBUG_MODE = False
SAVE_MARKET_DATA = True     # บันทึกข้อมูลตลาดสำหรับวิเคราะห์
EXPORT_TRADES_TO_CSV = True
GENERATE_DAILY_REPORTS = True

print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║                     GPT-Enhanced Trading Bot                        ║
║                          Configuration                               ║
╠══════════════════════════════════════════════════════════════════════╣
║ Strategy: {trading_strategy:<25} │ Leverage: {leverage:<10} ║
║ Symbols: {str(symbols_to_trade):<26} │ Order Size: {order_size}%        ║
║ Interval: {interval:<24} │ Max Positions: {max_number_of_positions:<5} ║
║ Min Confidence: {MIN_CONFIDENCE_SCORE}%<16> │ Min RR: 1:{MIN_RISK_REWARD:<6} ║
║ Daily Loss Limit: {MAX_DAILY_LOSSES} trades<13> │ Paper Trading: {PAPER_TRADING_MODE:<5} ║
╚══════════════════════════════════════════════════════════════════════╝
""")

# Validation
if not GPT_API_KEY:
    print("⚠️  WARNING: GPT_API_KEY not set. GPT features will be disabled.")

if trading_strategy == 'GPT_Market_Analysis' and not GPT_API_KEY:
    print("❌ ERROR: GPT_Market_Analysis strategy requires GPT_API_KEY")
    print("   Please set your OpenAI API key or switch to a different strategy.")