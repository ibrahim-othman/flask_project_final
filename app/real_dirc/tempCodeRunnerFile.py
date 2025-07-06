    # with open(root+new_file_name+".json", "r", encoding="utf-8") as file:
    #     raw_data = json.load(file)
    # df = pd.DataFrame(raw_data)
    # texts = df['text']
    # final_text = []
    # for text in texts:
    #     # Normalize the text
    #     text = text.lower()
    #     text = re.sub(r"http\S+|www.\S+", '', text)  # إزالة الروابط
    #     text = re.sub(r'[\w\.-]+@[\w\.-]+', '', text)  # إزالة الإيميلات
    #     text = ' '.join(text.split())  # إزالة المسافات الزائدة
    #     final_text.append(text)