import re  # مكتبة التعبيرات النمطية Regular Expressions

# (التشكيل)
TASHKEEL = re.compile(r'[\u064B-\u0652]')

# (التطويل)
TATWEEL = '\u0640'

TEH_MARBUTA = '\u0629'     # ة
ALEF_MAKSURA = '\u0649'    # ى
HEH = '\u0647'             # ه
YEH = '\u064a'             # ي

# (ألف ممدودة، ألف بهمزة فوق، تحت، إلخ)
ALEF_TYPES = re.compile(r'[\u0622\u0623\u0625\u0671\u0654\u0655]')

# (واو همزة، ياء همزة)
HAMZAT = re.compile(r'[\u0624\u0626]')
HAMZA = '\u0621'  # الهمزة الأصلية

def simple_normalize(text):
    text = text.lower()  # تحويل النص إلى أحرف صغيرة
    text = TASHKEEL.sub('', text)  # إزالة التشكيل (الفتحة، الضمة، إلخ)
    text = text.replace(TATWEEL, '')  # إزالة التطويل
    text = ALEF_TYPES.sub('ا', text)  # توحيد الألف بأنواعه إلى (ا)
    text = HAMZAT.sub(HAMZA, text)  # توحيد أنواع الهمزة إلى (ء)
    text = text.replace(TEH_MARBUTA, HEH)  # استبدال (ة) بـ (ه)
    text = text.replace(ALEF_MAKSURA, YEH)  # استبدال (ى) بـ (ي)
    text = re.sub(r"http\S+|www.\S+", '', text)  # إزالة الروابط
    text = re.sub(r'[\w\.-]+@[\w\.-]+', '', text)  # إزالة الإيميلات
    text = re.sub(r'[^\u0621-\u063A\u0641-\u064A]', ' ', text)  # إزالة كل شيء غير الحروف العربية
    text = ' '.join(text.split())  # إزالة المسافات الزائدة
    return text
