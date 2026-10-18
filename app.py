import streamlit as st
import pandas as pd
import PyPDF2
import google.generativeai as genai
import zipfile
import io

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="Balady Classification Pro", layout="wide", page_icon="🏢")

# تصميم CSS لضبط الألوان، الاتجاه، وتوقيعك الشخصي
st.markdown("""
    <style>
    .stApp { direction: rtl; text-align: right; }
    
    [data-testid="stSidebar"] { background-color: #0A365C !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* تكبير خطوط القائمة الجانبية */
    [data-testid="stSidebar"] .stRadio label {
        font-size: 1.2rem !important;
        font-weight: bold !important;
        padding-top: 10px;
    }
    
    .modar-footer {
        position: relative;
        bottom: 10px;
        width: 100%;
        text-align: center;
        font-size: 15px;
        color: #FFD700 !important;
        font-weight: bold;
        border-top: 1px solid rgba(255,255,255,0.2);
        padding-top: 15px;
        margin-top: 30px;
    }
    
    .ai-box {
        background-color: #f0f8ff;
        border-right: 4px solid #0A365C;
        padding: 15px;
        border-radius: 5px;
        margin-top: 10px;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- دوال الاستخراج الذكية -----------------
def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted: text += extracted + "\n"
    except Exception as e:
        text += f"[خطأ في قراءة PDF: {e}]\n"
    return text

def extract_text_from_excel(excel_file, filename=""):
    text = ""
    try:
        df = pd.read_excel(excel_file) if filename.endswith(('.xls', '.xlsx')) else pd.read_csv(excel_file)
        text += df.to_string() + "\n"
    except Exception as e:
        text += f"[خطأ في قراءة Excel: {e}]\n"
    return text

def process_uploaded_files(files, section_name):
    text = ""
    if files:
        text += f"\n--- مستندات {section_name} ---\n"
        for f in files:
            text += f"\n[ملف: {f.name}]\n"
            if f.name.endswith('.pdf'):
                text += extract_text_from_pdf(f)
            elif f.name.endswith(('.xlsx', '.xls', '.csv')):
                text += extract_text_from_excel(f, f.name)
    return text

def ai_analyze_section(api_key, context, prompt_instructions):
    if not api_key or not api_key.startswith("AIza"):
        st.error("❌ يرجى إدخال مفتاح Gemini صحيح في القائمة الجانبية أولاً.")
        return None
    if not context or len(context.strip()) < 10:
        st.warning("⚠️ لا توجد بيانات كافية للتحليل. يرجى إدخال البيانات أو حفظ المرفقات أولاً.")
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        prompt = f"أنت استشاري خبير ومقيم معتمد في تصنيف المقاولين في منصة 'بلدي' السعودية.\nالتعليمات: {prompt_instructions}\nالبيانات:\n{context[:100000]}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"❌ حدث خطأ في الذكاء الاصطناعي: {e}")
        return None


# ----------------- القائمة الجانبية (Navigation) -----------------
st.sidebar.title("🏢 منصة تدقيق بلدي")
st.sidebar.markdown("---")

api_key_input = st.sidebar.text_input("🔑 مفتاح الذكاء الاصطناعي:", type="password")

clients_list = [
    "--- إضافة عميل جديد ---",
    "مؤسسة زهور السماء للمقاولات",
    "شركة واحة التنمية للمقاولات العامة",
    "شركة نكسبس تاورز",
    "شركة طويق للصيانة والتشغيل",
    "مكتب قمة الابداع للاستشارات"
]
selected_client = st.sidebar.selectbox("📂 العميل الحالي:", clients_list)
st.sidebar.markdown("---")

menu_options = [
    "1️⃣ البيانات الأساسية", 
    "2️⃣ القسم القانوني", 
    "3️⃣ القسم المالي", 
    "4️⃣ الحوكمة", 
    "5️⃣ الحوكمة الائتمانية",
    "6️⃣ المشاريع",
    "📁 الرفع المتقدم (مجلد كامل)",
    "📊 التقرير النهائي (AI)"
]
selected_section = st.sidebar.radio("📋 الأقسام الرئيسية:", menu_options)

st.sidebar.markdown('<div class="modar-footer">⭐ تم التصميم من قبل مـضـر ⭐</div>', unsafe_allow_html=True)


# ----------------- الشاشة الرئيسية (تتغير حسب اختيار القائمة الجانبية) -----------------
st.title(selected_section)
st.markdown(f"**العميل النشط:** {selected_client}")
st.markdown("---")

allowed_types = ['pdf', 'xlsx', 'xls', 'csv']

if selected_section == "1️⃣ البيانات الأساسية":
    st.info("أدخل البيانات الأساسية للعميل للتحقق منها.")
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("اسم المنشأة:", value=selected_client if selected_client != "--- إضافة عميل جديد ---" else "")
        work_duration = st.text_input("مدة العمل:")
    with col2:
        cr_number = st.text_input("رقم السجل التجاري:")
        national_id = st.text_input("رقم الهوية / 700:")
    
    st.session_state.basic_info = f"العميل: {client_name}, المدة: {work_duration}, السجل: {cr_number}, الهوية: {national_id}"
    
    if st.button("✨ تحقق من صحة البيانات بالذكاء الاصطناعي"):
        result = ai_analyze_section(api_key_input, st.session_state.basic_info, "تحقق من منطقية البيانات الأساسية وهل أرقام السجلات تبدو صحيحة لمنشأة سعودية؟")
        if result: st.markdown(f'<div class="ai-box"><b>🤖 ملاحظات النظام:</b><br>{result}</div>', unsafe_allow_html=True)

elif selected_section == "2️⃣ القسم القانوني":
    st.info("ارفع المستندات القانونية. يمكنك رفع ملفات PDF أو Excel.")
    col1, col2 = st.columns(2)
    with col1:
        l1 = st.file_uploader("📑 السجل التجاري", type=allowed_types, accept_multiple_files=True)
        l2 = st.file_uploader("📑 رخصة البلدية", type=allowed_types, accept_multiple_files=True)
        l3 = st.file_uploader("📑 رخصة السكن الجماعي", type=allowed_types, accept_multiple_files=True)
    with col2:
        l4 = st.file_uploader("📑 شهادة المقاولين", type=allowed_types, accept_multiple_files=True)
        l5 = st.file_uploader("📑 التأمينات الاجتماعية", type=allowed_types, accept_multiple_files=True)
        l6 = st.file_uploader("📑 تراخيص أخرى", type=allowed_types, accept_multiple_files=True)
    
    if st.button("💾 حفظ المرفقات القانونية وقراءتها"):
        st.session_state.legal_text = process_uploaded_files(l1, "السجل") + process_uploaded_files(l2, "البلدية") + process_uploaded_files(l3, "السكن") + process_uploaded_files(l4, "المقاولين") + process_uploaded_files(l5, "التأمينات") + process_uploaded_files(l6, "أخرى")
        st.success("تم الحفظ بنجاح!")
        
    if st.button("✨ تدقيق قانوني بالذكاء الاصطناعي"):
        result = ai_analyze_section(api_key_input, st.session_state.get('legal_text', ''), "راجع المستندات المرفقة وتأكد من اكتمالها واذكر الملاحظات والنواقص لتصنيف بلدي.")
        if result: st.markdown(f'<div class="ai-box"><b>🤖 التقرير القانوني:</b><br>{result}</div>', unsafe_allow_html=True)

elif selected_section == "3️⃣ القسم المالي":
    st.info("ارفع القوائم والميزانيات المالية.")
    f1 = st.file_uploader("📊 الميزانيات المالية المعتمدة", type=allowed_types, accept_multiple_files=True)
    f2 = st.file_uploader("📈 جداول الإيرادات التفصيلية", type=allowed_types, accept_multiple_files=True)
    
    if st.button("💾 حفظ المرفقات المالية"):
        st.session_state.fin_text = process_uploaded_files(f1, "الميزانيات") + process_uploaded_files(f2, "الإيرادات")
        st.success("تم الحفظ!")
        
    if st.button("✨ تحليل مالي بالذكاء الاصطناعي"):
        result = ai_analyze_section(api_key_input, st.session_state.get('fin_text', ''), "حلل الأرقام المرفقة وتأكد من سلامة القوائم المالية وما ينقصها لرفع الدرجة المالية.")
        if result: st.markdown(f'<div class="ai-box"><b>🤖 التحليل المالي:</b><br>{result}</div>', unsafe_allow_html=True)

elif selected_section == "4️⃣ الحوكمة":
    st.info("مرفقات أنظمة الجودة والسياسات الداخلية.")
    g1 = st.file_uploader("📋 شهادات الأيزو وأنظمة ERP ولوائح الحوكمة", type=allowed_types, accept_multiple_files=True)
    
    if st.button("💾 حفظ ملفات الحوكمة"):
        st.session_state.gov_text = process_uploaded_files(g1, "الحوكمة")
        st.success("تم الحفظ!")
        
    if st.button("✨ تقييم الحوكمة بالذكاء الاصطناعي"):
        result = ai_analyze_section(api_key_input, st.session_state.get('gov_text', ''), "قيم المستندات الإدارية وشهادات الجودة، هل تكفي لنقاط الحوكمة في بلدي؟")
        if result: st.markdown(f'<div class="ai-box"><b>🤖 تقييم الحوكمة:</b><br>{result}</div>', unsafe_allow_html=True)

elif selected_section == "5️⃣ الحوكمة الائتمانية":
    st.info("مرفقات تقارير سمة والسياسات البنكية.")
    c1 = st.file_uploader("💳 تقرير سمة وخطة التعاقب والسير الذاتية", type=allowed_types, accept_multiple_files=True)
    
    if st.button("💾 حفظ ملفات الائتمان"):
        st.session_state.cred_text = process_uploaded_files(c1, "الائتمان")
        st.success("تم الحفظ!")
        
    if st.button("✨ تدقيق ائتماني ذكي"):
        result = ai_analyze_section(api_key_input, st.session_state.get('cred_text', ''), "راجع مستندات الائتمان وتقرير سمة واذكر الملاحظات بوضوح.")
        if result: st.markdown(f'<div class="ai-box"><b>🤖 التقرير الائتماني:</b><br>{result}</div>', unsafe_allow_html=True)

elif selected_section == "6️⃣ المشاريع":
    st.info("مرفقات العقود والمستخلصات لإثبات خبرة المقاول.")
    p1 = st.file_uploader("🏗️ عقود المشاريع وجداول الكميات والمستخلصات", type=allowed_types, accept_multiple_files=True)
    
    if st.button("💾 حفظ ملفات المشاريع"):
        st.session_state.proj_text = process_uploaded_files(p1, "المشاريع")
        st.success("تم الحفظ!")
        
    if st.button("✨ تقييم المشاريع بالذكاء الاصطناعي"):
        result = ai_analyze_section(api_key_input, st.session_state.get('proj_text', ''), "استخرج قائمة بالمشاريع الموجودة وقيم صحة المستخلصات والعقود.")
        if result: st.markdown(f'<div class="ai-box"><b>🤖 التدقيق الهندسي للمشاريع:</b><br>{result}</div>', unsafe_allow_html=True)

elif selected_section == "📁 الرفع المتقدم (مجلد كامل)":
    st.info("بدل رفع الملفات يدوياً في كل قسم، ارفع مجلد العميل كاملاً (بصيغة ZIP) ودع المنصة تفرزه آلياً.")
    zip_file = st.file_uploader("🗜️ ارفع ملف المجلد (ZIP)", type=['zip'])
    
    if zip_file and st.button("🚀 بدء فك الضغط والقراءة الآلية"):
        with st.spinner("جاري قراءة كافة مستندات المجلد..."):
            extracted_zip_text = ""
            try:
                with zipfile.ZipFile(zip_file, 'r') as z:
                    for filename in z.namelist():
                        if filename.startswith('__MACOSX/') or filename.endswith('/'): continue
                        with z.open(filename) as f:
                            file_bytes = io.BytesIO(f.read())
                            if filename.endswith('.pdf'):
                                extracted_zip_text += f"\n[ملف: {filename}]\n" + extract_text_from_pdf(file_bytes)
                            elif filename.endswith(('.xlsx', '.xls', '.csv')):
                                extracted_zip_text += f"\n[ملف مالي: {filename}]\n" + extract_text_from_excel(file_bytes, filename)
                st.session_state.advanced_text = extracted_zip_text
                st.success("✅ تم قراءة كافة الملفات داخل المجلد بنجاح!")
            except Exception as e:
                st.error(f"❌ حدث خطأ: {e}")
                
    if st.button("✨ فرز واكتشاف محتويات المجلد بالذكاء الاصطناعي"):
        result = ai_analyze_section(api_key_input, st.session_state.get('advanced_text', ''), "افرز هذه المستندات وصنفها إلى قانوني، مالي، ومشاريع، واذكر النواقص العامة.")
        if result: st.markdown(f'<div class="ai-box"><b>🤖 نتيجة الفرز الآلي:</b><br>{result}</div>', unsafe_allow_html=True)

elif selected_section == "📊 التقرير النهائي (AI)":
    st.header("إصدار تقرير التدقيق الشامل")
    st.info("بعد أن تنتهي من مراجعة ورفع ملفات الأقسام، اضغط هنا لاستخراج التقرير الاستشاري النهائي الخاص بمنصة بلدي.")
    
    if st.button("🚀 توليد التقرير الشامل الآن", type="primary"):
        final_context = (st.session_state.get('basic_info', '') + st.session_state.get('legal_text', '') + 
                         st.session_state.get('fin_text', '') + st.session_state.get('gov_text', '') + 
                         st.session_state.get('cred_text', '') + st.session_state.get('proj_text', '') + 
                         st.session_state.get('advanced_text', ''))
        
        with st.spinner("جاري صياغة التقرير الاستشاري الدقيق..."):
            result = ai_analyze_section(api_key_input, final_context, "بناءً على جميع البيانات المرفقة للعميل، اكتب تقريراً نهائياً شاملاً للمقاول لتجهيزه لبلدي. قسم التقرير إلى: 1. الملخص التنفيذي 2. الوضع القانوني والمالي 3. الحوكمة والمشاريع 4. التوصيات والنواقص المطلوب توفيرها بأسرع وقت.")
            if result: 
                st.success("✅ اكتمل التقرير بنجاح!")
                st.write(result)