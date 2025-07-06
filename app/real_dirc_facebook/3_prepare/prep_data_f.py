import pandas as pd
import aranorm  # مكتبتك المحلية
import os ,string
import json
from pathlib import Path
base_dir = Path(__file__).resolve().parent.parent
root=str(base_dir)+ "/"

with open(root+"file_name_and_id.json", encoding="utf-8") as id_file:
    file_id = json.load(id_file)
file_name= file_id.get("file_id")

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
file_path = root + "cleaned_"+file_name+".csv"

# قراءة البيانات
df = pd.read_csv(file_path, encoding='utf-8')



if 'message' in df.columns:
    df['message'] = df['message'].apply(clean_text)
else:
    print("⚠️ العمود 'message' غير موجود في الملف.")

output_path =   root+"prepared_"+file_name+".json"
df.to_json(output_path, orient='records', force_ascii=False, indent=4)
print(f"✅ تم حفظ الملف بعد التنظيف في: {output_path}")
