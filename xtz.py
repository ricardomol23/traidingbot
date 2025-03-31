import MetaTrader5 as mt5
import pandas as pd
import time

# Credenciales para la conexión a MT5
creds = {
    "path": "c:\\Program Files\\MetaTrader 5\\terminal64.exe",
    "login": 40514846,
    "password": "Monedero42.",  # CAMBIA ESTO POR SEGURIDAD
    "server": "Deriv-Demo",
    "timeout": 60000,
    "portable": False
}

# Conectar a MT5
if not mt5.initialize(**creds):
    print(f"Error al conectar a MT5: {mt5.last_error()}")
    quit()
else:
    account_info = mt5.account_info()
    if account_info:
        print(f"✅ Conectado a MT5 - Cuenta: {account_info.login} - Balance: {account_info.balance}")
    else:
        print("⚠️ No se pudo obtener información de la cuenta")

SYMBOL = "EURUSD"
TIMEFRAME = mt5.TIMEFRAME_M5
LOT_SIZE = 0.1
MAGIC_NUMBER = 123456
SL_PIPS = 10  # Stop Loss en pips
TP_PIPS = 20  # Take Profit en pips

tendencia_actual = None  # Estado global de la tendencia

def get_market_structure():
    """Detecta la estructura del mercado identificando HH, LL, HL y LH."""
    rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 100)
    if rates is None or len(rates) == 0:
        print("❌ Error al obtener datos del mercado. Reintentando...")
        return None, None, None, None
    
    df = pd.DataFrame(rates)
    df['cierre_actual'] = df['close']
    df['cierre_anterior1'] = df['cierre_actual'].shift(1)
    df['cierre_anterior2'] = df['cierre_actual'].shift(2)
    
    hh = df[(df['cierre_actual'] > df['cierre_anterior1']) & (df['cierre_anterior1'] > df['cierre_anterior2'])]
    ll = df[(df['cierre_actual'] < df['cierre_anterior1']) & (df['cierre_anterior1'] < df['cierre_anterior2'])]
    hl = df[(df['cierre_actual'] > df['cierre_anterior1']) & (df['cierre_anterior1'] < df['cierre_anterior2'])]
    lh = df[(df['cierre_actual'] < df['cierre_anterior1']) & (df['cierre_anterior1'] > df['cierre_anterior2'])]
    
    return hh, ll, hl, lh

def close_trades():
    """Cierra todas las operaciones abiertas del símbolo y con el MAGIC_NUMBER."""
    positions = mt5.positions_get(symbol=SYMBOL, magic=MAGIC_NUMBER)
    if not positions:
        print("⚠️ No hay operaciones abiertas para cerrar.")
        return
    
    for pos in positions:
        tick = mt5.symbol_info_tick(SYMBOL)
        if tick is None:
            print("❌ No se pudo obtener información del precio para cerrar la orden.")
            continue
        
        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": SYMBOL,
            "volume": pos.volume,
            "type": mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY,
            "position": pos.ticket,
            "price": tick.bid if pos.type == 0 else tick.ask,
            "deviation": 10,
            "magic": MAGIC_NUMBER,
            "type_time": mt5.ORDER_TIME_GTC
        }
        
        order = mt5.order_send(close_request)
        if order.retcode == mt5.TRADE_RETCODE_DONE:
            print("✅ Operación cerrada correctamente.")
        else:
            print(f"❌ Error al cerrar orden: {order.retcode}")

def open_trade():
    """Abre una orden de compra y muestra información detallada."""
    print("⚡ Intentando abrir una compra...")
    
    account_info = mt5.account_info()
    if account_info is None or account_info.balance < 100:
        print("❌ Saldo insuficiente para operar.")
        return
    
    tick = mt5.symbol_info_tick(SYMBOL)
    if tick is None:
        print("❌ No se pudo obtener información del precio.")
        return
    
    spread = tick.ask - tick.bid
    print(f"📊 Spread actual: {spread}")
    if spread > 2 * mt5.symbol_info(SYMBOL).point:
        print("⚠️ Spread demasiado alto, evitando operar.")
        return
    
    point = mt5.symbol_info(SYMBOL).point
    sl = tick.ask - SL_PIPS * point
    tp = tick.ask + TP_PIPS * point
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": LOT_SIZE,
        "type": mt5.ORDER_TYPE_BUY,
        "price": tick.ask,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": MAGIC_NUMBER,
        "type_time": mt5.ORDER_TIME_GTC
    }
    
    print("📤 Enviando orden de compra...")
    order = mt5.order_send(request)
    print(f"📩 Código de respuesta: {order.retcode}")
    if order.retcode == mt5.TRADE_RETCODE_DONE:
        print("✅ Orden de compra abierta exitosamente.")
    else:
        print(f"❌ Error al abrir la orden: {order.comment}")

def run_bot():
    """Ejecuta el bot en un loop infinito."""
    global tendencia_actual
    print("🚀 Iniciando bot...")
    try:
        while True:
            hh, ll, hl, lh = get_market_structure()
            if hh is None or ll is None or hl is None or lh is None:
                time.sleep(300)
                continue
            
            current_price = mt5.symbol_info_tick(SYMBOL).ask
            print(f"📈 Precio actual: {current_price}")
            
            if current_price < hh.iloc[-1]['cierre_actual']:
                print("🔻 Cambio a bajista, cerrando operaciones...")
                close_trades()
            elif current_price > ll.iloc[-1]['cierre_actual']:
                print("🟢 Condición de compra detectada, abriendo compra...")
                open_trade()
            
            time.sleep(300)
    except KeyboardInterrupt:
        mt5.shutdown()
        print("✅ Bot detenido.")

# Ejecutar el bots, soy ricardo

pass
run_bot()
