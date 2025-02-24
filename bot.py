import pandas as pd
import nest_asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
from rapidfuzz import process, fuzz

# تحميل بيانات الأسئلة الشائعة
file_path = "/content/university_faq (2).xlsx"
df = pd.read_excel(file_path)
faq_dict = dict(zip(df["السؤال"], df["الإجابة"]))

# تصنيفات لتحديد مستوى الطالب
categories = {
    "مستجد": ["التسجيل", "القبول", "متى يبدأ التقديم", "متى يفتح التسجيل", "كيف اسجل"],
    "تحضيري": ["السنة التحضيرية", "التحضيري صعب", "اللغة الإنجليزية", "مواد التحضيري"],
    "متقدم": ["التدريب", "التخرج", "مشروع التخرج", "وظائف للخريجين", "سوق العمل"]
}

# معرف المسؤول في تليجرام (استبدله بمعرفك)
ADMIN_ID = 5119712235  # ضع معرفك هنا

# البحث عن السؤال الأقرب بنسبة 80% وتحديد مستوى الطالب
def find_best_match(user_question):
    user_question = user_question.lower().strip()
    match = process.extractOne(user_question, faq_dict.keys(), scorer=fuzz.WRatio)

    # تحديد المستوى بناءً على الكلمات
    student_level = "غير محدد 🤔"
    for level, keywords in categories.items():
        if any(word in user_question for word in keywords):
            student_level = level
            break

    # التحقق من وجود تطابق قبل استخدامه
    if match and match[1] >= 80:
        best_match = match[0]
        return f"{faq_dict[best_match]}\n\n📌 *توقعي أنك طالب:* {student_level} 🎓"

    return "❌ المعذرة، ما فهمت سؤالك. حاول تصيغه بطريقة ثانية أو راجع موقع الجامعة."

# وظيفة الرد على الأسئلة وإرسال نسخة للمسؤول
async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text.strip()
    chat_id = update.message.chat_id  # معرف المستخدم
    response = find_best_match(user_message)

    # إرسال الرد للمستخدم
    await update.message.reply_text(response, parse_mode="Markdown")

    # إرسال نسخة من الرسالة للمسؤول (مدير البوت)
    admin_message = f"📩 رسالة جديدة من {chat_id}:\n\n{user_message}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)

# تشغيل البوت
TOKEN = "7747811357:AAFAc7oaNIHhzzMvA8U0BQTejO6OtC6GCXY"
app = Application.builder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

nest_asyncio.apply()

print("✅ البوت يعمل الآن... 🤖🔥")
app.run_polling()
