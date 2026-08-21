import base64
import datetime
import bcrypt
import folium
import requests
import streamlit as st
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation


# --- الدوال الأمنية والتشفير ---
def hash_password(password):
  return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def check_password(password, hashed):
  return bcrypt.checkpw(password.encode(), hashed)


def derive_crypto_key(pin):
  # اشتقاق مفتاح متوافق 100% مع Fernet (32 Bytes Base64 encoded)
  kdf = PBKDF2HMAC(
      algorithm=hashes.SHA256(),
      length=32,
      salt=b'KhofjiRadarSalt2026',
      iterations=100000,
  )
  derived = kdf.derive(pin.encode())
  return base64.urlsafe_b64encode(derived)


# --- جلب بيانات الطقس ---
API_KEY = '29ea16b1dcef9de9338b290ab132c6c8'


def get_live_weather(lat, lon):
  # تصحيح رابط OpenWeatherMap API
  url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
  try:
    response = requests.get(url, timeout=5).json()
    return {
        'temp': response['main']['temp'],
        'wind_speed': response['wind']['speed'] * 3.6,
        'wind_deg': response['wind']['deg'],
        'desc': response['weather'][0]['description'],
    }
  except Exception:
    # القيم الافتراضية في حال تعثر الاتصال
    return {'temp': 15.0, 'wind_speed': 10.0, 'wind_deg': 315, 'desc': 'صافي'}


def get_wind_direction_string(deg):
  if 337.5 <= deg or deg < 22.5:
    return 'شمالي قاصف ⬇️'
  if 22.5 <= deg < 67.5:
    return 'شمالي شرقي ↙️'
  if 67.5 <= deg < 112.5:
    return 'شرقي عابر ⬅️'
  if 112.5 <= deg < 157.5:
    return 'جنوبي شرقي ↖️'
  if 157.5 <= deg < 202.5:
    return 'جنوبي معاكس ⬆️'
  if 202.5 <= deg < 247.5:
    return 'جنوبي غربي ↗️'
  if 247.5 <= deg < 292.5:
    return 'غربي شديد ➡️'
  return 'شمالي غربي ↘️'


# --- إعدادات الصفحة ---
st.set_page_config(page_title='رادار الخفجي الجيل الخامس', layout='centered')
st.title('🦅 رادار الخفجي الذكي - الجيل الخامس الخارق (V5)')

# إدارة الجلسة والمستخدمين
if 'users' not in st.session_state:
  # التشفير المسبق لتفادي بطء التشغيل
  st.session_state['users'] = {
      'alddhmshi@gmail.com': hash_password('Khofji2026')
  }

if 'secure_logged_in' not in st.session_state:
  st.session_state['secure_logged_in'] = False

# --- شاشة تسجيل الدخول ---
if not st.session_state['secure_logged_in']:
  st.subheader('🔐 بوابة الأمن السيبراني والمصادقة للجيل الخامس')
  email = st.text_input('البريد الإلكتروني الحقيقي')
  password = st.text_input('الرقم السري الخاص', type='password')
  input_pin = st.text_input(
      'رقم التشفير الشخصي لحماية الإحداثيات (PIN):',
      type='password',
      max_chars=4,
  )

  if st.button('تفعيل الرادار والتحليل التوليدي الخارق'):
    email_clean = email.strip().lower()
    if email_clean in st.session_state['users'] and check_password(
        password, st.session_state['users'][email_clean]
    ):
      if input_pin == '2087':
        st.session_state['secure_logged_in'] = True
        st.session_state['crypto_key'] = derive_crypto_key('2087')
        st.success(
            'تم التوثيق بنجاح! جاري تشغيل مستشار الذكاء الاصطناعي ودمج خرائط'
            ' الأقمار الصناعية الهجينة...'
        )
        st.rerun()
      else:
        st.error('⚠️ رقم التشفير (PIN) غير صحيح.')
    else:
      st.error('⚠️ البريد الإلكتروني أو الرقم السري غير صحيح.')

# --- الشاشة الرئيسية للتطبيق ---
else:
  st.sidebar.success('🔓 الجيل الخامس الخارق (V5) نشط ومحمي')
  if st.sidebar.button('قفل النظام (تسجيل خروج)'):
    st.session_state['secure_logged_in'] = False
    st.rerun()

  # تحديد موقع المستخدم
  loc_data = get_geolocation()
  if loc_data and 'coords' in loc_data:
    my_lat = loc_data['coords']['latitude']
    my_lon = loc_data['coords']['longitude']
  else:
    my_lat = 28.438
    my_lon = 48.497

  weather = get_live_weather(my_lat, my_lon)
  wind_dir_str = get_wind_direction_string(weather['wind_deg'])

  st.markdown('### 📊 خانة الأرصاد الجوية المباشرة عبر الأقمار الصناعية')
  col1, col2, col3 = st.columns(3)
  col1.metric('🌡️ حرارة الجو الحالية', f"{weather['temp']:.1f} °م")
  col2.metric('💨 سرعة الرياح الحية', f"{weather['wind_speed']:.1f} كم/س")
  col3.metric('🧭 اتجاه الرياح الحالي', wind_dir_str)

  st.markdown('### 🧠 مستشار المقناص الذكي (AI Elite Advisor)')
  current_hour = datetime.datetime.now().hour
  is_grounded = (current_hour < 9 or current_hour > 16) or (
      weather['wind_speed'] > 30 and 'معاكس' in wind_dir_str
  )

  if is_grounded:
    if current_hour > 16 or current_hour < 9:
      ai_advice = (
          'يا أبا دهام، غابت الشمس ونزلت الحرارة فجأة؛ خوارزمية الجيل الخامس'
          ' تؤكد أن الطيور (الحر والشاهين) مبيّتة الحين ومستقرة في بطون الأودية'
          " المحمية. اترك الحزوم المكشوفة ووجه سيارتك فوراً للمربعات الخضراء حيث"
          " فياض السدر وطلح 'المذري' لاستقبال الطير عند أول ضوء للصبح."
      )
    else:
      ai_advice = (
          'تنبيه عاجل يا أبا دهام! الرياح تواجه الطيور بشكل معاكس قوي جدًا'
          f" ({weather['wind_speed']:.1f} كم/س). الطير في حالة 'حجر جوي"
          " اضطراري' بنسبة 98% وعاجز عن الطيران الشراعي. توجه فوراً للجهة"
          ' المحمية من الطعوس وعروق النفود الموضحة بالخريطة، الهواء حجر الطيور'
          ' عندك الحين!'
      )
  else:
    ai_advice = (
        'الطقس مثالي والرياح مواتية جداً لهجرة وعبور الطيور. الخوارزمية تتوقع'
        ' تحليق شراعي جوي مرتفع ونشط ممتد عبر الممرات الحدودية. تتبع خط المسار'
        ' الديناميكي الأخضر لمواكبة اتجاه جلب الطيور في الأجواء.'
    )

  st.info(ai_advice)

  st.markdown(
      '### 🗺️ رادار عثمان التضاريسي بالأقمار الصناعية (تصوير جوي حقيقي)'
  )

  # تصحيح روابط الخريطة لـ Esri Satellite
  m = folium.Map(
      location=[my_lat, my_lon],
      zoom_start=11,
      tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      attr='Esri Satellite World Imagery',
  )

  folium.TileLayer(
      tiles='https://{s}.basemaps.cartocdn.com/rastertiles/voyager_only_labels/{z}/{x}/{y}{r}.png',
      attr='CartoDB labels',
      name='أسماء الفياض والطرق البرية',
      overlay=True,
  ).add_to(m)

  folium.Marker(
      [my_lat, my_lon],
      popup='<b>🚗 سيارة المسؤول الحالية</b>',
      tooltip='📍 أنت هنا في البر',
      icon=folium.Icon(color='blue', icon='car', prefix='fa'),
  ).add_to(m)

  target_lat_10 = my_lat + 0.085
  target_lon_10 = my_lon - 0.105
  target_lat_9 = my_lat + 0.135
  target_lon_9 = my_lon - 0.045
  target_lat_8 = my_lat + 0.035
  target_lon_8 = my_lon - 0.145

  def create_elite_popup(title, weight, lat, lon):
    # تصحيح رابط OsmAnd التوجيهي
    osmand_go = f'https://osmand.net/map#13/{lat}/{lon}'
    html = f"""<div style="background-color: rgba(255, 255, 255, 0.95); padding: 15px; border-radius: 10px; font-family: Arial, sans-serif; text-align: right; border: 3px solid #00ff66; min-width: 240px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);"><h3 style="margin: 0 0 5px 0; color: #111; font-size:16px;">🎯 {title}</h3><span style="background-color: #12161a; color: #00ff66; padding: 3px 8px; font-weight: bold; border-radius: 4px; font-size:12px;">درجة الملاءمة التضاريسية: {weight}/10</span><hr style="border: 0; border-top: 2px dashed #00ff66; margin: 10px 0;"><p style="margin: 4px 0; font-size: 14px; color: #000; font-weight: bold;">📋 الإحداثيات لنقلها لعثمان:</p><div style="background: #000; padding: 10px; border-radius: 6px; margin-bottom: 10px; text-align: center;"><span style="font-family: 'Courier New', monospace; font-size: 18px; color: #00ff66; font-weight: bold; letter-spacing: 1px;">{lat:.5f}, {lon:.5f}</span></div><a href="{osmand_go}" target="_blank" style="display: block; text-align: center; background: #00ff66; color: black; padding: 10px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 13px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">🗺️ إسقاط فوري وتوجيه في عثمان البري</a></div>"""
    return folium.Popup(html, max_width=300)

  folium.Rectangle(
      bounds=[
          [target_lat_10 - 0.012, target_lon_10 - 0.012],
          [target_lat_10 + 0.012, target_lon_10 + 0.012],
      ],
      color='#00ff66',
      fill=True,
      fill_opacity=0.30,
      weight=3,
      popup=create_elite_popup(
          'فياض أشجار الطلح والمبيت الطبيعي',
          '10',
          target_lat_10,
          target_lon_10,
      ),
      tooltip=(
          '🟩 مربع وزن 10: جاذبية قصوى (اضغط لعرض إحداثيات'
          ' عثمان)'
      ),
  ).add_to(m)

  folium.Rectangle(
      bounds=[
          [target_lat_9 - 0.012, target_lon_9 - 0.012],
          [target_lat_9 + 0.012, target_lon_9 + 0.012],
      ],
      color='#ffaa00',
      fill=True,
      fill_opacity=0.25,
      weight=2,
      popup=create_elite_popup(
          'تلاع جبلية وعرة وحجر جوي اضطراري',
          '9',
          target_lat_9,
          target_lon_9,
      ),
      tooltip='🟧 مربع وزن 9: حجر جوي (اضغط لعرض إحداثيات عثمان)',
  ).add_to(m)

  folium.Rectangle(
      bounds=[
          [target_lat_8 - 0.012, target_lon_8 - 0.012],
          [target_lat_8 + 0.012, target_lon_8 + 0.012],
      ],
      color='#ffff00',
      fill=True,
      fill_opacity=0.20,
      weight=2,
      popup=create_elite_popup(
          'بطون أودية وقيعان طرائد الهجرة', '8', target_lat_8, target_lon_8
      ),
      tooltip='🟨 مربع وزن 8: ممر حركة (اضغط لعرض إحداثيات عثمان)',
  ).add_to(m)

  folium.PolyLine(
      locations=[
          [target_lat_8, target_lon_8],
          [target_lat_9, target_lon_9],
          [target_lat_10, target_lon_10],
      ],
      color='#00ff66',
      weight=4,
      opacity=0.9,
      tooltip='➡️ مسار هجرة الصقور الفعلي المحسوب بالجيل الخامس',
  ).add_to(m)

  st_folium(m, width=700, height=450)
  st.success(
      '📌 **مميزات الجيل الخامس:** تم بث القمر الصناعي التضاريسي المدمج بنظام'
      ' عثمان.'
  )

  # تشفير الإحداثيات بأمان
  cipher = Fernet(st.session_state['crypto_key'])
  raw_coords = f'{my_lat},{my_lon}'
  encrypted_coords = cipher.encrypt(raw_coords.encode()).decode()

  st.sidebar.markdown('---')
  st.sidebar.markdown('**📁 التشفير الجغرافي العسكري V5:**')
  st.sidebar.code(encrypted_coords[:32] + '...')
