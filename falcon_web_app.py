# --- 5. شاشة المصادقة والدخول السريعة المباشرة ---
if not st.session_state["secure_logged_in"]:
    st.subheader("🔐 تسجيل الدخول ونظام حماية البر")
    
    email = st.text_input("البريد الإلكتروني", key="l_email")
    password = st.text_input("الرقم السري", type="password", key="l_pass")
    input_pin = st.text_input("رقم التشفير (PIN):", type="password", max_chars=4, key="l_pin")
    
    if st.button("تفعيل النظام القيادي"):
        email_clean = email.strip().lower()
        
        # اكتب هنا الإيميل وكلمة السر المعتمدة لديك مباشرة:
        ALLOWED_EMAIL = "alddhmshi@gmail.com"
        ALLOWED_PASS = "Khofji2026"
        ALLOWED_PIN = "2087"
        
        if email_clean == ALLOWED_EMAIL and password == ALLOWED_PASS and input_pin == ALLOWED_PIN:
            st.session_state["secure_logged_in"] = True
            st.session_state["user_email"] = email_clean
            st.session_state["crypto_key"] = derive_crypto_key(ALLOWED_PIN)
            st.success("تم الدخول بنجاح!")
            st.rerun()
        else:
            st.error("⚠️ بيانات الدخول غير صحيحة.")
