import pandas as pd
import aranorm  # مكتبتك المحلية

def clean_text(text):
    if not isinstance(text, str):
        return ""

    # تحويل النص لحروف صغيرة
    text = text.lower()

    # توحيد الهمزات
    text = aranorm.normalize_hamza(text)

    # إزالة التشكيل
    text = aranorm.strip_tashkeel(text)

    # إزالة التطويل (ــــ)
    text = aranorm.strip_tatweel(text)

    # توحيد أشكال لا (ﻷ - لا)
    text = aranorm.normalize_lamalef(text)

    # إزالة underscores
    text = aranorm.remove_underscore(text)

    # إزالة علامات الترقيم
    text = aranorm.remove_all_punctuations(text)

    # استبدال الروابط بكلمة ثابتة
    text = aranorm.replace_urls(text)

    # تحويل الأرقام الشرقية للغربية (١٢٣ → 123)
    text = aranorm.convert_eastern_to_western_numerals(text)

    # إزالة أي حروف غير عربية
    text = aranorm.remove_non_arabic(text)

    # إزالة الإيموجي
    text = aranorm.remove_emojis(text)

    # حذف المسافات الزيادة
    text = aranorm.remove_extra_spaces(text)

    return text

# تعديل المسار حسب مكان ملفك
file_path = "D:/1- My syllabus/4th year/دراسة/myProject/Mahmoud proj/Grad. Project (1)/Grad. Project/cleaned_results.csv"

# قراءة البيانات
df = pd.read_csv(file_path, encoding='utf-8')



if 'message' in df.columns:
    df['message'] = df['message'].apply(clean_text)
else:
    print("⚠️ العمود 'message' غير موجود في الملف.")

output_path = "normalized_cleaned_results.json"
df.to_json(output_path, orient='records', force_ascii=False, indent=4)
print(f"✅ تم حفظ الملف بعد التنظيف في: {output_path}")
