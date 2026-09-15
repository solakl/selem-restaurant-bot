import os
import random
import datetime
import logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    BotCommand, BotCommandScopeDefault
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    CallbackQueryHandler, ContextTypes
)
from telegram.constants import ParseMode

# ==================== LOGGING ====================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== CONFIG ====================
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8663191953:AAG2ygZFsjlhZOfQN9jy4SAOsfBkSvY3x24")
IMAGES_FOLDER = "/home/akl/Desktop/imagebot"
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")
PORT = int(os.environ.get("PORT", 8000))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")

# ==================== MENU DATA ====================
MENU = {
    "featured": {"name": "🔥 Featured Today", "icon": "🔥", "items": {}},
    "traditional": {
        "name": "Traditional Ethiopian",
        "icon": "🇪🇹",
        "items": {
            "injera":      {"price": 30,  "description": "Traditional sourdough flatbread", "icon": "🥘", "prep": "5 min"},
            "doro_wat":    {"price": 250, "description": "Spicy chicken stew with boiled egg", "icon": "🍗", "prep": "25 min"},
            "tibs":        {"price": 200, "description": "Sautéed beef with onions and peppers", "icon": "🥩", "prep": "20 min"},
            "shiro":       {"price": 120, "description": "Chickpea stew with spices", "icon": "🍲", "prep": "15 min"},
            "kitfo":       {"price": 280, "description": "Ethiopian minced raw beef with spices", "icon": "🥩", "prep": "10 min"},
            "beyaynetu":   {"price": 180, "description": "Vegetarian platter with various dishes", "icon": "🥗", "prep": "15 min"},
            "misir_wat":   {"price": 140, "description": "Spicy red lentil stew", "icon": "🍛", "prep": "20 min"},
            "gomen":       {"price": 100, "description": "Collard greens with spices", "icon": "🥬", "prep": "15 min"},
            "key_wat":     {"price": 220, "description": "Spicy beef stew", "icon": "🍖", "prep": "25 min"},
            "ayib":        {"price": 80,  "description": "Ethiopian cottage cheese", "icon": "🧀", "prep": "5 min"},
        }
    },
    "fast_food": {
        "name": "Fast Food",
        "icon": "🍔",
        "items": {
            "burger":        {"price": 150, "description": "Classic beef burger with fries", "icon": "🍔", "prep": "15 min"},
            "pizza_slice":   {"price": 80,  "description": "Cheese pizza slice", "icon": "🍕", "prep": "10 min"},
            "french_fries":  {"price": 60,  "description": "Crispy golden fries", "icon": "🍟", "prep": "8 min"},
            "chicken_wings": {"price": 180, "description": "Spicy chicken wings (6 pcs)", "icon": "🍗", "prep": "18 min"},
            "samosa":        {"price": 50,  "description": "Fried pastry with meat filling", "icon": "🥟", "prep": "10 min"},
        }
    },
    "drinks": {
        "name": "Drinks & Beverages",
        "icon": "🥤",
        "items": {
            "coca_cola": {"price": 40, "description": "Coca-Cola 500ml", "icon": "🥤", "prep": "1 min"},
            "fanta":     {"price": 40, "description": "Fanta Orange 500ml", "icon": "🍊", "prep": "1 min"},
            "sprite":    {"price": 40, "description": "Sprite 500ml", "icon": "🥤", "prep": "1 min"},
            "water":     {"price": 20, "description": "Bottled water 500ml", "icon": "💧", "prep": "1 min"},
            "juice":     {"price": 60, "description": "Fresh fruit juice", "icon": "🧃", "prep": "5 min"},
            "coffee":    {"price": 50, "description": "Ethiopian coffee", "icon": "☕", "prep": "5 min"},
            "tea":       {"price": 30, "description": "Traditional tea", "icon": "🍵", "prep": "3 min"},
        }
    },
    "desserts": {
        "name": "Desserts",
        "icon": "🍰",
        "items": {
            "cake_slice":  {"price": 100, "description": "Chocolate cake slice", "icon": "🍰", "prep": "3 min"},
            "ice_cream":   {"price": 80,  "description": "Vanilla ice cream", "icon": "🍦", "prep": "2 min"},
            "fruit_salad": {"price": 90,  "description": "Fresh fruit salad", "icon": "🍓", "prep": "5 min"},
        }
    },
    "services": {
        "name": "Services & Support",
        "icon": "💎",
        "items": {
            "call_admin":       {"price": 0, "description": "Get admin phone number", "icon": "📞", "prep": "-"},
            "telegram_support": {"price": 0, "description": "Chat directly with admin", "icon": "💬", "prep": "-"},
        }
    }
}

DAILY_SPECIALS = {
    "monday":    {"item": "doro_wat_featured", "name": "Doro Wat + Extra Injera", "price": 200, "desc": "🔥 Monday Only - Save 50 ETB!", "icon": "🍗"},
    "tuesday":   {"item": "tibs_featured",     "name": "Tibs + Free Juice",       "price": 220, "desc": "🔥 Tuesday Special!",       "icon": "🥩"},
    "wednesday": {"item": "beyaynetu_featured","name": "Beyaynetu Veggie Platter","price": 150, "desc": "🔥 Wednesday - Save 30 ETB!","icon": "🥗"},
    "thursday":  {"item": "burger_featured",   "name": "Double Burger + Fries",   "price": 180, "desc": "🔥 Thursday Deal!",         "icon": "🍔"},
    "friday":    {"item": "fish_featured",     "name": "Fried Fish + Gomen",      "price": 250, "desc": "🔥 Friday Special!",        "icon": "🐟"},
    "saturday":  {"item": "kitfo_featured",    "name": "Kitfo + Ayib",            "price": 300, "desc": "🔥 Saturday - Save 20 ETB!", "icon": "🥩"},
    "sunday":    {"item": "family_doro",       "name": "Family Doro Wat (4 ppl)", "price": 800, "desc": "🔥 Sunday Family Deal!",    "icon": "👨‍👩‍👧‍👦"}
}

RESTAURANT_INFO = {
    "name": "Selem Restaurant",
    "tagline": "Authentic Ethiopian Cuisine Since 2010",
    "address": "Bahir Dar, Ethiopia",
    "phone": "+251965895552",
    "hours": "Mon-Sun: 10:00 AM - 11:00 PM",
    "telegram": "https://t.me/Amen365",
    "facebook": "https://facebook.com",
    "email": "info@selemethiopian.com",
    "cbe_account": "1000123456789",
    "telebirr_number": "0965895552",
    "admin_telegram": "https://t.me/Amen365",
    "rating": "4.9 ⭐ (2,340 reviews)"
}

# ==================== STORAGE ====================
user_orders = {}
users_sending_receipt = {}

# ==================== HELPERS ====================
def get_featured_item():
    today = datetime.datetime.now().strftime("%A").lower()
    special = DAILY_SPECIALS.get(today)
    if special:
        return {
            special["item"]: {
                "price": special["price"],
                "description": special["desc"],
                "name": special["name"],
                "icon": special["icon"],
                "prep": "20 min"
            }
        }
    return {}

def get_item_price(category, item):
    if category == "featured":
        return get_featured_item().get(item, {}).get("price", 0)
    return MENU.get(category, {}).get("items", {}).get(item, {}).get("price", 0)

def get_item_name(category, item):
    if category == "featured":
        return get_featured_item().get(item, {}).get("name", item.replace("_", " ").title())
    return item.replace("_", " ").title()

def get_item_icon(category, item):
    if category == "featured":
        return get_featured_item().get(item, {}).get("icon", "⭐")
    return MENU.get(category, {}).get("items", {}).get(item, {}).get("icon", "🍽️")

def get_item_prep(category, item):
    if category == "featured":
        return get_featured_item().get(item, {}).get("prep", "20 min")
    return MENU.get(category, {}).get("items", {}).get(item, {}).get("prep", "-")

def get_item_desc(category, item):
    if category == "featured":
        return get_featured_item().get(item, {}).get("description", "")
    return MENU.get(category, {}).get("items", {}).get(item, {}).get("description", "")

def format_price(price):
    return f"{price} ETB" if price > 0 else "FREE"

def divider(char="━", length=24):
    return char * length

def get_cart_total(uid):
    total = 0
    if uid in user_orders:
        for e in user_orders[uid]:
            total += get_item_price(e["category"], e["item"]) * e["qty"]
    return total

def get_cart_count(uid):
    if uid not in user_orders:
        return 0
    return sum(e["qty"] for e in user_orders[uid])

# ==================== START ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "Guest"
    
    text = (
        f"🌟 *Welcome to {RESTAURANT_INFO['name']}* 🌟\n"
        f"_{RESTAURANT_INFO['tagline']}_\n"
        f"{divider()}\n\n"
        f"👋 Hello *{name}*!\n\n"
        f"🍽️ Authentic Ethiopian cuisine\n"
        f"👨‍🍳 Fresh ingredients • Traditional recipes\n"
        f"⭐ Rated {RESTAURANT_INFO['rating']}\n"
        f"🕐 Open {RESTAURANT_INFO['hours']}\n\n"
        f"👇 *Choose an option to get started:*"
    )
    
    inline_kb = [
        [InlineKeyboardButton("🍽️  Browse Full Menu", callback_data="menu")],
        [InlineKeyboardButton("🛒  Start Ordering", callback_data="order")],
        [
            InlineKeyboardButton("📸 Gallery", callback_data="gallery"),
            InlineKeyboardButton("ℹ️ About", callback_data="about")
        ],
        [
            InlineKeyboardButton("📍 Location", callback_data="location"),
            InlineKeyboardButton("📞 Contact", callback_data="contact")
        ],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    
    await update.effective_message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_kb),
        parse_mode=ParseMode.MARKDOWN
    )

# ==================== BUTTON HANDLER ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data != "noop":
        await query.answer()
    else:
        return

    try:
        if data == "menu":
            await show_menu(update, context)
        elif data == "order":
            await show_order_categories(update, context)
        elif data == "gallery":
            await show_gallery(update, context)
        elif data == "about":
            await show_about(update, context)
        elif data == "location":
            await show_location(update, context)
        elif data == "contact":
            await show_contact(update, context)
        elif data == "help":
            await help_command(update, context)
        elif data == "back_main":
            await back_to_main(update, context)
        elif data.startswith("category_"):
            category = data.split("_", 1)[1]
            await show_category_items(update, context, category)
        elif data.startswith("order_"):
            rest = data[6:]
            category = item = None
            for cat_key in list(MENU.keys()) + ["featured"]:
                if rest.startswith(cat_key + "_"):
                    category = cat_key
                    item = rest[len(cat_key) + 1:]
                    break
            if category and item:
                await add_to_order(update, context, category, item)
            else:
                await query.answer("⚠️ Invalid item", show_alert=True)
        elif data == "view_cart":
            await view_cart(update, context)
        elif data == "checkout":
            await checkout(update, context)
        elif data == "clear_cart":
            await clear_cart(update, context)
        elif data.startswith("qty_"):
            parts = data.split("_")
            if len(parts) >= 4:
                action = parts[-1]
                category = parts[1]
                item = "_".join(parts[2:-1])
                await change_quantity(update, context, category, item, action)
        elif data.startswith("remove_"):
            rest = data[7:]
            for cat_key in list(MENU.keys()) + ["featured"]:
                if rest.startswith(cat_key + "_"):
                    category = cat_key
                    item = rest[len(cat_key) + 1:]
                    await remove_from_cart(update, context, category, item)
                    break
        elif data.startswith("copy_cbe_"):
            await query.answer(f"✅ CBE Copied: {data.replace('copy_cbe_', '')}", show_alert=True)
        elif data.startswith("copy_tele_"):
            await query.answer(f"✅ Telebirr Copied: {data.replace('copy_tele_', '')}", show_alert=True)
        elif data.startswith("copy_phone_"):
            await query.answer(f"✅ Phone Copied: {RESTAURANT_INFO['phone']}", show_alert=True)
        elif data == "upload_receipt":
            await upload_receipt_instructions(update, context)
        elif data == "cancel_upload":
            await cancel_upload(update, context)
        elif data == "payment_done":
            await query.answer("✅ Thank you! Please upload your payment receipt.", show_alert=True)
        elif data == "clear_confirm":
            user_orders[update.effective_user.id] = []
            await query.edit_message_text("🗑️ *Cart cleared successfully.*", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Handler error for {data}: {e}")

# ==================== FULL MENU ====================
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    featured = get_featured_item()
    today = datetime.datetime.now().strftime("%A")
    
    msg = (
        f"╔══════════════════════════╗\n"
        f"   🍽️  *FULL MENU*  🍽️\n"
        f"╚══════════════════════════╝\n\n"
    )
    
    if featured:
        msg += f"🔥 *FEATURED TODAY ({today})*\n"
        msg += f"{divider('─')}\n"
        for k, v in featured.items():
            msg += (
                f"⭐ *{v['name']}*\n"
                f"   💰 *{v['price']} ETB*\n"
                f"   📝 _{v['description']}_\n"
                f"   ⏱️ Prep: {v.get('prep','20 min')}\n\n"
            )
        msg += f"{divider()}\n\n"
    
    for ck, cd in MENU.items():
        if ck == "featured":
            continue
        icon = cd.get("icon", "🍽️")
        msg += f"{icon} *{cd['name'].upper()}*\n"
        msg += f"{divider('─')}\n"
        for item, details in cd["items"].items():
            p = format_price(details["price"])
            i_icon = details.get("icon", "•")
            msg += f"{i_icon} *{item.replace('_',' ').title()}* — `{p}`\n"
            msg += f"     _{details['description']}_\n"
        msg += "\n"
    
    msg += f"{divider()}\n"
    msg += "💡 *Tip:* Tap the button below to start ordering!"
    
    kb = [
        [InlineKeyboardButton("🛒  Start Ordering", callback_data="order")],
        [InlineKeyboardButton("🏠  Main Menu", callback_data="back_main")]
    ]
    
    try:
        await update.effective_message.reply_text(
            msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN
        )
    except Exception:
        # Fallback if message too long
        await update.effective_message.reply_text(
            "🍽️ *Full Menu*\n\nTap below to start ordering:",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode=ParseMode.MARKDOWN
        )

# ==================== ORDER CATEGORIES ====================
async def show_order_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    cart_count = get_cart_count(uid)
    cart_total = get_cart_total(uid)
    
    msg = (
        f"╔══════════════════════════╗\n"
        f"   🛒  *PLACE YOUR ORDER*  🛒\n"
        f"╚══════════════════════════╝\n\n"
    )
    
    if cart_count > 0:
        msg += f"🛒 *Cart:* {cart_count} items • *{cart_total} ETB*\n\n"
    
    msg += "👇 *Select a category below:*"
    
    kb = []
    featured = get_featured_item()
    if featured:
        kb.append([InlineKeyboardButton("🔥  Featured Today", callback_data="category_featured")])
    
    for ck, cd in MENU.items():
        if ck == "featured":
            continue
        icon = cd.get("icon", "🍽️")
        count = len(cd["items"])
        kb.append([InlineKeyboardButton(f"{icon}  {cd['name']}  ({count})", callback_data=f"category_{ck}")])
    
    kb.append([InlineKeyboardButton("👀  View Cart", callback_data="view_cart")])
    kb.append([InlineKeyboardButton("🏠  Main Menu", callback_data="back_main")])
    
    await update.effective_message.reply_text(
        msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN
    )

# ==================== CATEGORY ITEMS ====================
async def show_category_items(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    if category == "featured":
        items = get_featured_item()
        if not items:
            await update.effective_message.reply_text("❌ No featured item today.")
            return
        title = "🔥 Featured Today"
    else:
        if category not in MENU:
            await update.effective_message.reply_text("❌ Category not found.")
            return
        items = MENU[category]["items"]
        title = f"{MENU[category].get('icon','🍽️')} {MENU[category]['name']}"
    
    msg = (
        f"╔══════════════════════════╗\n"
        f"   {title}\n"
        f"╚══════════════════════════╝\n\n"
        f"👇 *Tap an item to add to cart:*"
    )
    
    kb = []
    for item, details in items.items():
        name = details.get("name", item.replace("_", " ").title())
        p = format_price(details["price"])
        icon = details.get("icon", "🍽️")
        kb.append([InlineKeyboardButton(f"{icon} {name}  —  {p}", callback_data=f"order_{category}_{item}")])
    
    kb.append([
        InlineKeyboardButton("🔙  Categories", callback_data="order"),
        InlineKeyboardButton("🛒  Cart", callback_data="view_cart")
    ])
    
    await update.effective_message.reply_text(
        msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN
    )

# ==================== ADD TO CART ====================
async def add_to_order(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str, item: str):
    uid = update.effective_user.id
    if uid not in user_orders:
        user_orders[uid] = []
    
    found = False
    for entry in user_orders[uid]:
        if entry["category"] == category and entry["item"] == item:
            entry["qty"] += 1
            found = True
            break
    
    if not found:
        user_orders[uid].append({"category": category, "item": item, "qty": 1})
    
    name = get_item_name(category, item)
    icon = get_item_icon(category, item)
    qty = next(e["qty"] for e in user_orders[uid] if e["category"] == category and e["item"] == item)
    count = get_cart_count(uid)
    total = get_cart_total(uid)
    
    await update.effective_message.reply_text(
        f"✅ {icon} *{name}* added!\n"
        f"   Quantity: *{qty}*\n"
        f"{divider('─')}\n"
        f"🛒 Cart: *{count} items* • *{total} ETB*",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒  View Cart", callback_data="view_cart")],
            [InlineKeyboardButton("🔙  Continue Shopping", callback_data="order")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

async def change_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str, item: str, action: str):
    uid = update.effective_user.id
    if uid not in user_orders:
        return
    for entry in list(user_orders[uid]):
        if entry["category"] == category and entry["item"] == item:
            if action == "plus":
                entry["qty"] += 1
            elif action == "minus":
                entry["qty"] -= 1
                if entry["qty"] <= 0:
                    user_orders[uid].remove(entry)
            break
    await view_cart(update, context)

async def remove_from_cart(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str, item: str):
    uid = update.effective_user.id
    if uid in user_orders:
        user_orders[uid] = [e for e in user_orders[uid] if not (e["category"] == category and e["item"] == item)]
    await view_cart(update, context)

# ==================== CART ====================
async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    
    if uid not in user_orders or not user_orders[uid]:
        msg = (
            f"╔══════════════════════════╗\n"
            f"   🛒  *YOUR CART*  🛒\n"
            f"╚══════════════════════════╝\n\n"
            f"😔 *Your cart is empty*\n\n"
            f"Browse our menu and add delicious items!"
        )
        kb = [
            [InlineKeyboardButton("🍽️  Browse Menu", callback_data="order")],
            [InlineKeyboardButton("🏠  Main Menu", callback_data="back_main")]
        ]
        await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
        return
    
    msg = (
        f"╔══════════════════════════╗\n"
        f"   🛒  *YOUR CART*  🛒\n"
        f"╚══════════════════════════╝\n\n"
    )
    total = 0
    kb = []
    
    for idx, entry in enumerate(user_orders[uid], 1):
        c, i, q = entry["category"], entry["item"], entry["qty"]
        price = get_item_price(c, i)
        name = get_item_name(c, i)
        icon = get_item_icon(c, i)
        prep = get_item_prep(c, i)
        line_total = price * q
        total += line_total
        
        msg += (
            f"*{idx}.* {icon} *{name}*\n"
            f"     `{q} × {price} ETB = {line_total} ETB`\n"
            f"     ⏱️ {prep}\n\n"
        )
        
        kb.append([
            InlineKeyboardButton("➖", callback_data=f"qty_{c}_{i}_minus"),
            InlineKeyboardButton(f"  {q}  ", callback_data="noop"),
            InlineKeyboardButton("➕", callback_data=f"qty_{c}_{i}_plus"),
            InlineKeyboardButton("🗑️", callback_data=f"remove_{c}_{i}")
        ])
    
    msg += f"{divider()}\n"
    msg += f"💰 *TOTAL: {total} ETB*\n"
    msg += f"📦 *Items: {get_cart_count(uid)}*\n"
    msg += f"{divider()}"
    
    kb.append([InlineKeyboardButton("💳  Checkout & Pay", callback_data="checkout")])
    kb.append([
        InlineKeyboardButton("➕  Add More", callback_data="order"),
        InlineKeyboardButton("🗑️  Clear", callback_data="clear_cart")
    ])
    kb.append([InlineKeyboardButton("🏠  Main Menu", callback_data="back_main")])
    
    await update.effective_message.reply_text(
        msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN
    )

async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_orders or not user_orders[uid]:
        await update.effective_message.reply_text("🛒 Your cart is already empty.")
        return
    
    kb = [
        [InlineKeyboardButton("✅  Yes, Clear", callback_data="clear_confirm")],
        [InlineKeyboardButton("❌  Cancel", callback_data="view_cart")]
    ]
    await update.effective_message.reply_text(
        "⚠️ *Are you sure you want to clear your cart?*",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN
    )

# ==================== CHECKOUT ====================
async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_orders or not user_orders[uid]:
        await update.effective_message.reply_text("🛒 Your cart is empty.")
        return
    
    services = [o for o in user_orders[uid] if o["category"] == "services"]
    food = [o for o in user_orders[uid] if o["category"] != "services"]
    
    for s in services:
        if s["item"] == "call_admin":
            kb = [[InlineKeyboardButton("📋  Copy Phone", callback_data="copy_phone_")]]
            await update.effective_message.reply_text(
                f"📞 *Admin Phone:*\n`{RESTAURANT_INFO['phone']}`",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode=ParseMode.MARKDOWN
            )
        elif s["item"] == "telegram_support":
            kb = [[InlineKeyboardButton("💬  Message Admin", url=RESTAURANT_INFO["admin_telegram"])]]
            await update.effective_message.reply_text(
                "💬 *Opening chat with admin...*",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode=ParseMode.MARKDOWN
            )
    
    if not food:
        user_orders[uid] = []
        return
    
    total = 0
    items_lines = []
    for o in food:
        price = get_item_price(o["category"], o["item"])
        name = get_item_name(o["category"], o["item"])
        icon = get_item_icon(o["category"], o["item"])
        qty = o["qty"]
        line_total = price * qty
        total += line_total
        items_lines.append(f"  {icon} {name}\n     `{qty} × {price} = {line_total} ETB`")
    
    order_id = f"ORD-{datetime.datetime.now().strftime('%y%m%d%H%M%S')}-{uid % 10000}"
    context.user_data["last_order_id"] = order_id
    context.user_data["last_total"] = total
    
    msg = (
        f"╔══════════════════════════╗\n"
        f"   🎉  *ORDER SUMMARY*  🎉\n"
        f"╚══════════════════════════╝\n\n"
        f"🆔 *Order ID:* `{order_id}`\n"
        f"📅 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"*📦 Items:*\n" + "\n".join(items_lines) + "\n\n"
        f"{divider()}\n"
        f"💰 *TOTAL: {total} ETB*\n"
        f"{divider()}\n\n"
        f"💳 *PAYMENT METHODS*\n\n"
        f"🏦 *Commercial Bank of Ethiopia (CBE)*\n"
        f"   Account: `{RESTAURANT_INFO['cbe_account']}`\n"
        f"   Name: {RESTAURANT_INFO['name']}\n\n"
        f"📱 *Telebirr Mobile Money*\n"
        f"   Number: `{RESTAURANT_INFO['telebirr_number']}`\n"
        f"   Name: {RESTAURANT_INFO['name']}\n\n"
        f"⚠️ *After payment:*\n"
        f"   1️⃣ Upload your receipt\n"
        f"   2️⃣ We verify & prepare order\n"
        f"   3️⃣ You get notified when ready"
    )
    
    kb = [
        [
            InlineKeyboardButton("📋 Copy CBE", callback_data=f"copy_cbe_{RESTAURANT_INFO['cbe_account']}"),
            InlineKeyboardButton("📋 Copy Telebirr", callback_data=f"copy_tele_{RESTAURANT_INFO['telebirr_number']}")
        ],
        [InlineKeyboardButton("📤  Upload Receipt", callback_data="upload_receipt")],
        [InlineKeyboardButton("✅  I Have Paid", callback_data="payment_done")],
        [InlineKeyboardButton("🏠  Main Menu", callback_data="back_main")]
    ]
    
    await update.effective_message.reply_text(
        msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN
    )

# ==================== RECEIPT ====================
async def upload_receipt_instructions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users_sending_receipt[update.effective_user.id] = True
    
    msg = (
        f"╔══════════════════════════╗\n"
        f"   📤  *UPLOAD RECEIPT*  📤\n"
        f"╚══════════════════════════╝\n\n"
        f"Please send a *clear photo* or *PDF* of your payment.\n\n"
        f"*How to upload:*\n"
        f"  1️⃣ Tap 📎 (paperclip icon)\n"
        f"  2️⃣ Choose *Photo* or *File*\n"
        f"  3️⃣ Send it here\n\n"
        f"_⏳ Waiting for your receipt..._"
    )
    kb = [[InlineKeyboardButton("❌  Cancel Upload", callback_data="cancel_upload")]]
    await update.effective_message.reply_text(
        msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN
    )

async def cancel_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users_sending_receipt.pop(update.effective_user.id, None)
    try:
        await update.effective_message.delete()
    except Exception:
        pass
    await update.effective_message.reply_text("❌ *Upload cancelled.*", parse_mode=ParseMode.MARKDOWN)

async def handle_payment_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not users_sending_receipt.get(uid):
        return
    
    os.makedirs("receipts", exist_ok=True)
    filename = f"receipts/{uid}_{random.randint(1000,9999)}"
    
    try:
        if update.message.photo:
            photo = update.message.photo[-1]
            file = await photo.get_file()
            path = f"{filename}.jpg"
            await file.download_to_drive(path)
        elif update.message.document:
            doc = update.message.document
            file = await doc.get_file()
            ext = os.path.splitext(doc.file_name or "file")[1] or ".pdf"
            path = f"{filename}{ext}"
            await file.download_to_drive(path)
        else:
            await update.effective_message.reply_text("❌ Please send a *photo* or *PDF*.", parse_mode=ParseMode.MARKDOWN)
            return
        
        users_sending_receipt.pop(uid, None)
        
        # Capture order info before clearing
        order_id = context.user_data.get("last_order_id", "N/A")
        total = context.user_data.get("last_total", 0)
        order_items = list(user_orders.get(uid, []))
        user_orders[uid] = []
        
        await update.effective_message.reply_text(
            f"╔══════════════════════════╗\n"
            f"   ✅  *RECEIPT RECEIVED!*\n"
            f"╚══════════════════════════╝\n\n"
            f"🆔 Order ID: `{order_id}`\n"
            f"💰 Amount: *{total} ETB*\n\n"
            f"⏳ Your payment is being verified.\n"
            f"👨‍🍳 We'll prepare your order shortly.\n"
            f"🔔 You'll be notified when ready!\n\n"
            f"🙏 Thank you for choosing {RESTAURANT_INFO['name']}!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠  Main Menu", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        
        if ADMIN_CHAT_ID:
            user = update.effective_user
            items_text = "\n".join([
                f"  • {get_item_name(o['category'], o['item'])} × {o['qty']}"
                for o in order_items
            ])
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=(
                    f"🧾 *NEW ORDER RECEIVED*\n"
                    f"{divider('─')}\n"
                    f"🆔 Order: `{order_id}`\n"
                    f"👤 Customer: {user.full_name}\n"
                    f"📱 Username: @{user.username or 'N/A'}\n"
                    f"🆔 User ID: `{uid}`\n"
                    f"💰 Total: *{total} ETB*\n\n"
                    f"*Items:*\n{items_text}\n\n"
                    f"📎 Receipt: `{path}`"
                ),
                parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        logger.error(f"Receipt error: {e}")
        await update.effective_message.reply_text("❌ Failed to save receipt. Please try again.")

# ==================== OTHER PAGES ====================
async def show_gallery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(IMAGES_FOLDER):
        await update.effective_message.reply_text("❌ No images available.")
        return
    files = [f for f in os.listdir(IMAGES_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
    if not files:
        await update.effective_message.reply_text("❌ No images available.")
        return
    img = random.choice(files)
    try:
        with open(os.path.join(IMAGES_FOLDER, img), "rb") as f:
            await update.effective_message.reply_photo(
                photo=f,
                caption=(
                    f"📸 *{RESTAURANT_INFO['name']} Gallery*\n"
                    f"{divider('─')}\n"
                    f"🍽️ Authentic Ethiopian cuisine\n"
                    f"👨‍🍳 Made with love\n"
                    f"⭐ Rated {RESTAURANT_INFO['rating']}"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄  Another Photo", callback_data="gallery")],
                    [InlineKeyboardButton("🏠  Main Menu", callback_data="back_main")]
                ]),
                parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        await update.effective_message.reply_text(f"❌ Error: {e}")

async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        f"╔══════════════════════════╗\n"
        f"   ℹ️  *ABOUT US*  ℹ️\n"
        f"╚══════════════════════════╝\n\n"
        f"🍽️ *{RESTAURANT_INFO['name']}*\n"
        f"_{RESTAURANT_INFO['tagline']}_\n\n"
        f"We serve authentic Ethiopian cuisine prepared with traditional recipes and the finest local ingredients.\n\n"
        f"{divider()}\n"
        f"⭐ Rating: {RESTAURANT_INFO['rating']}\n"
        f"📞 Phone: `{RESTAURANT_INFO['phone']}`\n"
        f"🕐 Hours: {RESTAURANT_INFO['hours']}\n"
        f"📍 Address: {RESTAURANT_INFO['address']}\n"
        f"📧 Email: `{RESTAURANT_INFO['email']}`\n"
        f"{divider()}\n\n"
        f"*Follow us:*"
    )
    kb = [
        [InlineKeyboardButton("📱  Telegram", url=RESTAURANT_INFO["telegram"])],
        [InlineKeyboardButton("📘  Facebook", url=RESTAURANT_INFO["facebook"])],
        [InlineKeyboardButton("🏠  Main Menu", callback_data="back_main")]
    ]
    await update.effective_message.reply_text(
        msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN
    )

async def show_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        f"╔══════════════════════════╗\n"
        f"   📍  *OUR LOCATION*  📍\n"
        f"╚══════════════════════════╝\n\n"
        f"🏠 *{RESTAURANT_INFO['name']}*\n\n"
        f"📍 {RESTAURANT_INFO['address']}\n\n"
        f"Located in the heart of Bahir Dar 🇪🇹\n\n"
        f"🕐 *Hours:*\n"
        f"   {RESTAURANT_INFO['hours']}\n\n"
        f"🚗 Free parking available\n"
        f"🚶 5 min walk from city center"
    )
    kb = [
        [InlineKeyboardButton("📍  Open in Google Maps", url="https://maps.google.com/?q=Bahir+Dar,Ethiopia")],
        [InlineKeyboardButton("🏠  Main Menu", callback_data="back_main")]
    ]
    await update.effective_message.reply_text(
        msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN
    )

async def show_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        f"╔══════════════════════════╗\n"
        f"   📞  *CONTACT US*  📞\n"
        f"╚══════════════════════════╝\n\n"
        f"Need help or have a special request?\n\n"
        f"{divider()}\n"
        f"💬 *Telegram:*\n"
        f"   {RESTAURANT_INFO['admin_telegram']}\n\n"
        f"📞 *Phone:*\n"
        f"   `{RESTAURANT_INFO['phone']}`\n\n"
        f"📧 *Email:*\n"
        f"   `{RESTAURANT_INFO['email']}`\n"
        f"{divider()}\n\n"
        f"🕐 We respond within 5-10 minutes"
    )
    kb = [
        [InlineKeyboardButton("💬  Message Admin", url=RESTAURANT_INFO["admin_telegram"])],
        [InlineKeyboardButton("📋  Copy Phone", callback_data="copy_phone_")],
        [InlineKeyboardButton("🏠  Main Menu", callback_data="back_main")]
    ]
    await update.effective_message.reply_text(
        msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN
    )

# ==================== BACK TO MAIN ====================
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    cart_count = get_cart_count(uid)
    cart_total = get_cart_total(uid)
    
    text = (
        f"🏠 *Main Menu*\n"
        f"{divider('─')}\n\n"
        f"Welcome back to {RESTAURANT_INFO['name']}!\n\n"
    )
    if cart_count > 0:
        text += f"🛒 *Cart:* {cart_count} items • *{cart_total} ETB*\n\n"
    
    text += "👇 *Choose an option:*"
    
    inline_kb = [
        [InlineKeyboardButton("🍽️  Full Menu", callback_data="menu")],
        [InlineKeyboardButton("🛒  Order Now", callback_data="order")],
        [
            InlineKeyboardButton("📸 Gallery", callback_data="gallery"),
            InlineKeyboardButton("ℹ️ About", callback_data="about")
        ],
        [
            InlineKeyboardButton("📍 Location", callback_data="location"),
            InlineKeyboardButton("📞 Contact", callback_data="contact")
        ],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    
    # If cart has items, add quick resume button
    if cart_count > 0:
        inline_kb.insert(2, [
            InlineKeyboardButton(f"⚡  Resume Cart ({cart_count})", callback_data="view_cart")
        ])
    
    await update.effective_message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(inline_kb), parse_mode=ParseMode.MARKDOWN
    )

# ==================== COMMANDS ====================
async def menu_command(u, c): await show_menu(u, c)
async def order_command(u, c): await show_order_categories(u, c)
async def gallery_command(u, c): await show_gallery(u, c)
async def about_command(u, c): await show_about(u, c)
async def location_command(u, c): await show_location(u, c)
async def contact_command(u, c): await show_contact(u, c)
async def cart_command(u, c): await view_cart(u, c)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"╔══════════════════════════╗\n"
        f"   ❓  *HELP & COMMANDS*  ❓\n"
        f"╚══════════════════════════╝\n\n"
        f"🍽️ *Available Commands:*\n\n"
        f"/start    – Main menu\n"
        f"/menu     – Full menu\n"
        f"/order    – Start ordering\n"
        f"/cart     – View your cart\n"
        f"/gallery  – See photos\n"
        f"/about    – About us\n"
        f"/location – Find us\n"
        f"/contact  – Contact admin\n"
        f"/help     – This message\n\n"
        f"{divider()}\n"
        f"💡 *Tips:*\n"
        f"• Tap 🛒 items to add to cart\n"
        f"• Use ➕/➖ to change quantity\n"
        f"• Upload receipt after payment\n\n"
        f"📞 Need help? Contact admin:\n"
        f"{RESTAURANT_INFO['admin_telegram']}"
    )
    kb = [[InlineKeyboardButton("🏠  Main Menu", callback_data="back_main")]]
    await update.effective_message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN
    )

# ==================== TEXT MESSAGE HANDLER ====================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle any plain text — politely redirect user."""
    text = update.message.text.strip()
    
    await update.message.reply_text(
        f"🤔 I didn't understand: *{text}*\n\n"
        f"Please use the buttons below to navigate.\n"
        f"Or type /help to see all commands.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠  Main Menu", callback_data="back_main")],
            [InlineKeyboardButton("❓  Help", callback_data="help")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

# ==================== SET BOT COMMANDS ====================
async def set_commands(app: Application):
    commands = [
        BotCommand("start", "🏠 Main menu"),
        BotCommand("menu", "🍽️ Full menu"),
        BotCommand("order", "🛒 Start ordering"),
        BotCommand("cart", "🛒 View cart"),
        BotCommand("gallery", "📸 Gallery"),
        BotCommand("about", "ℹ️ About us"),
        BotCommand("location", "📍 Find us"),
        BotCommand("contact", "📞 Contact admin"),
        BotCommand("help", "❓ Help"),
    ]
    await app.bot.set_my_commands(commands, scope=BotCommandScopeDefault())

# ==================== ERROR HANDLER ====================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

# ==================== MAIN ====================
def main():
    app = Application.builder().token(TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("order", order_command))
    app.add_handler(CommandHandler("cart", cart_command))
    app.add_handler(CommandHandler("gallery", gallery_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("location", location_command))
    app.add_handler(CommandHandler("contact", contact_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # Messages
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_payment_receipt))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    # Callbacks
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)
    
    # Post init
    app.post_init = set_commands
    
    if WEBHOOK_URL:
        logger.info(f"🚀 Webhook mode on port {PORT}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
        )
    else:
        logger.info("⚠️ Polling mode (local testing)")
        app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
