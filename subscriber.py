import paho.mqtt.client as mqtt
import json
import time

# Renk kodları (terminal)
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
CYAN    = "\033[96m"
RESET   = "\033[0m"
BOLD    = "\033[1m"

# Broker Ayarları (TLS Güvenli Portu: 8883)
BROKER = "localhost"
PORT = 8883

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"{GREEN}✅ Broker'a Başarıyla Bağlanıldı! (Port: {PORT}){RESET}")
        client.subscribe("hospital/+/heartrate")
    else:
        print(f"{RED}❌ Bağlantı Başarısız! Hata Kodu: {rc}{RESET}")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        bed = msg.topic.split('/')[1].upper()
        heartrate = data.get("heartrate", 0)
        
        if heartrate > 100:
            print(f"{RED}🚨 ACİL ALARM! [{bed}] Kritik Nabız: {heartrate} BPM!{RESET}")
        else:
            print(f"{GREEN}💚 Stabil [{bed}] Nabız: {heartrate} BPM{RESET}")
    except Exception as e:
        print(f"{YELLOW}⚠️ Veri okuma hatası: {e}{RESET}")

def on_disconnect(client, userdata, rc, properties=None):
    print(f"{YELLOW}⭕ Broker bağlantısı koptu.{RESET}")

# 1. ÖNCE CLIENT NESNESİNİ OLUŞTURUYORUZ
client = mqtt.Client(client_id="HospitalSubscriber", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

print(f"{BOLD}🏥 Hastane Acil Servis Subscriber - Başlatılıyor...{RESET}")

# 2. BAĞLANMADAN HEMEN ÖNCE TLS SERTİFİKASINI TANITIYORUZ
client.tls_set(ca_certs="certs/ca.crt")

# 3. GÜVENLİ PORT ÜZERİNDEN BAĞLANTIYI ATEŞLİYORUZ
client.connect(BROKER, PORT, 60)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print(f"\n{YELLOW}🛑 Subscriber durduruldu.{RESET}")
    client.disconnect()