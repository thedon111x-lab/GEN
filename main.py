import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# Logging Setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8027675591:AAGXdGj-MbTMGRsgTVIEp-_J5xC9tCWVHz0"
ADMIN_ID = 8161638248  # Admin ID
OUTPUT_FILE = "accounts.json"
USERS_FILE = "users.json"
DEFAULT_NICK_PREFIX = "JCD"

# Target Channels & Groups Configuration
CHANNELS = [
    {
        "name": "Public Channel",
        "url": "https://t.me/JCDMODAPI",
        "chat_id": "@JCDMODAPI" # Public channel username
    },
    {
        "name": "Private Channel",
        "url": "https://t.me/+7wsrrgLqD14zYmY1",
        "chat_id": None # Force check skip (Private invite link)
    },
    {
        "name": "Private Group",
        "url": "https://t.me/+lUKPJHAEM5Y3Njg9",
        "chat_id": None # Force check skip (Private invite link)
    }
]
# =======================================================

executor = ThreadPoolExecutor(max_workers=2)


def save_user(user_id):
    """Users ko broadcast ke liye save karta hai"""
    users = set()
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                users = set(json.load(f))
        except Exception:
            users = set()

    if user_id not in users:
        users.add(user_id)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(users), f, indent=4)


def get_all_users():
    """Saare saved users ki list read karta hai"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


async def is_user_joined(bot, user_id):
    """Check karta hai ki user required public channels me joined hai ya nahi"""
    for ch in CHANNELS:
        if ch["chat_id"]:
            try:
                member = await bot.get_chat_member(chat_id=ch["chat_id"], user_id=user_id)
                if member.status in ["left", "kicked"]:
                    return False
            except Exception:
                return False
    return True


def get_join_keyboard():
    """Channels join karne ke liye 2 Upar aur 1 Neeche wala Layout with Custom Emojis"""
    keyboard = [
        # Row 1: Upar 2 Channels
        [
            InlineKeyboardButton(
                CHANNELS[0]["name"], 
                url=CHANNELS[0]["url"],
                icon_custom_emoji_id="6023660820544623088"
            ),
            InlineKeyboardButton(
                CHANNELS[1]["name"], 
                url=CHANNELS[1]["url"],
                icon_custom_emoji_id="6001449118000487326"
            )
        ],
        # Row 2: Neeche 1 Channel/Group
        [
            InlineKeyboardButton(
                CHANNELS[2]["name"], 
                url=CHANNELS[2]["url"],
                icon_custom_emoji_id="5971944878815317190"
            )
        ],
        # Row 3: Verification Button
        [
            InlineKeyboardButton(
                "✅ Verify Join", 
                callback_data="verify_join",
                icon_custom_emoji_id="6026367225466720832"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "Generate Accounts",
                callback_data="select_quantity",
                icon_custom_emoji_id="6001449118000487326",
            ),
            InlineKeyboardButton(
                "Bot Status",
                callback_data="status",
                icon_custom_emoji_id="6001440193058444284",
            ),
        ],
        [
            InlineKeyboardButton(
                "Help / Info",
                callback_data="help",
                icon_custom_emoji_id="4949560993840629085",
            ),
            InlineKeyboardButton(
                "VIP Channel",
                url="https://t.me/JCDMODAPI",
                icon_custom_emoji_id="6023660820544623088",
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_quantity_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "5 Accounts",
                callback_data="gen_5",
                icon_custom_emoji_id="6026367225466720832",
            ),
            InlineKeyboardButton(
                "10 Accounts",
                callback_data="gen_10",
                icon_custom_emoji_id="6026367225466720832",
            ),
        ],
        [
            InlineKeyboardButton(
                "20 Accounts",
                callback_data="gen_20",
                icon_custom_emoji_id="6026367225466720832",
            ),
            InlineKeyboardButton(
                "50 Accounts",
                callback_data="gen_50",
                icon_custom_emoji_id="6026367225466720832",
            ),
        ],
        [
            InlineKeyboardButton(
                "Main Menu",
                callback_data="main_menu",
                icon_custom_emoji_id="6285315214673975495",
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_keyboard():
    keyboard = [[
        InlineKeyboardButton(
            "Main Menu",
            callback_data="main_menu",
            icon_custom_emoji_id="6285315214673975495",
        )
    ]]
    return InlineKeyboardMarkup(keyboard)


def execute_generator(target_count):
    try:
        import prngen

        prngen.CONFIG["target"] = target_count
        prngen.CONFIG["threads"] = min(target_count, 10)
        prngen.CONFIG["nick_prefix"] = DEFAULT_NICK_PREFIX
        prngen.CONFIG["nick_max_len"] = 12
        prngen.CONFIG["output_file"] = OUTPUT_FILE

        prngen.load_proxies()
        prngen.run_batch()
        return True, "Success"
    except Exception as e:
        return False, str(e)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id)

    # Force Join Check
    joined = await is_user_joined(context.bot, user.id)
    if not joined:
        join_msg = (
            '<tg-emoji emoji-id="6023660820544623088">✨</tg-emoji> <b>WELCOME TO JCD VIP BOT</b> <tg-emoji emoji-id="5474143948572223102">💀</tg-emoji>\n\n'
            f"Hey <b>{user.first_name}</b> <tg-emoji emoji-id='5999337402840127790'>👋</tg-emoji>,\n\n"
            '<tg-emoji emoji-id="5420323339723881652">⚠️</tg-emoji> <b>ACCESS RESTRICTED!</b>\n'
            '<tg-emoji emoji-id="6285315214673975495">➡️</tg-emoji> Bot ko access karne ke liye niche diye gaye <b>VIP Channels</b> ko join karna mandatory hai.\n\n'
            '<tg-emoji emoji-id="6026367225466720832">⚡</tg-emoji> Saare channels join karke <b>Verify Join</b> par click karein:'
        )
        if update.message:
            await update.message.reply_text(join_msg, parse_mode="HTML", reply_markup=get_join_keyboard())
        elif update.callback_query:
            await update.callback_query.edit_message_text(join_msg, parse_mode="HTML", reply_markup=get_join_keyboard())
        return

    welcome_text = (
        f'<tg-emoji emoji-id="6001449118000487326">🦋</tg-emoji> <b>JCD VIP GEN'
        f' BOT</b> <tg-emoji emoji-id="6023660820544623088">✨</tg-emoji>\n\n'
        f"Hello, <b>{user.first_name}</b> <tg-emoji"
        ' emoji-id="5999337402840127790">🦋</tg-emoji>!\n\n'
        '<tg-emoji emoji-id="6285315214673975495">➡️</tg-emoji> Press <b>Generate'
        " Accounts</b> to start."
    )

    if update.message:
        await update.message.reply_text(
            welcome_text, parse_mode="HTML", reply_markup=get_main_keyboard()
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            welcome_text, parse_mode="HTML", reply_markup=get_main_keyboard()
        )


# ==================== ADMIN BROADCAST ====================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text(
            '<tg-emoji emoji-id="5420323339723881652">⚠️</tg-emoji> <b>Aapke paas'
            " permission nahi hai!</b>",
            parse_mode="HTML",
        )
        return

    if not context.args:
        await update.message.reply_text(
            '<tg-emoji emoji-id="5420323339723881652">⚠️</tg-emoji>'
            " <b>Usage:</b> <code>/broadcast Message</code>",
            parse_mode="HTML",
        )
        return

    broadcast_message = " ".join(context.args)
    users = get_all_users()

    if not users:
        await update.message.reply_text("❌ Koi users save nahi hain.")
        return

    status_msg = await update.message.reply_text(
        '<tg-emoji emoji-id="6282977077427702833">🎉</tg-emoji> <b>Broadcast'
        f" Shuru Ho Raha Hai...</b>\nTotal Users: <code>{len(users)}</code>",
        parse_mode="HTML",
    )

    success_count = 0
    failed_count = 0

    for uid in users:
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=(
                    '<tg-emoji emoji-id="6026367225466720832">⚡</tg-emoji> <b>ADMIN'
                    f" ANNOUNCEMENT</b>\n\n{broadcast_message}"
                ),
                parse_mode="HTML",
            )
            success_count += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed_count += 1

    await status_msg.edit_text(
        '<tg-emoji emoji-id="6023660820544623088">✨</tg-emoji> <b>Broadcast'
        " Completed!</b>\n\n🟢 Successful:"
        f" <code>{success_count}</code>\n🔴 Failed: <code>{failed_count}</code>",
        parse_mode="HTML",
    )


# ==========================================================


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = update.effective_user.id
    save_user(user_id)

    if data == "verify_join":
        joined = await is_user_joined(context.bot, user_id)
        if joined:
            await query.answer("✅ Verification successful!", show_alert=True)
            await start(update, context)
        else:
            await query.answer("❌ Aapne abhi tak public channel join nahi kiya hai!", show_alert=True)
        return

    await query.answer()

    # Double check membership before allowing menu actions
    if not await is_user_joined(context.bot, user_id):
        await start(update, context)
        return

    if data == "main_menu":
        await start(update, context)

    elif data == "select_quantity":
        await query.edit_message_text(
            '<tg-emoji emoji-id="6001440193058444284">⚙️</tg-emoji> <b>Select Account'
            " Quantity:</b>\n\n"
            f'<tg-emoji emoji-id="6285315214673975495">➡️</tg-emoji> Prefix:'
            f" <code>{DEFAULT_NICK_PREFIX}</code>\n"
            "Niche diye gaye button par click karein:",
            parse_mode="HTML",
            reply_markup=get_quantity_keyboard(),
        )

    elif data.startswith("gen_"):
        count = int(data.split("_")[1])

        await query.edit_message_text(
            '<tg-emoji emoji-id="5974235702701853774">🟠</tg-emoji>'
            f" <b>Generating {count} Accounts...</b>\n\nPlease wait...",
            parse_mode="HTML",
        )

        loop = asyncio.get_running_loop()
        success, err_msg = await loop.run_in_executor(
            executor, execute_generator, count
        )

        if success:
            if os.path.exists(OUTPUT_FILE):
                try:
                    with open(OUTPUT_FILE, "rb") as file:
                        await context.bot.send_document(
                            chat_id=user_id,
                            document=file,
                            caption=(
                                '<tg-emoji emoji-id="6282977077427702833">🎉</tg-emoji>'
                                " <b>Generated Accounts File</b>\n\n"
                                '<tg-emoji emoji-id="6226493198013830325">✍️</tg-emoji>'
                                f" <b>Prefix:</b> <code>{DEFAULT_NICK_PREFIX}</code>\n"
                                '<tg-emoji emoji-id="6026367225466720832">⚡</tg-emoji>'
                                f" <b>Quantity:</b> <code>{count}</code>"
                            ),
                            parse_mode="HTML",
                        )
                    await query.edit_message_text(
                        '<tg-emoji emoji-id="6023660820544623088">✨</tg-emoji>'
                        " <b>Completed!</b>\n\n"
                        '<tg-emoji emoji-id="5999340396432333728">🔥</tg-emoji>'
                        " <b>accounts.json</b> file aapke DM mein bhej di gayi hai!",
                        parse_mode="HTML",
                        reply_markup=get_back_keyboard(),
                    )
                except Exception as e:
                    await query.edit_message_text(
                        '<tg-emoji emoji-id="5420323339723881652">⚠️</tg-emoji>'
                        f" <b>Error:</b> <code>{str(e)}</code>",
                        parse_mode="HTML",
                        reply_markup=get_back_keyboard(),
                    )
        else:
            await query.edit_message_text(
                '<tg-emoji emoji-id="6078087767106001151">💔</tg-emoji>'
                f" <b>Failed:</b>\n<code>{err_msg[:300]}</code>",
                parse_mode="HTML",
                reply_markup=get_back_keyboard(),
            )

    elif data == "status":
        count = 0
        if os.path.exists(OUTPUT_FILE):
            try:
                with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                    data_json = json.load(f)
                    count = len(data_json)
            except Exception:
                count = 0

        users_count = len(get_all_users())
        status_text = (
            '<tg-emoji emoji-id="6001440193058444284">⚙️</tg-emoji> <b>SYSTEM'
            " STATUS</b>\n\n"
            '<tg-emoji emoji-id="6026367225466720832">⚡</tg-emoji> <b>Bot'
            " Status:</b> <code>ACTIVE</code>\n"
            '<tg-emoji emoji-id="5971944878815317190">💫</tg-emoji> <b>Total'
            f" Users:</b> <code>{users_count}</code>\n"
            '<tg-emoji emoji-id="6023660820544623088">✨</tg-emoji> <b>Accounts'
            f" File:</b> <code>{count}</code>\n"
            '<tg-emoji emoji-id="6001449118000487326">🦋</tg-emoji>'
            " <b>Delivery:</b> <code>Direct DM</code>"
        )
        await query.edit_message_text(
            status_text, parse_mode="HTML", reply_markup=get_back_keyboard()
        )

    elif data == "help":
        help_text = (
            '<tg-emoji emoji-id="4949560993840629085">🧠</tg-emoji> <b>HOW TO'
            " USE:</b>\n\n"
            "1. Click <b>Generate Accounts</b>.\n"
            "2. Select quantity (<b>5, 10, 20, 50</b>).\n"
            "3. Bot will send <b>accounts.json</b> directly to your DM."
        )
        await query.edit_message_text(
            help_text, parse_mode="HTML", reply_markup=get_back_keyboard()
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("--- BOT RUNNING WITHOUT SYNTAX ERRORS ---")
    app.run_polling()


if __name__ == "__main__":
    main()
