import paho.mqtt.client as mqtt
import json
import time
import math
import random

# Broker Ayarları (TLS Güvenli Portu: 8883)
BROKER = "localhost"
PORT = 8883

# Renk kodları (terminal)
GREEN   = "\033[92m"
RED     = "\033[91m"
RESET   = "\033[0m"

# Geri bildirim fonksiyonları
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"{GREEN}✅ Publisher Broker'a güvenli porttan bağlandı! (Port: {PORT}){RESET}")
    else:
        print(f"{RED}❌ Publisher bağlantı hatası! Kod: {rc}{RESET}")

# 1. CLIENT NESNESİNİ OLUŞTURUYORUS
client = mqtt.Client(client_id="HospitalPublisher", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect

# 2. BAĞLANMADAN HEMEN ÖNCE TLS SERTİFİKASINI TANITIYORUZ
client.tls_set(ca_certs="certs/ca.crt")

# 3. GÜVENLİ PORT ÜZERİNDEN BAĞLANTIYI BAŞLATIYORUZ
print("🏥 Hastane Acil Servis Yayın Birimi Başlatılıyor...")
client.connect(BROKER, PORT, 60)
client.loop_start()

# Hasta Yatakları Başlangıç Değerleri
beds = {
    "bed1": {"base_hr": 75, "phase": 0.0},
    "bed2": {"base_hr": 70, "phase": 2.0},
    "bed3": {"base_hr": 85, "phase": 4.0}  # Bu yatak krize girecek
}

counter = 0

try:
    while True:
        counter += 1
        for bed_id, info in beds.items():
            # Sinüs dalgası ile doğal nabız dalgalanması simüle ediliyor
            info["phase"] += 0.1
            noise = random.uniform(-1, 1)
            
            # Senaryo: 15. saniyeden sonra Yatak 3'ün nabzı anomali gösterip fırlıyor
            if bed_id == "bed3" and counter > 15:
                # Nabız kademeli olarak 115 BPM civarına yükseliyor
                current_hr = round(info["base_hr"] + 25 + 5 * math.sin(info["phase"]) + noise, 1)
            else:
                current_hr = round(info["base_hr"] + 4 * math.sin(info["phase"]) + noise, 1)
            
            # JSON formatında paketleme
            payload = {
                "bed_id": bed_id,
                "heartrate": current_hr,
                "timestamp": time.time()
            }
            
            topic = f"hospital/{bed_id}/heartrate"
            client.publish(topic, json.dumps(payload), qos=1)
            
            if current_hr > 100:
                print(f"{RED}🚨 [YAYIN] {bed_id.upper()} Kritik Veri Gönderildi: {current_hr} BPM{RESET}")
            else:
                print(f"{GREEN}💚 [YAYIN] {bed_id.upper()} Stabil Veri Gönderildi: {current_hr} BPM{RESET}")
                
        time.sleep(1)  # Her saniye yeni ölçüm gönder

except KeyboardInterrupt:
    print(f"\n{RED}🛑 Yayın durduruldu.{RESET}")
    client.loop_stop()
    client.disconnect()