import base64
import datetime
import urllib.parse
import folium
import requests
import streamlit as st
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="رادار الخفجي الجيل الخامس V6.0 Ultimate", layout="centered", page_icon="🦅")
st.title("🦅 رادار الخفجي الذكي - V6.0 Falcon Dynamics Engine")

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

# --- 3. تهيئة حالات الجلسة ---
if "secure_logged_in" not in st.session_state:
    st.session_state["secure_logged_in"] = True
if "user_email" not in st.session_state:
    st.session_state["user_email"] = "alddhmshi@gmail.com"
if "crypto_key" not in st.session_state:
    st.session_state["crypto_key"] = derive_crypto_key("2087")

# --- 4. دالة أصدار الصوت التنبيهي ---
def trigger_native_audio_alert():
    sound_js = """
    <script>
    function playBeep() {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.6);
    }
    playBeep();
    </script>
    """
    st.components.v1.html(sound_js, height=0)

# --- 5. جلب بيانات الطقس ---
API_KEY = "29ea16b1dcef9de9338b290ab132c6c8" 

def get_live_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=5).json()
        return {
            "temp": response["main"]["temp"],
            "wind_speed": response["wind"]["speed"] * 3.6,
            "wind_deg": response["wind"]["deg"],
            "clouds": response["clouds"]["all"],
            "desc": response["weather"][0]["description"]
        }
    except Exception:
        return {"temp": 28.0, "wind_speed": 18.0, "wind_deg": 320, "clouds": 10, "desc": "صافي"}

def get_wind_direction_string(deg):
    if 337.5 <= deg or deg < 22.5: return "شمالي ⬇️ (شمال إلى جنوب)"
    if 22.5 <= deg < 67.5: return "شمالي شرقي ↙️"
    if 67.5 <= deg < 112.5: return "شرقي ⬅️"
    if 112.5 <= deg < 157.5: return "جنوبي شرقي ↖️"
    if 157.5 <= deg < 202.5: return "جنوبي ⬆️ (معاكس للهجرة)"
    if 202.5 <= deg < 247.5: return "جنوبي غربي ↗️"
    if 247.5 <= deg < 292.5: return "غربي ➡️"
    return "شمالي غربي ↘️"

# --- 6. الخوارزمية الذكية الشاملة لـ 24 ساعة وافتراض موقع النزول ---
def calculate_falcon_dynamics(temp, wind_speed, wind_deg, clouds, hour, month):
    # تحليل نوع الرياح بالنسبة لمسار الهجرة (من الشمال إلى الجنوب)
    is_tailwind = (wind_deg >= 315 or wind_deg <= 45) # رياح شمالية مساعدة
    is_headwind = (135 <= wind_deg <= 225)           # رياح جنوبية معاكسة

    # أ) فترة المبيت والليل (24 ساعة) - من 6 مساءً إلى 5 صباحاً
    if hour >= 18 or hour < 5:
        return 100, "🌙 **فترة مبيت واستقرار:** الطير حاط بالأرض ومستقر في الأشجار أو التلاع للمبيت حتى الشروق.", "الأشجار المرتفعة، الفياض، أو مجاري السيول المظلمة"

    # ب) تأثير الغيوم الكثيفة (انعدام الحراريات)
    if clouds >= 70:
        return 90, "☁️ **تغطية سحابية عالية:** غياب أشعة الشمس يمنع الحراريات الصاعدة، الطير يفضل النزول وعدم المجهود.", "الروابي المفتوحة والمناطق البرية المستوية"

    # ج) تأثير الرياح القوية والمواجهة
    if wind_speed > 25:
        if is_headwind:
            return 95, f"🛑 **رياح جنوبية معاكسة شديدة ({wind_speed:.1f} كم/س):** تعيق الهجرة وتسبب إجهاداً مضاعفاً، الطير حاط بالأرض حتماً.", "في ذرى الحزوم والمناطق المنخفضة المحمية من الهواء"
        elif not is_tailwind:
            return 80, f"💨 **رياح جانبية شديدة ({wind_speed:.1f} كم/س):** تجرف الطير عن مساره، مما يدفعه للنزول.", "الأشجار الكبيرة والشعاب البرية"

    # د) حساب النزول والارتفاع بناءً على الحرارة والشهور خلال النهار
    # 1. بداية الموسم / الأيام الحارة (شهر 10 / حرارة >= 30°م)
    if month == 10 or temp >= 30:
        if 8 <= hour <= 9:
            return 10, "🦅 **ذروة الارتفاع المبكر:** الحرارة عالية وتشكلت حراريات صاعدة مبكرة، الطير محلق بارتفاع عالي.", "الاعتماد على المسح بالدربيل بالسماء"
        elif 15 <= hour < 18:
            return 90, "📉 **انكسار الحرارة عصراً:** الطير ينزل مبكراً بين 3 و 6 عصراً لتفادي الحرارة والتهيؤ للمبيت.", "الأشجار البرية، المزارع المهجورة، والتلاع"
        elif hour >= 10:
            return 70, "☀️ **حرارة نهارية مرتفعة:** الطير يفضل الركون والنزول بالأرض تجنباً للإجهاد والجفاف.", "ذيل الشعاب والأماكن المظللة"

    # 2. الشهور الباردة والمعتدلة (نوفمبر وما بعده / حرارة < 30°م)
    else:
        if 9 <= hour <= 10:
            return 10, "🦅 **ذروة الارتفاع المتأخر:** الجو معتدل وتأخر تكون الحراريات، الطير يحلق بارتفاع جيد.", "مسح جوي بالسماء"
        elif 16 <= hour < 18:
            return 85, "🌆 **فترة انكسار الشمس:** النزول الطبيعي قبل الغروب (من 4 إلى 6 عصراً).", "مرتفعات الحزوم، التلاع، والشجر"

    return 30, "✨ **حركة عبور طبيعية:** الأجواء مستقرة وتسمح للطيران المنخفض والمناورة.", "مناطق العبور المفتوحة"

# --- 7. شاشة الدخول ---
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

# --- 8. الواجهة الرئيسية V6.0 ---
else:
    st.sidebar.success(f"🔓 المستكشف: {st.session_state['user_email']}")
    if st.sidebar.button("قفل النظام"):
        st.session_state["secure_logged_in"] = False
        st.rerun()

    loc = get_geolocation()
    my_lat, my_lon = (loc["coords"]["latitude"], loc["coords"]["longitude"]) if (loc and "coords" in loc) else (28.438, 48.497)

    weather = get_live_weather(my_lat, my_lon)
    wind_dir = get_wind_direction_string(weather["wind_deg"])
    now = datetime.datetime.now()
    
    landing_score, reason, landing_spot = calculate_falcon_dynamics(
        weather["temp"], 
        weather["wind_speed"], 
        weather["wind_deg"], 
        weather["clouds"], 
        now.hour, 
        now.month
    )

    # --- عرض نظام التنبيه المباشر ---
    st.markdown("### 🚨 نظام التنبيه المباشر لرصد ونزول الطيور (24 ساعة)")
    
    if landing_score >= 70:
        st.error(f"🚨 **احتمالية نزول مرتفعة جداً ({landing_score}%):**\n\n{reason}")
        st.info(f"🎯 **الموقع الافتراضي لنزول الطير حالياً:**\n\nيُتوقع وجود/نزول الطير في: **{landing_spot}**.")
    elif landing_score >= 40:
        st.warning(f"⚠️ **تنبيه متوسط ({landing_score}%):**\n\n{reason}")
    else:
        st.success(f"✅ **وضع طيران وعبور ({landing_score}%):**\n\n{reason}")

    # --- لوحة الأرصاد الجوية ---
    st.markdown("### 📊 لوحة الأرصاد الحية ومؤشرات الفيزياء الجوية")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌡️ الحرارة", f"{weather['temp']:.1f} °م")
    c2.metric("💨 الرياح", f"{weather['wind_speed']:.1f} كم/س")
    c3.metric("🧭 الاتجاه", wind_dir)
    c4.metric("☁️ الغيوم", f"{weather['clouds']}%")

    # --- إرسال تنبيه رصد/مشاهدة طير ---
    st.markdown("#### 📡 إرسال تنبيه إشارة طرح/مشاهدة طير عاجل")
    col_a, col_b = st.columns([2, 1])
    with col_a:
        bird_type = st.selectbox("نوع الطير المرصود:", ["شاهين بحري", "حر تام", "وكري", "شرياص / جلاميد", "طيور أخرى"])
    with col_b:
        st.write("")
        st.write("")
        btn_alert = st.button("📢 بث التنبيه مع الصوت")

    map_link = f"https://www.google.com/maps/search/?api=1&query={my_lat},{my_lon}"
    alert_text = f"🚨 تنبيه رصد/طرح طير!\nالنوع: {bird_type}\nالموقع: {map_link}"
    encoded_text = urllib.parse.quote(alert_text)
    whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"

    if btn_alert:
        trigger_native_audio_alert()
        st.error(f"🔔 **إشعار عاجل:** تم تسجيل رصد ({bird_type}) بالموقع بنجاح!")
        st.code(alert_text, language="markdown")
        st.markdown(f'''
            <a href="{whatsapp_url}" target="_blank" style="
                background-color: #25D366;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
                display: inline-block;
                margin-top: 5px;">📲 مشاركة التنبيه والموقع عبر الواتساب فوراً</a>
        ''', unsafe_allow_html=True)

    # --- خريطة المقناص ---
    st.markdown("### 🗺️ خريطة المقناص والمعابر الشاملة")
    all_passages = [
        {"lat": 28.0833, "lon": 48.6167, "name": "معبر رأس مشعاب (الخفجي)", "desc": "خط عبور رئيسي للشواهين البحرية"},
        {"lat": 28.4380, "lon": 48.4970, "name": "ساحل الخفجي الشمالي", "desc": "شريط ساحلي لترصد وطرح الشواهين"},
        {"lat": 28.1500, "lon": 48.5333, "name": "معبر الأبرق (غرب الخفجي)", "desc": "منطقة حجر ومأوى بري حيوية"},
        {"lat": 28.3833, "lon": 48.1667, "name": "أبرق الكبريت (غرب الخفجي)", "desc": "أرض صحراوية مرتفعة ممتازة للحرار"},
        {"lat": 27.6000, "lon": 48.4833, "name": "معبر النعيرية (وادي المياه)", "desc": "محطة مبيت ومقناص شهيرة"},
        {"lat": 30.9833, "lon": 40.5000, "name": "صحراء الحماد (عرعر)", "desc": "أشهر موقع عالمي لطرح الصقور والحرار"},
        {"lat": 20.2167, "lon": 40.0167, "name": "معبر المجيرمة (الغربية)", "desc": "موقع طرح الشواهين الشهير على البحر الأحمر"}
    ]

    m = folium.Map(location=[my_lat, my_lon], zoom_start=8, tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="Esri")
    folium.TileLayer(tiles="https://{s}.basemaps.cartocdn.com/rastertiles/voyager_only_labels/{z}/{x}/{y}{r}.png", attr="Carto", name="الأسماء", overlay=True).add_to(m)

    folium.Marker([my_lat, my_lon], popup="موقعك الحالي", icon=folium.Icon(color="blue", icon="car", prefix="fa")).add_to(m)

    for site in all_passages:
        gmaps = f"https://www.google.com/maps/dir/?api=1&destination={site['lat']},{site['lon']}"
        popup_html = f"<b>{site['name']}</b><br>{site['desc']}<br><br><a href='{gmaps}' target='_blank'>🧭 التوجيه</a>"
        folium.Marker([site["lat"], site["lon"]], popup=popup_html, icon=folium.Icon(color="red", icon="crosshairs", prefix="fa")).add_to(m)

    st_folium(m, width=700, height=450)

    # --- التشفير الجانبي ---
    cipher = Fernet(st.session_state["crypto_key"])
    encrypted_coords = cipher.encrypt(f"{my_lat},{my_lon}".encode()).decode()
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🔒 التشفير الجغرافي النشط:**")
    st.sidebar.code(encrypted_coords[:30] + "...")
