import schedule
import time
import json
import os
from dotenv import load_dotenv
from src.database import initialize_database, check_sql_server_global, register_event, last_connection
from src.alerts import send_telegram

load_dotenv()

def load_servers():
    try:
        with open('config/servers.json', 'r') as f:
            servers = json.load(f)
        
        for s in servers:
            if s['USER'] == "SQL":
                s['USER'] = os.getenv("SQL_USER")
                s['PASS'] = os.getenv("SQL_PASS")
            elif s['USER'] == "SQL2":
                s['USER'] = os.getenv("SQL2_USER")
                s['PASS'] = os.getenv("SQL2_PASS")
                
        return servers
    except FileNotFoundError:
        print("❌ Error: The file was not found config/servers.json")
        return []

def monitor():
    print(f"\n--- 🔍 Starting monitoring cycle: {time.ctime()} ---")
    servers = load_servers()
    cycle_report = [] 

    for s in servers:
        store = s['name_headquarters']
        res = check_sql_server_global(s)
        
        if res['status'] == 'ONLINE':
            # Complete record in database for history
            txt_disco_db = res['critical_disc'] if res['critical_disc'] else "OK"
            txt_log_db = res['critical_log'] if res['critical_log'] else "OK"
            register_event(store, "ONLINE", txt_disco_db, txt_log_db)
            
            # Message construction for Telegram (Only shows errors)
            if res['critical_disc'] or res['critical_log']:
                details = []
                if res['critical_disc']:
                    details.append(f"💾 Disc: {res['critical_disc']}")
                if res['critical_log']:
                    details.append(f"🔥 Log: {res['critical_log']}")
                
                line = f"⚠️ *{store}*\n" + "\n".join(details)
            else:
                line = f"✅ *{store}* | Stable"
            
            cycle_report.append(line)
        else:
            # case of fallen seridor
            last = last_connection(store)
            register_event(store, "OFFLINE", error=res['error'])
            cycle_report.append(f"🚨 *FALLEN: {store}*\n   🕒 seen: {last}")
        
        time.sleep(1)

    if cycle_report:
        date_str = time.strftime('%d/%m/%Y %H:%M:%S')
        head = f"📊 *MONITORING SUMMARY*\n📅 {date_str}\n"
        head += "───────────────────\n"
        final_message = head + "\n".join(cycle_report)
        send_telegram(final_message)

if __name__ == "__main__":
    try:
        initialize_database()
        print("✅ Initialized local databases")
    except Exception as e:
        print(f"❌ Critical error initializing DB: {e}")

    print("📡 Performing initial security check...")
    while True:
        try:
            monitor() 
            break  
        except Exception as e:
            print(f"⚠️ Initial check error (possible lack of network): {e}")
            print("🔄 Trying again in 15 seconds...")
            time.sleep(15)

    schedule.every(5).minutes.do(monitor)
    print(f"🚀 SQL-Sentinel running (Cycles every 5 min)")
    print("📌 Press Ctrl+C to stop manually")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            print(f"🔥 Unexpected error in main loop: {e}")
            time.sleep(5) 