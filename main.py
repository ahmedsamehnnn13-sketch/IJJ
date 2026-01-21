import telebot
import random
from datetime import datetime, timedelta
from collections import Counter

# 1. التوكن الخاص بك
BOT_TOKEN = 'YOUR_BOT_TOKEN'
bot = telebot.TeleBot(BOT_TOKEN)

matches = {}

# --- [الدستور] ---
CONSTITUTION = {
    "سكربت": "⚖️ قانون السكربت: طاقات 92 أو أقل = سكربت. الاعتراض في البداية مع دليل.",
    "عقود": "⚖️ قانون العقود: اللاعب غير المسجل = وهمي. هدفه ملغي والاعتراض خلال 10 ساعات.",
    "92": "⚖️ تنبيه: لاعب 92 سكربت صريح.",
    "تصوير": "⚖️ قانون التصوير: للأيفون فيديو (حول الجهاز + التسلسلي + الروم).",
    "خروج": "⚖️ قانون الخروج: خروج بدون دليل = تحذير ثم هدف."
}

print("--- [النظام المطور يعمل الآن] ---")

# --- [1. بدء المواجهة] ---
@bot.message_handler(func=lambda m: "VS" in m.text.upper())
def init_match(message):
    try:
        text = message.text.upper().replace("CLAN", "").replace("كلان", "")
        parts = text.split("VS")
        clan_a = parts[0].strip().split()[-1] 
        clan_b = parts[1].strip().split()[0]
        
        deadline = datetime.now() + timedelta(hours=14) 
        matches[message.chat.id] = {
            'clan_a': clan_a, 'clan_b': clan_b,
            'score_a': 0, 'score_b': 0,
            'lists': {}, 'goals': [],
            'deadline': deadline
        }
        bot.set_chat_title(message.chat.id, f"{clan_a} 0 VS 0 {clan_b}")
        bot.reply_to(message, f"🛡 **تم الاعتماد**\n🏰 {clan_a} 🆚 {clan_b}\n\n✅ سجل القائمة بـ: `قائمة {clan_a}` (رد على القائمة)")
    except: pass

# --- [2. تسجيل القوائم والقرعة - نسخة مرنة] ---
@bot.message_handler(func=lambda m: m.text and "قائمة" in m.text)
def register_list(message):
    chat_id = message.chat.id
    if chat_id not in matches or not message.reply_to_message: return
    
    data = matches[chat_id]
    text = message.text.upper()
    
    # التحقق من الكلان المذكور في الرسالة بمرونة
    target = data['clan_a'] if data['clan_a'] in text else data['clan_b'] if data['clan_b'] in text else None
    
    if target:
        lines = [l for l in message.reply_to_message.text.strip().split('\n') if l.strip()]
        if len(lines) != 6:
            bot.reply_to(message, f"❌ القائمة {len(lines)} لاعبين! لازم 6.")
            return
        
        data['lists'][target] = lines
        bot.reply_to(message, f"✅ تم اعتماد قائمة {target}")

        if len(data['lists']) == 2:
            l1, l2 = data['lists'][data['clan_a']], data['lists'][data['clan_b']]
            random.shuffle(l1); random.shuffle(l2)
            draw = "🎲 **القرعة**\n" + "\n".join([f"👤 {p1} 🆚 {p2}" for p1, p2 in zip(l1, l2)])
            bot.send_message(chat_id, draw)

# --- [3. تسجيل النقاط - نسخة مرنة] ---
@bot.message_handler(func=lambda m: m.text and "+1" in m.text)
def add_score(message):
    chat_id = message.chat.id
    if chat_id not in matches: return
    
    data = matches[chat_id]
    text = message.text.upper()
    player = message.reply_to_message.from_user.first_name if message.reply_to_message else "لاعب"

    if data['clan_a'] in text:
        data['score_a'] += 1
        data['goals'].append(player)
        target = data['clan_a']
    elif data['clan_b'] in text:
        data['score_b'] += 1
        data['goals'].append(player)
        target = data['clan_b']
    else: return

    bot.set_chat_title(chat_id, f"{data['clan_a']} {data['score_a']} VS {data['score_b']} {data['clan_b']}")
    bot.reply_to(message, f"⚽️ هدف لـ {target}! ({data['score_a']} - {data['score_b']})")

# --- [4. الألقاب - حدد] ---
@bot.message_handler(func=lambda m: "حدد" in m.text)
def finish(message):
    chat_id = message.chat.id
    if chat_id not in matches or not matches[chat_id]['goals']: 
        bot.reply_to(message, "⚠️ لم يتم تسجيل أهداف بعد!")
        return
    data = matches[chat_id]
    
    stats = Counter(data['goals'])
    scorer = stats.most_common(1)[0][0]
    clutch = data['goals'][-1]
    star = random.choice(list(stats.keys()))

    bot.reply_to(message, f"🏁 **الألقاب:**\n🥇 الهداف: {scorer}\n🌟 النجم: {star}\n🔥 الحاسم: {clutch}")
    del matches[chat_id]

# --- [5. الدستور والوقت] ---
@bot.message_handler(func=lambda m: any(word in m.text for word in CONSTITUTION.keys()))
def ai_rules(message):
    for k in CONSTITUTION:
        if k in message.text: bot.reply_to(message, CONSTITUTION[k]); break

@bot.message_handler(commands=['check'])
def check_dead(message):
    if message.chat.id in matches:
        d = matches[message.chat.id]
        if len(d['lists']) == 1: bot.reply_to(message, f"🏆 فوز إداري لـ {list(d['lists'].keys())[0]}")
        elif len(d['lists']) == 0: bot.reply_to(message, f"🎲 فوز عشوائي لـ {random.choice([d['clan_a'], d['clan_b']])}")

bot.infinity_polling()
