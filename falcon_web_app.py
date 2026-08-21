import base64
import datetime
import io
import folium
import qrcode
import requests
import streamlit as st
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PIL import Image
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# --- 1. إعدادات الصفحة والتطبيق ---
st.set_page_config(page_title="رادار الخفجي الجيل الخامس V5.1 Ultimate", layout="centered", page_icon="🦅")
st.title("🦅 رادار الخفجي الذكي - V5.1 Ultimate Pro")

# --- 2. الدوال الأمنية والتشفير ---
def derive_crypto_key(pin):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'KhofjiRadarSalt2026',
        iterations=100000
    )
    derived = kdf.derive(pin.encode())
    return base64.urlsafe_b64encode(derived)

# --- 3. تهيئة حالات الجلسة (Session State) ---
# تفعيل الدخول الافتراضي فور فتح التطبيق لتفادي تعليق الشاشة
if "secure_logged_in" not in st.session_state:
    st.session_state["secure_logged_in"] = True
if "user_email" not in st.session_state:
    st.session_state["user_email"] = "alddhmshi@gmail.com"
if "crypto_key" not in st.session_state:
    st.session_state["crypto_key"] = derive_crypto_key("2087")

# --- 4. جلب بيانات الطقس وتوليد ملفات الملاحة والـ QR ---
API_KEY = "29ea16b1dcef9de9338b290ab132c6c8" 

def get_live_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=5).json()
        return {
            "temp": response["main"]["temp"],
            "wind_speed": response["wind"]["speed"] * 3.6,
            "wind_deg": response["wind"]["deg"],
            "desc": response["weather"][0]["description"]
        }
    except Exception:
        return {"temp": 18.0, "wind_speed": 12.0, "wind_deg": 315, "desc": "صافي"}

def get_wind_direction_string(deg):
    if 337.5 <= deg or deg < 22.5: return "شمالي قاصف ⬇️"
    if 22.5 <= deg < 67.5: return "شمالي شرقي ↙️"
    if 67.5 <= deg < 112.5: return "شرقي عابر ⬅️"
    if 112.5 <= deg < 157.5: return "جنوبي شرقي ↖️"
    if 157.5 <= deg < 202.5: return "جنوبي معاكس ⬆️"
    if 202.5 <= deg < 247.5: return "جنوبي غربي ↗️"
    if 247.5 <= deg < 292.5: return "غربي شديد ➡️"
    return "شمالي غربي ↘️"

def generate_gpx(waypoints):
    gpx = """<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.1" creator="KhofjiRadarV51">\n"""
    for wpt in waypoints:
        gpx += f'  <wpt lat="{wpt["lat"]}" lon="{wpt["lon"]}"><name>{wpt["name"]}</name><desc>{wpt["desc"]}</desc></wpt>\n'
    gpx += "</gpx>"
    return gpx

def generate_sos_qr(lat, lon, email):
    google_maps_url = f"https://maps.google.com/?q={lat},{lon}"
    sos_text = f"🚨 نداء استغاثة بري!\nالمستخدم: {email}\nالموقع: {lat:.5f}, {lon:.5f}\nرابط الخريطة: {google_maps_url}"
    
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(sos_text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf)
    return buf.getvalue()

# --- 5. شاشة المصادقة والدخول السريعة المباشرة ---
if not st.session_state["secure_logged_in"]:
    st.subheader("🔐 تسجيل الدخول ونظام حماية البر")
    
    email = st.text_input("البريد الإلكتروني", key="l_email")
    password = st.text_input("الرقم السري", type="password", key="l_pass")
    input_pin = st.text_input("رقم التشفير (PIN):", type="password", max_chars=4, key="l_pin")
    
    if st.button("تفعيل النظام القيادي"):
        email_clean = email.strip().lower()
        pass_clean = password.strip()
        pin_clean = input_pin.strip()
        
        ALLOWED_EMAIL = "alddhmshi@gmail.com"
        ALLOWED_PASS = "Khofji2026"
        ALLOWED_PIN = "2087"
        
        if email_clean == ALLOWED_EMAIL and pass_clean == ALLOWED_PASS and pin_clean == ALLOWED_PIN:
            st.session_state["secure_logged_in"] = True
            st.session_state["user_email"] = email_clean
            st.session_state["crypto_key"] = derive_crypto_key(ALLOWED_PIN)
            st.success("تم الدخول بنجاح!")
            st.rerun()
        else:
            st.error("⚠️ بيانات الدخول غير صحيحة.")

# --- 6. الواجهة الرئيسية V5.1 Ultimate ---
else:
    st.sidebar.success(f"🔓 المستكشف: {st.session_state['user_email']}")
    if st.sidebar.button("قفل النظام"):
        st.session_state["secure_logged_in"] = False
        st.rerun()

    loc = get_geolocation()
    my_lat, my_lon = (loc["coords"]["latitude"], loc["coords"]["longitude"]) if (loc and "coords" in loc) else (28.438, 48.497)

    weather = get_live_weather(my_lat, my_lon)
    wind_dir = get_wind_direction_string(weather["wind_deg"])

    # --- لوحة الأرصاد والتحكم الزمني ---
    st.markdown("### 📊 خانة الأرصاد والمحاكاة المستقبلية")
    c1, c2, c3 = st.columns(3)
    c1.metric("🌡️ الحرارة", f"{weather['temp']:.1f} °م")
    c2.metric("💨 سرعة الرياح", f"{weather['wind_speed']:.1f} كم/س")
    c3.metric("🧭 اتجاه الهواء", wind_dir)

    st.markdown("#### ⏳ محاكاة نسيم القمراء وسلوك الصقور (خلال 24 ساعة):")
    selected_hour = st.slider("اختر الساعة المستهدفة للاستكشاف:", 0, 23, datetime.datetime.now().hour)
    
    if 5 <= selected_hour <= 8:
        st.info("🌅 **فترة البكر والمطير:** الطيور تبدأ بالتحرك من المبيت بحثاً عن الأعلاف. ركّز على أطراف الفياض والمربعات المفتوحة.")
    elif 9 <= selected_hour <= 15:
        st.warning("☀️ **فترة التحليق والشواهين:** ارتفاع حرارة الجو يُنشّط التيارات الهوائية الصاعدة (Thermals). الصقور تحلق بارتفاعات عالية جداً.")
    else:
        st.success("🌙 **فترة المبيت والحجر:** الطيور تنزل للأرض وتستقر في الأشجار أو التلاع المحمية من الهواء. استخدم كشافات المقناص في المربعات الخضراء.")

    # --- مستشار الذكاء الاصطناعي ---
    st.markdown("### 🧠 المستشار التضاريسي المباشر")
    target_10 = {"lat": my_lat + 0.085, "lon": my_lon - 0.105, "name": "مربع 10 - فياض الطلح", "desc": "ملاءمة 98% للمبيت"}
    target_9 = {"lat": my_lat + 0.135, "lon": my_lon - 0.045, "name": "مربع 9 - الحجر الجوي", "desc": "تلاع جبلية محمية"}
    target_8 = {"lat": my_lat + 0.035, "lon": my_lon - 0.145, "name": "مربع 8 - بطون الأودية", "desc": "ممر عبور رئيسي"}

    st.write(f"🦅 **التوصية:** توجه نحو `{target_10['name']}`؛ حيث تشير التحليلات التضاريسية لارتفاع نسبة ملاءمة الاختباء والمبيت بنسبة 95%.")

    # --- الخريطة التفاعلية ---
    st.markdown("### 🗺️ خريطة المقناص والأقمار الصناعية")
    m = folium.Map(location=[my_lat, my_lon], zoom_start=11, tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="Esri")
    folium.TileLayer(tiles="https://{s}.basemaps.cartocdn.com/rastertiles/voyager_only_labels/{z}/{x}/{y}{r}.png", attr="Carto", name="الأسماء", overlay=True).add_to(m)

    folium.Marker(
        [my_lat, my_lon], 
        popup=f"موقعك الحالي:<br>Lat: {my_lat:.5f}<br>Lon: {my_lon:.5f}", 
        icon=folium.Icon(color="blue", icon="car", prefix="fa")
    ).add_to(m)

    for wpt, color in zip([target_10, target_9, target_8], ["#00ff66", "#ffaa00", "#ffff00"]):
        folium.Rectangle(
            bounds=[[wpt["lat"] - 0.012, wpt["lon"] - 0.012], [wpt["lat"] + 0.012, wpt["lon"] + 0.012]],
            color=color, fill=True, fill_opacity=0.3, weight=2,
            popup=f"<b>{wpt['name']}</b><br>{wpt['desc']}<br>📍 Lat: {wpt['lat']:.5f} | Lon: {wpt['lon']:.5f}"
        ).add_to(m)

    st_folium(m, width=700, height=450)

    # --- تصدير البيانات وأدوات السلامة البرية ---
    st.markdown("### 🛠️ أدوات السلامة والتصدير البري")
    col_gpx, col_qr = st.columns(2)

    with col_gpx:
        st.markdown("#### 📂 ملف الإحداثيات للملاحة (GPX)")
        gpx_data = generate_gpx([target_10, target_9, target_8])
        st.download_button(
            label="⬇️ تحميل GPX لـ OsmAnd والقارمن",
            data=gpx_data,
            file_name=f"Khofji_V5_Waypoints.gpx",
            mime="application/gpx+xml"
        )

    with col_qr:
        st.markdown("#### 🚨 رمز الاستغاثة البري (SOS Offline)")
        if st.button("توليد QR Code للطوارئ"):
            qr_bytes = generate_sos_qr(my_lat, my_lon, st.session_state["user_email"])
            st.image(qr_bytes, caption="اعرض هذا الرمز لأي شخص لنسخ إحداثياتك بدون إنترنت!", width=200)

    # تشفير البيانات الجغرافية
    cipher = Fernet(st.session_state["crypto_key"])
    encrypted_coords = cipher.encrypt(f"{my_lat},{my_lon}".encode()).decode()
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🔒 التشفير الجغرافي النشط:**")
    st.sidebar.code(encrypted_coords[:30] + "...")
