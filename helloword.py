def run_bot():
    """Ejecuta el bot en un loop, con opción de salida segura"""
    global tendencia_actual
    print("🚀 Iniciando bot... Presiona Ctrl + C para detenerlo.")
    try:
        while True:
            hh, ll, hl = get_market_structure()
            if hh is None or ll is None or hl is None:
                time.sleep(300)
                continue
            
            if not hh.empty and not ll.empty:
                last_hh = hh.iloc[-1]['cierre_actual']
                last_ll = ll.iloc[-1]['cierre_actual']
                last_hl = hl.iloc[-1]['cierre_actual'] if not hl.empty else None
                current_price = mt5.symbol_info_tick(SYMBOL).ask
                
                if current_price < last_hh and tendencia_actual != "bajista":
                    print("🔻 Cambio a bajista, cerrando operaciones...")
                    close_trades()
                    tendencia_actual = "bajista"
                elif (current_price > last_ll) and tendencia_actual != "alcista":
                    print("🟢 Tendencia alcista confirmada, abriendo compra...")
                    open_trade()
                    tendencia_actual = "alcista"
                elif last_hl and current_price > last_hl and tendencia_actual == "bajista":
                    print("🟢 Tendencia bajista con HL detectado, abriendo compra...")
                    open_trade()
                else:
                    print("⚠️ No hay un cambio de tendencia claro.")
            
            time.sleep(300)  # Esperar 5 minutos
    except KeyboardInterrupt:
        print("🛑 Bot detenido manualmente. Cerrando conexión...")
        mt5.shutdown()
        print("✅ Conexión cerrada. Puedes apagar la máquina.")


# Ejecutar el bot
run_bot()