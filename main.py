import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
from dotenv import load_dotenv

load_dotenv()

# ── ENV ──────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
BOT_TOKEN    = os.environ["BOT_TOKEN"]
ADMIN_ID     = int(os.environ["ADMIN_CHAT_ID"])

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── FASTAPI ──────────────────────────────────────────────────────────
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def base():
    rows = supabase.table("contestants").select("*").eq("visible", True).execute().data
    return {row["name"]: {"src": row["src"], "link": row["link"]} for row in rows}


# ── BOT ──────────────────────────────────────────────────────────────
ADD_NAME, ADD_SRC, ADD_LINK = range(3)
DELETE_NAME = 3
TOGGLE_NAME = 4

def is_admin(update: Update) -> bool:
    return update.effective_user.id == ADMIN_ID

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    await update.message.reply_text(
        "👑 *Мисс Лицей — Панель управления*\n\n"
        "/list — список участниц\n"
        "/add — добавить участницу\n"
        "/delete — удалить участницу\n"
        "/toggle — включить/выключить показ",
        parse_mode="Markdown"
    )

async def list_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    rows = supabase.table("contestants").select("name, visible").execute().data
    if not rows:
        await update.message.reply_text("Список пуст.")
        return
    text = "\n".join(
        f"{'✅' if r['visible'] else '❌'} {r['name']}"
        for r in rows
    )
    await update.message.reply_text(f"📋 *Участницы:*\n{text}", parse_mode="Markdown")

# ── ADD flow ─────────────────────────────────────────────────────────
async def add_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return ConversationHandler.END
    await update.message.reply_text("Введи *имя* участницы:", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    return ADD_NAME

async def add_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("Введи *ссылку на фото* (src):", parse_mode="Markdown")
    return ADD_SRC

async def add_src(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["src"] = update.message.text.strip()
    await update.message.reply_text("Введи *ссылку для QR-кода* (link):", parse_mode="Markdown")
    return ADD_LINK

async def add_link(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    name = ctx.user_data["name"]
    src  = ctx.user_data["src"]
    link = update.message.text.strip()
    supabase.table("contestants").insert({"name": name, "src": src, "link": link, "visible": True}).execute()
    await update.message.reply_text(f"✅ *{name}* добавлена!", parse_mode="Markdown")
    return ConversationHandler.END

# ── DELETE flow ───────────────────────────────────────────────────────
async def delete_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return ConversationHandler.END
    rows = supabase.table("contestants").select("name").execute().data
    if not rows:
        await update.message.reply_text("Список пуст.")
        return ConversationHandler.END
    names = [[r["name"]] for r in rows]
    await update.message.reply_text(
        "Выбери кого удалить:",
        reply_markup=ReplyKeyboardMarkup(names, one_time_keyboard=True, resize_keyboard=True)
    )
    return DELETE_NAME

async def delete_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    supabase.table("contestants").delete().eq("name", name).execute()
    await update.message.reply_text(f"🗑 *{name}* удалена.", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# ── TOGGLE flow ───────────────────────────────────────────────────────
async def toggle_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return ConversationHandler.END
    rows = supabase.table("contestants").select("name, visible").execute().data
    if not rows:
        await update.message.reply_text("Список пуст.")
        return ConversationHandler.END
    names = [[f"{'✅' if r['visible'] else '❌'} {r['name']}"] for r in rows]
    await update.message.reply_text(
        "Выбери участницу чтобы переключить показ:\n✅ — показывается  |  ❌ — скрыта",
        reply_markup=ReplyKeyboardMarkup(names, one_time_keyboard=True, resize_keyboard=True)
    )
    return TOGGLE_NAME

async def toggle_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    raw = update.message.text.strip()
    name = raw.lstrip("✅❌ ").strip()

    row = supabase.table("contestants").select("visible").eq("name", name).execute().data
    if not row:
        await update.message.reply_text("Участница не найдена.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    new_visible = not row[0]["visible"]
    supabase.table("contestants").update({"visible": new_visible}).eq("name", name).execute()

    status = "показывается ✅" if new_visible else "скрыта ❌"
    await update.message.reply_text(
        f"*{name}* теперь {status}",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# ── STARTUP ───────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    bot_app = Application.builder().token(BOT_TOKEN).build()

    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("list", list_cmd))

    bot_app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("add", add_start)],
        states={
            ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_name)],
            ADD_SRC:  [MessageHandler(filters.TEXT & ~filters.COMMAND, add_src)],
            ADD_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_link)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    ))

    bot_app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("delete", delete_start)],
        states={
            DELETE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    ))

    bot_app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("toggle", toggle_start)],
        states={
            TOGGLE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, toggle_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    ))

    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()


@app.on_event("shutdown")
async def shutdown():
    pass
