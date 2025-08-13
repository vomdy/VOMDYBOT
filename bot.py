import os
import re
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, ChatPermissions
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from datetime import timedelta

# Load environment variables
load_dotenv()

# 🔴 သင့်ရဲ့ User ID ကိုဒီမှာထည့်ပါ
OWNER_ID = 17827970345 # @userinfobot ကနေရယူပါ

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Warning Counter Store
user_warnings = {}

# ... (ကျန်တဲ့ code တွေကိုမထိပါနဲ့) ...

# ✅ /start Command (ပြင်ဆင်ပြီး)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        return  # ပိုင်ရှင်မဟုတ်ရင် ဘာမှမလုပ်ဘူး
    await update.message.reply_text("✅ Hello Owner! I'm your private bot.")

# ✅ Welcome Message for New Members
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.new_chat_members:
            return

        for member in update.message.new_chat_members:
            if member.id == context.bot.id:
                continue

            name = member.full_name
            username = f"@{member.username}" if member.username else "(no username)"
            user_id = member.id

            welcome_message = (
                f"မင်္ဂလာပါ {name}\n"
                f"Username - {username} ({user_id})\n\n"
                f"Voice Of Mandalay (VOM) တော်လှန်ရေးသတင်း Group မှကြိုဆိုပါတယ်။\n\n"
                f"ကျွန်တော်ကတော့ စကစကိုတော်လှန်နေတဲ့တော်လှန်‌ရေးမှာပါဝင်နေတဲ့ တော်လှန်စက်ရုပ် တစ်ကောင်ဖြစ်ပါတယ်။\n"
                f"ကျွန်တော်တို Voice Of Mandalay (VOM)တော်လှန်ရေးသတင်း Group အတွင်းဝင်ထားမည်ဆိုပါက\n\n"
                f"မိဘပြည်သူများ၏ လုံခြုံရေးအတွက် အောက်ပါအချက်များကို သတိပြုရန် လိုအပ်ပါသည်။\n\n"
                f"၁။ Profile တွင် မိမိ၏ပုံအစစ်မှန်ကို မတင်ထားရန်။\n"
                f"၂။ ဖုန်းနံပါတ်ကို ဖျောက်ထားရန်။\n"
                f"၃။ မိမိ၏တည်နေရာကို public chat သိုမဟုတ် DM တွင် မဖော်ပြရန်။"
                f"၄။ DMတွင်ဖြစ်စေ၊Groupထဲတွင်ဖြစ်စေ မိမိမသိသော Link များကို မနှိပ်မိရန်သတိထားပါ။"
                f"၅။ သတင်းပေးပိုလိုပါက admin များထံသို DM မှတစ်ဆင့် ဆက်သွယ်သတင်းပေးရန်။\n\n"
                f"မိဘပြည်သူများအနေဖြင့် -\n"
                f"• စကစ၏ ယုတ်မာရက်စက်မှုများ\n"
                f"• ဧည့်စားရင်းစစ်သတင်းများ\n"
                f"• စကစ၏ လှုပ်ရှားမှုသတင်းများ\n"
                f"• စစ်မှုထမ်းရန်ဖမ်းဆီးခေါ်ဆောင်မှုများ\n"
                f"တိုကို သတင်းပေးချင်ပါက ⤵️\n"
                f"/admin ကိုနှိပ်ပြီး သတင်းပေးပါ။"
            )

            await update.message.reply_text(welcome_message)

    except Exception as e:
        logger.error(f"Welcome error: {e}")

# ✅ Link Filter with 3-strike rule (updated)
async def filter_links(update, context):
    if not update.message or not update.message.text:
        return

    user_id = update.message.from_user.id
    username = update.message.from_user.full_name
    text = update.message.text.lower()
    if user_id == 7827970345：
     return

    # ✅ Improved pattern: detects .com, .net, .org, .top, .xyz, etc. even with spaces or hyphens
    link_pattern = r'(https?:\/\/|www\.|t\.me\/|@[a-z0-9_]{5,}|[a-z0-9\-]+\s*\.\s*[a-z]{2,10})'

    if re.search(link_pattern, text, flags=re.IGNORECASE):
        try:
            # Delete message immediately
            await update.message.delete()

            # Warn count
            user_warnings[user_id] = user_warnings.get(user_id, 0) + 1

            # Apply punishments
            if user_warnings[user_id] == 1:
                until = update.message.date + timedelta(minutes=5)
                mute_time = "5 မိနစ်"
            elif user_warnings[user_id] == 2:
                until = update.message.date + timedelta(hours=1)
                mute_time = "1 နာရီ"
            else:
                until = update.message.date + timedelta(hours=48)
                mute_time = "48 နာရီ"

            await context.bot.restrict_chat_member(
                chat_id=update.effective_chat.id,
                user_id=user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until
            )

            warn_msg = f"🚫 {username} ကို link ပို့လို့ {mute_time} mute လုပ်လိုက်ပါပြီ! ({user_warnings[user_id]}/3)"
            sent_msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=warn_msg
            )
            await asyncio.sleep(10)
            await sent_msg.delete()

        except Exception as e:
            print(f"Error deleting link: {e}")


# ✅ Group Rules Command
async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rules_text = """📜 <b>အုပ်စုစည်းမျဉ်းများ</b>:
1. လောင်းကစားကြော်ငြာများ၊ refer မပြုလုပ်ပါနဲ့။
2. Groupအတွင်းသို adminများ၏ ခွင့်ပြုချက်မရှိပဲ Link  များမပေးပိုရ ။
3. တော်လှန်ရေးနှင့်ပတ်သတ်သောအကြောင်းအရာများကို လွတ်လပ်စွာ ဆွေးနွေးနိုင်ပါသည်။
4. Group member မိဘပြည်သူများကို စိတ်အနှောက်အယှက်ဖြစ်စေသော message များ မပို့ ရ။
5. တော်လှန်ပြည်သူအချင်းချင်း စိတ်ဝမ်းကွဲစေနိုင်သော စကားများပြောဆိုခြင်းမပြု ရ။
"""
    await update.message.reply_text(rules_text, parse_mode=ParseMode.HTML)

# ✅ Admin List Command
import asyncio
from datetime import datetime, timedelta

# Dictionary to store the last usage time for each user
last_used = {}

# Admin list command with cooldown
async def admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    cooldown_time = timedelta(hours=1)  # 1 hour cooldown

    # Get current time
    current_time = datetime.now()

    # Check if user already used the command recently
    if user_id in last_used:
        time_difference = current_time - last_used[user_id]
        if time_difference < cooldown_time:
            # If the user has used the command within the last hour
            remaining_time = cooldown_time - time_difference
            await update.message.reply_text(
                f"⏳ နောက်တစ်ကြိမ်အသုံးပြုရန် {remaining_time.seconds // 60} မိနစ် {remaining_time.seconds % 60} စက္ကန့် ကြာမည်။"
            )
            return
    
    # Update the last used time
    last_used[user_id] = current_time

    predefined_admins = ["@Oakgyi1116", "@bebeex124", "@GuGuLay1234"]
    message = (
        "🔷 <b>Admin များ:</b>\n\n" +
        "\n".join([f"• {admin}" for admin in predefined_admins]) +
        "\n\nသတင်းပေးရန် ဖော်ပြထားသော admin DM ထံသို့ ဆက်သွယ်ပါ။"
    )
    await update.message.reply_text(message, parse_mode=ParseMode.HTML)


# ✅ Ban user by username or ID
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ သင့်အနေနဲ့ admin ဖြစ်ရပါမည်။")
        return

    if not context.args:
        await update.message.reply_text("အသုံးပြုနည်း: /ban <username or user_id> [အကြောင်းရင်း]")
        return

    target = context.args[0]
    reason = " ".join(context.args[1:]) if len(context.args) > 1 else "စည်းမျဉ်းချိုးမှု"

    try:
        if target.startswith("@"):
            await update.message.reply_text("❌ Username ဖြင့် ban မရပါ။ user_id သုံးပါ။")
            return
        else:
            user_id = int(target)

        await context.bot.ban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text(f"🚫 User {target} ကို Ban လုပ်ပြီးပါပြီ။\nအကြောင်းရင်း: {reason}")
    except Exception as e:
        logger.error(f"Ban error: {e}")
        await update.message.reply_text("❌ Ban လုပ်ရာတွင် အမှားတစ်ခုဖြစ်နေသည်။")

# ✅ Report User Command
async def report_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        reported_msg = update.message.reply_to_message
        if not reported_msg:
            await update.message.reply_text("⚠️ Reply ပြန်ပြီးမှ /report သုံးပါ။")
            return

        reporter = update.effective_user
        reported_user = reported_msg.from_user

        report_text = (
            f"⚠️ Report\n"
            f"👤 Reported by: {reporter.mention_html()} ({reporter.id})\n"
            f"🧾 Target: {reported_user.mention_html()} ({reported_user.id})\n\n"
            f"📄 Message:\n{reported_msg.text or 'Media'}"
        )

        admins = await context.bot.get_chat_administrators(update.effective_chat.id)
        for admin in admins:
            try:
                await context.bot.send_message(chat_id=admin.user.id, text=report_text, parse_mode=ParseMode.HTML)
            except Exception as e:
                logger.error(f"Report send error: {e}")
    except Exception as e:
        logger.error(f"Report error: {e}")

# ✅ Block forwarded messages
async def block_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message and update.message.forward_origin:
            await update.message.delete()
            warning_msg = await context.bot.send_message(
                chat_id=update.message.chat.id,
                text=f"⚠️ {update.message.from_user.mention_html()}, Group ထဲကို Forward message မပို့နိုင်ပါ။",
                parse_mode=ParseMode.HTML
            )
            await asyncio.sleep(10)
            await warning_msg.delete()
    except Exception as e:
        logger.error(f"Forward block error: {e}")

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable not set")

    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rules", rules))
    application.add_handler(CommandHandler("admin", admin_list))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("report", report_user))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), filter_links))
    application.add_handler(MessageHandler(filters.FORWARDED, block_forward))

    logger.info("🤖 Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
