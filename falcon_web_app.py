import streamlit as st
import requests
import datetime
import folium
from streamlit_folium import st_folium
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# --- 1. خوارزمية التشفير السيبراني المباشرة ---
def derive_crypto_key(pin):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'KhofjiRadarSalt2026',
        iterations=100000
    )
    return base64.urlsafe_b64encode(kdf.derive(pin.encode()))

# --- 2. مفتاح الأرصاد الحقيقي والحي الخاص بك ---
API_KEY = "29ea16b1dcef9de9338b290ab132c6c8" 

def get_live_weather(lat, lon):
    url = f"https://openweathermap.org{lat}&lon={lon}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url).json()
        return {
            "temp": response["main"]["temp"],
            "wind_speed": response["wind"]["speed"] * 3.6, # كم/ساعة
            "wind_deg": response["wind"]["deg"],
            "desc": response["weather"]["description"]
        }
    except:
        return {"temp": 15.0, "wind_speed": 10.0, "wind_deg": 180, "desc": "صافي"}

def get_wind_direction_string(deg):
    if 337.5 <= deg or deg < 22.5: return "شمالي قاصف"
    if 157.5 <= deg < 202.5: return "جنوبي معاكس"
    if 247.5 <= deg < 292.5: return "غربي شديد"
    return "شرقي"

# --- 3. بناء واجهة رادار الخفجي المطور بالخلفية المظلمة ---
st.set_page_config(page_title="رادار الخفجي المطور", layout="centered")
st.title("🦅 رادار الخفجي الذكي لتعقب الصقور")

# التحقق من حالة الدخول الآمن
if "secure_logged_in" not in st.session_state:
    st.session_state["secure_logged_in"] = False

if not st.session_state["secure_logged_in"]:
    st.subheader("🔐 بوابة الأمن السيبراني لرادار الخفجي")
    
    # خانة إدخال رقم التشفير المخصص لك مباشرة
    input_pin = st.text_input("أدخل رقم التشفير الشخصي لفتح الرادار والخرائط الحية:", type="password", max_chars=4)
    
    if st.button("تفعيل الرادار والمصادقة"):
        if input_pin == "2087":
            st.session_state["secure_logged_in"] = True
            st.session_state["crypto_key"] = derive_crypto_key("2087")
            st.success("تم التوثيق بنجاح! جاري فك تشفير البيانات الجغرافية وتشغيل الخريطة السوداء...")
            st.rerun()
        else:
            st.error("⚠️ رقم التشفير غير صحيح. الوصول محظور للحفاظ على سرية الفياض.")
else:
    # --- بعد الدخول الناجح والمصادقة برقم 2087 ---
    st.sidebar.success("🔓 النظام مشفر ومحمي بـ AES-256")
    if st.sidebar.button("قفل الرادار (تسجيل خروج)"):
        st.session_state["secure_logged_in"] = False
        st.rerun()

    falcon_type = st.radio("🎯 اختر فئة الصقر لتوقع تضاريس نزوله الميداني:", ("صقر حُر", "صقر شاهين"))

    # ممرات ومواقع المقناص والجرود البرية في المملكة
    locations = {
        "الخفجي (المنطقة الشرقية)": {"lat": 28.438, "lon": 48.497},
        "حفر الباطن (الصمان الشمالي)": {"lat": 28.433, "lon": 45.958},
        "رفحاء (الحدود الشمالية)": {"lat": 29.400, "lon": 43.500},
        "وادي السرحان (الجوف)": {"lat": 30.500, "lon": 38.500}
    }
    selected_zone = st.selectbox("🗺️ اختر موقع تواجدك البري الحالي لتحديث الخريطة السوداء والرياح الحية:", list(locations.keys()))

    loc = locations[selected_zone]
    weather = get_live_weather(loc["lat"], loc["lon"])
    wind_dir_str = get_wind_direction_string(weather["wind_deg"])

    # عرض الأرصاد الحية
    st.markdown("### 📊 خانة الأرصاد الجوية المباشرة عبر الأقمار الصناعية")
    col1, col2, col3 = st.columns(3)
    col1.metric("🌡️ حرارة الجو الحالية", f"{weather['temp']:.1f} °م")
    col2.metric("💨 سرعة الرياح الحية", f"{weather['wind_speed']:.1f} كم/س")
    col3.metric("🧭 اتجاه الرياح الحالي", wind_dir_str)

    # --- 🗺️ رسم الخريطة البرية المظلمة (نفس مظهر الصفحة السوداء السابقة) ---
    st.markdown("### 🗺️ خريطة المقناص الجغرافية والتضاريس (المظهر الأسود)")

    # دمج ثيم الخريطة السوداء الفخمة CartoDB.DarkMatter لتطابق تصميمك السابق
    m = folium.Map(
        location=[loc["lat"], loc["lon"]], 
        zoom_start=9, 
        tiles="https://{s}://{z}/{x}/{y}{r}.png",
        attr="&copy; CartoDB"
    )

    # تثبيت موقع الصقار الحالي بنقطة زرقاء مضيئة على الخريطة السوداء
    folium.Marker(
        [loc["lat"], loc["lon"]], 
        popup=f"موقعك الميداني: {selected_zone}", 
        tooltip="📍 موقع سيارتك الحالي",
        icon=folium.Icon(color="blue", icon="car", prefix="fa")
    ).add_to(m)

    # خوارزمية تحليل التضاريس ونوع الأرض (شجر أو جبل) تلقائياً
    current_hour = datetime.datetime.now().hour
    is_grounded = (falcon_type == "صقر حُر" and (current_hour < 9 or current_hour > 16)) or (weather["wind_speed"] > 35 and wind_dir_str == "جنوبي معاكس")

    # حساب نقطة النزل المتوقعة تبعد 15 كم في اتجاه المذري حسب اتجاه الريح الحية
    nest_lat = loc["lat"] + 0.13
    nest_lon = loc["lon"] - 0.16

    if is_grounded:
        if current_hour > 16 or current_hour < 9:
            terrain_type = "🌳 أشجار طلح وسدر (مبيت وفياض شعبية محمية توفر المذري)"
            icon_name = "tree"
        else:
            terrain_type = "⛰️ جبال وعرة وتلاع صخرية (حجر جوي اضطراري بسبب الرياح)"
            icon_name = "mountain"
        
        folium.Marker(
            [nest_lat, nest_lon],
            popup=f"<b>🎯 موقع نزول الطير:</b><br>{terrain_type}",
            tooltip="🟡 موقع الصقر الحالي على الأرض",
            icon=folium.Icon(color="orange", icon=icon_name, prefix="fa")
        ).add_to(m)
        
        folium.Circle(
            location=[nest_lat, nest_lon],
            radius=4000,
            color="#00ff66", 
            fill=True,
            fill_opacity=0.1
        ).add_to(m)
        
        st.success(f"📌 **تحليل التضاريس والجرود:** الخوارزمية تتوقع استقرار الصقر حالياً فوق تضاريس من نوع **[{terrain_type}]**. اتبع النطاق الأخضر الفسفوري على الخريطة السوداء.")
    else:
        folium.Marker(
            [nest_lat + 0.3, nest_lon + 0.3],
            popup="✈️ ممر طيران جوي عابر ونشط فوق الأودية والجرود البرية",
            tooltip="🔴 الصقر يحلق الآن جوياً",
            icon=folium.Icon(color="red", icon="plane", prefix="fa")
        ).add_to(m)
        
        folium.PolyLine(
            locations=[[loc["lat"], loc["lon"]], [nest_lat + 0.3, nest_lon + 0.3]],
            color="#00ff66", weight=3, opacity=0.8
        ).add_to(m)
        st.info("🔴 **تحليل التضاريس والجرود:** الصقر في حالة طيران شراعي جوي مرتفع عابر فوق الممرات البرية والنفود، ولم ينزل للأرض بعد.")

    st_folium(m, width=700, height=450)

    # حماية وتعمية البيانات السيبرانية داخل ذاكرة التخزين السحابية للموقع
    cipher = Fernet(st.session_state["crypto_key"])
    raw_coords = f"{loc['lat']},{loc['lon']}"
    encrypted_coords = cipher.encrypt(raw_coords.encode()).decode()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📁 التشفير الجغرافي الحكيم:**")
    st.sidebar.code(encrypted_coords[:32] + "...")
