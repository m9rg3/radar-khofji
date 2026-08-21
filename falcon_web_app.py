import base64
import datetime
import folium
import requests
import streamlit as st
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# --- 1. إعدادات الصفحة والتطبيق ---
st.set_page_config(page_title="رادار الخفجي الجيل الخامس V5.3 Ultimate", layout="centered", page_icon="🦅")
st.title("🦅 رادار الخفجي الذكي - V5.3 Radar & Mute Controls")

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
if "secure_logged_in" not in st.session_state:
    st.session_state["secure_logged_in"] = True
if "user_email" not in st.session_state:
    st.session_state["user_email"] = "alddhmshi@gmail.com"
if "crypto_key" not in st.session_state:
    st.session_state["crypto_key"] = derive_crypto_key("2087")
if "play_sound_url" not in st.session_state:
    st.session_state["play_sound_url"] = None

# --- 4. دالة تشغيل وكتم المشغل الصوتي ---
def render_audio_player():
    if st.session_state["play_sound_url"]:
        sound_html = f"""
            <audio autoplay controls style="width: 100%;">
                <source src="{st.session_state['play_sound_url']}" type="audio/mp3">
                المتصفح لا يدعم تشغيل الصوت.
            </audio>
        """
        st.components.v1.html(sound_html, height=60)

# --- 5. جلب بيانات الطقس ودوال الحساب الجوي ---
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
        return {"temp": 18.0, "wind_speed": 22.0, "wind_deg": 315, "desc": "شمالية نشطة"}

def get_wind_direction_string(deg):
    if 337.5 <= deg or deg < 22.5: return "شمالي قاصف ⬇️"
    if 22.5 <= deg < 67.5: return "شمالي شرقي ↙️"
    if 67.5 <= deg < 112.5: return "شرقي عابر ⬅️"
    if 112.5 <= deg < 157.5: return "جنوبي شرقي ↖️"
    if 157.5 <= deg < 202.5: return "جنوبي معاكس ⬆️"
    if 202.5 <= deg < 247.5: return "جنوبي غربي ↗️"
    if 247.5 <= deg < 292.5: return "غربي شديد ➡️"
    return "شمالي غربي ↘️"

def calculate_landing_probability(wind_speed, hour):
    score = 0
    if wind_speed > 20: score += 40
    if wind_speed > 35: score += 30
    if 5 <= hour <= 7 or 16 <= hour <= 18: score += 30
    return min(score, 100)

def generate_gpx(waypoints):
    gpx = """<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.1" creator="KhofjiRadarV53">\n"""
    for wpt in waypoints:
        gpx += f'  <wpt lat="{wpt["lat"]}" lon="{wpt["lon"]}"><name>{wpt["name"]}</name><desc>{wpt["desc"]}</desc></wpt>\n'
    gpx += "</gpx>"
    return gpx

# --- 6. شاشة المصادقة والدخول ---
if not st.session_state["secure_logged_in"]:
    st.subheader("🔐 تسجيل الدخول ونظام حماية البر")
    email = st.text_input("البريد الإلكتروني", key="l_email")
    password = st.text_input("الرقم السري", type="password", key="l_pass")
    input_pin = st.text_input("رقم التشفير (PIN):", type="password", max_chars=4, key="l_pin")
    
    if st.button("تفعيل النظام القيادي"):
        if email.strip().lower() == "alddhmshi@gmail.com" and password.strip() == "Khofji2026" and input_pin.strip() == "2087":
            st.session_state["secure_logged_in"] = True
            st.session_state["user_email"] = email.strip().lower()
            st.session_state["crypto_key"] = derive_crypto_key("2087")
            st.success("تم الدخول بنجاح!")
            st.rerun()
        else:
            st.error("⚠️ بيانات الدخول غير صحيحة.")

# --- 7. الواجهة الرئيسية V5.3 ---
else:
    st.sidebar.success(f"🔓 المستكشف: {st.session_state['user_email']}")
    if st.sidebar.button("قفل النظام"):
        st.session_state["secure_logged_in"] = False
        st.rerun()

    loc = get_geolocation()
    my_lat, my_lon = (loc["coords"]["latitude"], loc["coords"]["longitude"]) if (loc and "coords" in loc) else (28.438, 48.497)

    weather = get_live_weather(my_lat, my_lon)
    wind_dir = get_wind_direction_string(weather["wind_deg"])
    current_hour = datetime.datetime.now().hour
    landing_score = calculate_landing_probability(weather["wind_speed"], current_hour)

    # --- نظام التنبيهات المباشر (BIRD LANDING ALERT) ---
    st.markdown("### 🚨 نظام التنبيهات المباشر لرصد ونزول الطيور")
    
    if landing_score >= 70:
        st.error(f"🚨 **تنبيه عالي (احتمالية نزول الطيور {landing_score}%):** الأحوال الجوية (سرعة الرياح {weather['wind_speed']:.1f} كم/س) والوقت الحالي يشيران إلى ترجيح نزول وحطّ الصقور والطيور المهاجرة في الأشجار والفياض!")
    elif landing_score >= 40:
        st.warning(f"⚠️ **تنبيه متوسط (احتمالية نزول الطيور {landing_score}%):** حركة عبور نشطة، يُنصح بمراقبة العوالق والتلاع المفتوحة.")
    else:
        st.success(f"✅ **الوضع هادئ (احتمالية النزول {landing_score}%):** الطيور في حالة تحليق عالي أو عبور مستمر.")

    # --- لوحة الأرصاد والتحكم الزمني ---
    st.markdown("### 📊 خانة الأرصاد والمحاكاة المستقبلية")
    c1, c2, c3 = st.columns(3)
    c1.metric("🌡️ الحرارة", f"{weather['temp']:.1f} °م")
    c2.metric("💨 سرعة الرياح", f"{weather['wind_speed']:.1f} كم/س")
    c3.metric("🧭 اتجاه الهواء", wind_dir)

    # --- زر التنبيه الفوري عند مشاهدة طير ---
    st.markdown("#### 📡 إرسال تنبيه إشارة طرح/مشاهدة طير عاجل")
    col_a, col_b = st.columns([2, 1])
    with col_a:
        bird_type = st.selectbox("نوع الطير المرصود:", ["شاهين بحري", "حر تام", "وكري", "شرياص / جلاميد", "طيور أخرى"])
    with col_b:
        if st.button("📢 بث التنبيه"):
            map_link = f"https://www.google.com/maps/search/?api=1&query={my_lat},{my_lon}"
            alert_msg = f"🚨 **تنبيه رصد طير!**\nالنوع: {bird_type}\nالموقع: {map_link}"
            st.code(alert_msg, language="markdown")
            st.success("تم تجهيز التنبيه! يمكنك نسخته وإرساله فوراً.")

    # --- قاعدة بيانات المعابر ---
    all_passages = [
        {"lat": 28.0833, "lon": 48.6167, "name": "معبر رأس مشعاب (الخفجي)", "desc": "خط عبور رئيسي للشواهين البحرية"},
        {"lat": 28.4380, "lon": 48.4970, "name": "ساحل الخفجي الشمالي", "desc": "شريط ساحلي لترصد وطرح الشواهين"},
        {"lat": 28.1500, "lon": 48.5333, "name": "معبر الأبرق (غرب الخفجي)", "desc": "منطقة حجر ومأوى بري حيوية"},
        {"lat": 28.3833, "lon": 48.1667, "name": "أبرق الكبريت (غرب الخفجي)", "desc": "أرض صحراوية مرتفعة ممتازة للحرار"},
        {"lat": 27.6000, "lon": 48.4833, "name": "معبر النعيرية (وادي المياه)", "desc": "محطة مبيت ومقناص شهيرة"},
        {"lat": 30.9833, "lon": 40.5000, "name": "صحراء الحماد (عرعر)", "desc": "أشهر موقع عالمي لطرح الصقور والحرار"},
        {"lat": 20.2167, "lon": 40.0167, "name": "معبر المجيرمة (الغربية)", "desc": "موقع طرح الشواهين الشهير على البحر الأحمر"}
    ]

    # --- الخريطة التفاعلية ---
    st.markdown("### 🗺️ خريطة المقناص والمعابر الشاملة")
    m = folium.Map(location=[my_lat, my_lon], zoom_start=8, tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="Esri")
    folium.TileLayer(tiles="https://{s}.basemaps.cartocdn.com/rastertiles/voyager_only_labels/{z}/{x}/{y}{r}.png", attr="Carto", name="الأسماء", overlay=True).add_to(m)

    folium.Marker([my_lat, my_lon], popup="موقعك الحالي", icon=folium.Icon(color="blue", icon="car", prefix="fa")).add_to(m)

    for site in all_passages:
        gmaps = f"https://www.google.com/maps/dir/?api=1&destination={site['lat']},{site['lon']}"
        popup_html = f"<b>{site['name']}</b><br>{site['desc']}<br><br><a href='{gmaps}' target='_blank'>🧭 التوجيه</a>"
        folium.Marker([site["lat"], site["lon"]], popup=popup_html, icon=folium.Icon(color="red", icon="crosshairs", prefix="fa")).add_to(m)

    st_folium(m, width=700, height=450)

    # --- مكتبة الأصوات والتصدير مع خيار الكتم ---
    st.markdown("### 🛠️ الملاحة البرية والمؤثرات الصوتية")
    col_gpx, col_sound = st.columns(2)

    with col_gpx:
        st.markdown("#### 📂 ملف الإحداثيات للملاحة (OsmAnd / Garmin)")
        st.download_button(
            label="⬇️ تحميل GPX لجميع المعابر",
            data=generate_gpx(all_passages),
            file_name="Khofji_Passages.gpx",
            mime="application/gpx+xml"
        )

    with col_sound:
        st.markdown("#### 🔊 مكتبة أصوات البر والتحكم بالصوت")
        sound_choice = st.selectbox("اختر الصوت المراد تشغيله:", [
            "🔊 صفارة طوارئ وإنذار عالي (SOS Warning Siren)",
            "🦅 أصوات حداء وتغاريد طيور برية",
            "📢 نداء استجذاب وتدريب صقور"
        ])
        
        btn_play, btn_mute = st.columns(2)
        
        with btn_play:
            if st.button("▶️ تشغيل الصوت"):
                if "صفارة" in sound_choice:
                    st.session_state["play_sound_url"] = "https://www.soundjay.com/buttons/sounds/beep-07a.mp3"
                elif "تغاريد" in sound_choice:
                    st.session_state["play_sound_url"] = "https://www.soundjay.com/nature/sounds/birds-1.mp3"
                else:
                    st.session_state["play_sound_url"] = "https://www.soundjay.com/nature/sounds/eagle-cry-1.mp3"
                st.rerun()

        with btn_mute:
            if st.button("🔇 كتم الصوت / إيقاف"):
                st.session_state["play_sound_url"] = None
                st.success("تم كتم الصوت.")
                st.rerun()

        # عرض مشغل الصوت إذا كان مفعلاً
        render_audio_player()

    cipher = Fernet(st.session_state["crypto_key"])
    encrypted_coords = cipher.encrypt(f"{my_lat},{my_lon}".encode()).decode()
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🔒 التشفير الجغرافي النشط:**")
    st.sidebar.code(encrypted_coords[:30] + "...")
