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
LOGO_PATH = "/opt/photo_2025-08-07_21-29-50.jpg"   # 👈 Put your logo file here (same folder as bot.py)
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")
PORT = int(os.environ.get("PORT", 8000))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")

# ==================== MENU DATA ====================
MENU = {
    "featured": {"name": "🔥 Featured Today", "name_am": "🔥 የዛሬ ልዩ", "icon": "🔥", "items": {}},
    "traditional": {
        "name": "Traditional Ethiopian",
        "name_am": "ባህላዊ የኢትዮጵያ ምግቦች",
        "icon": "🇪🇹",
        "items": {
            "injera":      {"price": 30,  "description": "Traditional sourdough flatbread", "description_am": "ባህላዊ እንጀራ", "icon": "🥘", "prep": "5 min"},
            "doro_wat":    {"price": 250, "description": "Spicy chicken stew with boiled egg", "description_am": "በእንቁላል የተጋገረ ዶሮ ወጥ", "icon": "🍗", "prep": "25 min"},
            "tibs":        {"price": 200, "description": "Sautéed beef with onions and peppers", "description_am": "በቀይ ሽንኩርትና በሚጥሚጣ የተጠበሰ ስጋ", "icon": "🥩", "prep": "20 min"},
            "shiro":       {"price": 120, "description": "Chickpea stew with spices", "description_am": "በቅመማ ቅመም የተዘጋጀ ሽሮ", "icon": "🍲", "prep": "15 min"},
            "kitfo":       {"price": 280, "description": "Ethiopian minced raw beef with spices", "description_am": "በቅመማ ቅመም የተዘጋጀ ክትፎ", "icon": "🥩", "prep": "10 min"},
            "beyaynetu":   {"price": 180, "description": "Vegetarian platter with various dishes", "description_am": "የተለያዩ የጾም ምግቦች ስብስብ", "icon": "🥗", "prep": "15 min"},
            "misir_wat":   {"price": 140, "description": "Spicy red lentil stew", "description_am": "የተቀመመ ምስር ወጥ", "icon": "🍛", "prep": "20 min"},
            "gomen":       {"price": 100, "description": "Collard greens with spices", "description_am": "በቅመማ ቅመም የተዘጋጀ ጎመን", "icon": "🥬", "prep": "15 min"},
            "key_wat":     {"price": 220, "description": "Spicy beef stew", "description_am": "የተቀመመ ቀይ ወጥ", "icon": "🍖", "prep": "25 min"},
            "ayib":        {"price": 80,  "description": "Ethiopian cottage cheese", "description_am": "አይብ", "icon": "🧀", "prep": "5 min"},
        }
    },
    "fast_food": {
        "name": "Fast Food",
        "name_am": "ፈጣን ምግቦች",
        "icon": "🍔",
        "items": {
            "burger":        {"price": 150, "description": "Classic beef burger with fries", "description_am": "ክላሲክ በርገር ከጥብስ ጋር", "icon": "🍔", "prep": "15 min"},
            "pizza_slice":   {"price": 80,  "description": "Cheese pizza slice", "description_am": "የቺዝ ፒዛ ቁራጭ", "icon": "🍕", "prep": "10 min"},
            "french_fries":  {"price": 60,  "description": "Crispy golden fries", "description_am": "የተጠበሰ ድንች", "icon": "🍟", "prep": "8 min"},
            "chicken_wings": {"price": 180, "description": "Spicy chicken wings (6 pcs)", "description_am": "የተቀመሙ የዶሮ ክንፎች (6 ቁራጭ)", "icon": "🍗", "prep": "18 min"},
            "samosa":        {"price": 50,  "description": "Fried pastry with meat filling", "description_am": "በስጋ የተሞላ ሳምቡሳ", "icon": "🥟", "prep": "10 min"},
        }
    },
    "drinks": {
        "name": "Drinks & Beverages",
        "name_am": "መጠጦች",
        "icon": "🥤",
        "items": {
            "coca_cola": {"price": 40, "description": "Coca-Cola 500ml", "description_am": "ኮካ ኮላ 500ml", "icon": "🥤", "prep": "1 min"},
            "fanta":     {"price": 40, "description": "Fanta Orange 500ml", "description_am": "ፋንታ ብርቱካን 500ml", "icon": "🍊", "prep": "1 min"},
            "sprite":    {"price": 40, "description": "Sprite 500ml", "description_am": "ስፕራይት 500ml", "icon": "🥤", "prep": "1 min"},
            "water":     {"price": 20, "description": "Bottled water 500ml", "description_am": "የጠርሙስ ውሃ 500ml", "icon": "💧", "prep": "1 min"},
            "juice":     {"price": 60, "description": "Fresh fruit juice", "description_am": "ትኩስ የፍራፍሬ ጭማቂ", "icon": "🧃", "prep": "5 min"},
            "coffee":    {"price": 50, "description": "Ethiopian coffee", "description_am": "የኢትዮጵያ ቡና", "icon": "☕", "prep": "5 min"},
            "tea":       {"price": 30, "description": "Traditional tea", "description_am": "ባህላዊ ሻይ", "icon": "🍵", "prep": "3 min"},
        }
    },
    "desserts": {
        "name": "Desserts",
        "name_am": "ጣፋጭ ምግቦች",
        "icon": "🍰",
        "items": {
            "cake_slice":  {"price": 100, "description": "Chocolate cake slice", "description_am": "የቸኮሌት ኬክ ቁራጭ", "icon": "🍰", "prep": "3 min"},
            "ice_cream":   {"price": 80,  "description": "Vanilla ice cream", "description_am": "ቫኒላ አይስክሬም", "icon": "🍦", "prep": "2 min"},
            "fruit_salad": {"price": 90,  "description": "Fresh fruit salad", "description_am": "ትኩስ የፍራፍሬ ሳላድ", "icon": "🍓", "prep": "5 min"},
        }
    },
    "services": {
        "name": "Services & Support",
        "name_am": "አገልግሎቶች እና ድጋፍ",
        "icon": "💎",
        "items": {
            "call_admin":       {"price": 0, "description": "Get admin phone number", "description_am": "የአስተዳዳሪ ስልክ ቁጥር ያግኙ", "icon": "📞", "prep": "-"},
            "telegram_support": {"price": 0, "description": "Chat directly with admin", "description_am": "ከአስተዳዳሪ ጋር በቀጥታ ይወያዩ", "icon": "💬", "prep": "-"},
        }
    }
}

DAILY_SPECIALS = {
    "monday":    {"item": "doro_wat_featured", "name": "Doro Wat + Extra Injera", "name_am": "ዶሮ ወጥ + ተጨማሪ እንጀራ", "price": 200, "desc": "🔥 Monday Only - Save 50 ETB!", "desc_am": "🔥 የሰኞ ብቻ - 50 ብር ይቆጥቡ!", "icon": "🍗"},
    "tuesday":   {"item": "tibs_featured",     "name": "Tibs + Free Juice",       "name_am": "ጥብስ + ነፃ ጭማቂ",       "price": 220, "desc": "🔥 Tuesday Special!",         "desc_am": "🔥 የማክሰኞ ልዩ!",         "icon": "🥩"},
    "wednesday": {"item": "beyaynetu_featured","name": "Beyaynetu Veggie Platter","name_am": "በያይነቱ የጾም ምግብ",   "price": 150, "desc": "🔥 Wednesday - Save 30 ETB!", "desc_am": "🔥 የረቡዕ - 30 ብር ይቆጥቡ!", "icon": "🥗"},
    "thursday":  {"item": "burger_featured",   "name": "Double Burger + Fries",   "name_am": "ድርብ በርገር + ጥብስ",     "price": 180, "desc": "🔥 Thursday Deal!",           "desc_am": "🔥 የሐሙስ ቅናሽ!",         "icon": "🍔"},
    "friday":    {"item": "fish_featured",     "name": "Fried Fish + Gomen",      "name_am": "የተጠበሰ ዓሳ + ጎመን",   "price": 250, "desc": "🔥 Friday Special!",          "desc_am": "🔥 የዓርብ ልዩ!",          "icon": "🐟"},
    "saturday":  {"item": "kitfo_featured",    "name": "Kitfo + Ayib",            "name_am": "ክትፎ + አይብ",           "price": 300, "desc": "🔥 Saturday - Save 20 ETB!",  "desc_am": "🔥 የቅዳሜ - 20 ብር ይቆጥቡ!", "icon": "🥩"},
    "sunday":    {"item": "family_doro",       "name": "Family Doro Wat (4 ppl)", "name_am": "የቤተሰብ ዶሮ ወጥ (4 ሰው)", "price": 800, "desc": "🔥 Sunday Family Deal!",      "desc_am": "🔥 የእሁድ የቤተሰብ ቅናሽ!",  "icon": "👨‍👩‍👧‍👦"}
}

RESTAURANT_INFO = {
    "name": "Selem Restaurant",
    "name_am": "ሰለም ሬስቶራንት",
    "tagline": "Authentic Ethiopian Cuisine Since 2010",
    "tagline_am": "ከ2010 ዓ.ም ጀምሮ ባህላዊ የኢትዮጵያ ምግቦች",
    "address": "Bahir Dar, Ethiopia",
    "address_am": "ባህርዳር፣ ኢትዮጵያ",
    "phone": "+251965895552",
    "hours": "Mon-Sun: 10:00 AM - 11:00 PM",
    "hours_am": "ሰኞ-እሁድ: ከጠዋቱ 4:00 - ከምሽቱ 5:00",
    "telegram": "https://t.me/Amen365",
    "facebook": "https://facebook.com",
    "email": "info@selemethiopian.com",
    "cbe_account": "1000123456789",
    "telebirr_number": "0965895552",
    "admin_telegram": "https://t.me/Amen365",
    "rating": "4.9 ⭐ (2,340 reviews)",
    "rating_am": "4.9 ⭐ (2,340 ግምገማዎች)"
}

# ==================== TRANSLATIONS ====================
TEXTS = {
    "en": {
        "welcome_title": "🌟 *Welcome to {name}* 🌟",
        "hello": "👋 Hello *{name}*!",
        "welcome_intro": "🍽️ Authentic Ethiopian cuisine\n👨‍🍳 Fresh ingredients • Traditional recipes\n⭐ Rated {rating}\n🕐 Open {hours}",
        "choose_option": "👇 *Choose an option to get started:*",
        "btn_menu": "🍽️  Browse Full Menu",
        "btn_order": "🛒  Start Ordering",
        "btn_gallery": "📸 Gallery",
        "btn_about": "ℹ️ About",
        "btn_location": "📍 Location",
        "btn_contact": "📞 Contact",
        "btn_help": "❓ Help",
        "btn_back_main": "🏠  Main Menu",
        "btn_view_cart": "👀  View Cart",
        "btn_cart": "🛒  Cart",
        "btn_categories": "🔙  Categories",
        "btn_checkout": "💳  Checkout & Pay",
        "btn_add_more": "➕  Add More",
        "btn_clear": "🗑️  Clear",
        "btn_language": "🌐 Language",
        "btn_english": "🇬🇧 English",
        "btn_amharic": "🇪🇹 አማርኛ",
        "lang_select_title": "🌐 *Select Your Language*\n\nPlease choose your preferred language:",
        "lang_changed": "✅ Language changed to *English*",
        "full_menu_title": "   🍽️  *FULL MENU*  🍽️",
        "featured_today": "🔥 *FEATURED TODAY ({day})*",
        "menu_tip": "💡 *Tip:* Tap the button below to start ordering!",
        "menu_too_long": "🍽️ *Full Menu*\n\nTap below to start ordering:",
        "order_title": "   🛒  *PLACE YOUR ORDER*  🛒",
        "cart_summary": "🛒 *Cart:* {count} items • *{total} ETB*",
        "select_category": "👇 *Select a category below:*",
        "featured_button": "🔥  Featured Today",
        "tap_to_add": "👇 *Tap an item to add to cart:*",
        "added_to_cart": "✅ {icon} *{name}* added!\n   Quantity: *{qty}*",
        "continue_shopping": "🔙  Continue Shopping",
        "cart_title": "   🛒  *YOUR CART*  🛒",
        "cart_empty": "😔 *Your cart is empty*\n\nBrowse our menu and add delicious items!",
        "browse_menu": "🍽️  Browse Menu",
        "cart_total": "💰 *TOTAL: {total} ETB*",
        "cart_items": "📦 *Items: {count}*",
        "clear_confirm": "⚠️ *Are you sure you want to clear your cart?*",
        "clear_yes": "✅  Yes, Clear",
        "clear_no": "❌  Cancel",
        "cart_cleared": "🗑️ *Cart cleared successfully.*",
        "cart_already_empty": "🛒 Your cart is already empty.",
        "order_summary_title": "   🎉  *ORDER SUMMARY*  🎉",
        "order_id": "🆔 *Order ID:* `{id}`",
        "payment_methods": "💳 *PAYMENT METHODS*",
        "cbe_label": "🏦 *Commercial Bank of Ethiopia (CBE)*",
        "telebirr_label": "📱 *Telebirr Mobile Money*",
        "account_label": "   Account: `{acc}`",
        "number_label": "   Number: `{num}`",
        "name_label": "   Name: {name}",
        "after_payment": "⚠️ *After payment:*\n   1️⃣ Upload your receipt\n   2️⃣ We verify & prepare order\n   3️⃣ You get notified when ready",
        "copy_cbe": "📋 Copy CBE",
        "copy_tele": "📋 Copy Telebirr",
        "copy_phone": "📋  Copy Phone",
        "upload_receipt": "📤  Upload Receipt",
        "have_paid": "✅  I Have Paid",
        "receipt_title": "   📤  *UPLOAD RECEIPT*  📤",
        "receipt_instructions": "Please send a *clear photo* or *PDF* of your payment.\n\n*How to upload:*\n  1️⃣ Tap 📎 (paperclip icon)\n  2️⃣ Choose *Photo* or *File*\n  3️⃣ Send it here",
        "waiting_receipt": "_⏳ Waiting for your receipt..._",
        "cancel_upload": "❌  Cancel Upload",
        "upload_cancelled": "❌ *Upload cancelled.*",
        "receipt_received": "   ✅  *RECEIPT RECEIVED!*",
        "receipt_thanks": "⏳ Your payment is being verified.\n👨‍🍳 We'll prepare your order shortly.\n🔔 You'll be notified when ready!\n\n🙏 Thank you for choosing {name}!",
        "send_photo_pdf": "❌ Please send a *photo* or *PDF*.",
        "receipt_failed": "❌ Failed to save receipt. Please try again.",
        "about_title": "   ℹ️  *ABOUT US*  ℹ️",
        "about_desc": "We serve authentic Ethiopian cuisine prepared with traditional recipes and the finest local ingredients.",
        "follow_us": "*Follow us:*",
        "location_title": "   📍  *OUR LOCATION*  📍",
        "location_desc": "Located in the heart of Bahir Dar 🇪🇹",
        "location_hours": "🕐 *Hours:*",
        "location_parking": "🚗 Free parking available\n🚶 5 min walk from city center",
        "open_maps": "📍  Open in Google Maps",
        "contact_title": "   📞  *CONTACT US*  📞",
        "contact_desc": "Need help or have a special request?",
        "contact_telegram": "💬 *Telegram:*",
        "contact_phone": "📞 *Phone:*",
        "contact_email": "📧 *Email:*",
        "contact_response": "🕐 We respond within 5-10 minutes",
        "message_admin": "💬  Message Admin",
        "main_menu_title": "🏠 *Main Menu*",
        "welcome_back": "Welcome back to {name}!",
        "resume_cart": "⚡  Resume Cart ({count})",
        "help_title": "   ❓  *HELP & COMMANDS*  ❓",
        "help_commands": "🍽️ *Available Commands:*",
        "help_tips": "💡 *Tips:*\n• Tap 🛒 items to add to cart\n• Use ➕/➖ to change quantity\n• Upload receipt after payment",
        "help_contact": "📞 Need help? Contact admin:\n{link}",
        "not_understood": "🤔 I didn't understand: *{text}*\n\nPlease use the buttons below to navigate.\nOr type /help to see all commands.",
        "copied_cbe": "✅ CBE Copied: {value}",
        "copied_tele": "✅ Telebirr Copied: {value}",
        "copied_phone": "✅ Phone Copied: {value}",
        "invalid_item": "⚠️ Invalid item",
        "no_featured": "❌ No featured item today.",
        "category_not_found": "❌ Category not found.",
        "no_images": "❌ No images available.",
        "paid_thanks": "✅ Thank you! Please upload your payment receipt.",
        "admin_new_order": "🧾 *NEW ORDER RECEIVED*",
        "admin_order_id": "🆔 Order: `{id}`",
        "admin_customer": "👤 Customer: {name}",
        "admin_username": "📱 Username: @{username}",
        "admin_user_id": "🆔 User ID: `{uid}`",
        "admin_total": "💰 Total: *{total} ETB*",
        "admin_items": "*Items:*",
        "admin_receipt": "📎 Receipt: `{path}`",
        "order_date": "📅 {date}",
        "prep_label": "⏱️ {prep}",
        "free_label": "FREE",
    },
    "am": {
        "welcome_title": "🌟 *እንኳን ወደ {name} በደህና መጡ* 🌟",
        "hello": "👋 ሰላም *{name}*!",
        "welcome_intro": "🍽️ ባህላዊ የኢትዮጵያ ምግቦች\n👨‍🍳 ትኩስ ግብዓቶች • ባህላዊ የምግብ አሰራር\n⭐ ደረጃ {rating}\n🕐 ክፍት {hours}",
        "choose_option": "👇 *ለመጀመር አንድ አማራጭ ይምረጡ:*",
        "btn_menu": "🍽️  ሙሉ ምናሌ",
        "btn_order": "🛒  ማዘዝ ይጀምሩ",
        "btn_gallery": "📸 ፎቶዎች",
        "btn_about": "ℹ️ ስለ እኛ",
        "btn_location": "📍 አድራሻ",
        "btn_contact": "📞 አግኙን",
        "btn_help": "❓ እርዳታ",
        "btn_back_main": "🏠  ዋና ምናሌ",
        "btn_view_cart": "👀  ጋሪ ይመልከቱ",
        "btn_cart": "🛒  ጋሪ",
        "btn_categories": "🔙  ምድቦች",
        "btn_checkout": "💳  ይክፈሉ",
        "btn_add_more": "➕  ተጨማሪ ጨምር",
        "btn_clear": "🗑️  አጽዳ",
        "btn_language": "🌐 ቋንቋ",
        "btn_english": "🇬🇧 English",
        "btn_amharic": "🇪🇹 አማርኛ",
        "lang_select_title": "🌐 *ቋንቋ ይምረጡ*\n\nእባክዎ የሚፈልጉትን ቋንቋ ይምረጡ:",
        "lang_changed": "✅ ቋንቋ ወደ *አማርኛ* ተቀይሯል",
        "full_menu_title": "   🍽️  *ሙሉ ምናሌ*  🍽️",
        "featured_today": "🔥 *የዛሬ ልዩ ({day})*",
        "menu_tip": "💡 *ምክር:* ማዘዝ ለመጀመር ከታች ያለውን ቁልፍ ይጫኑ!",
        "menu_too_long": "🍽️ *ሙሉ ምናሌ*\n\nማዘዝ ለመጀመር ከታች ይጫኑ:",
        "order_title": "   🛒  *ማዘዝ ይጀምሩ*  🛒",
        "cart_summary": "🛒 *ጋሪ:* {count} ዕቃዎች • *{total} ብር*",
        "select_category": "👇 *ከታች አንድ ምድብ ይምረጡ:*",
        "featured_button": "🔥  የዛሬ ልዩ",
        "tap_to_add": "👇 *ወደ ጋሪ ለመጨመር አንድ ዕቃ ይጫኑ:*",
        "added_to_cart": "✅ {icon} *{name}* ተጨምሯል!\n   ብዛት: *{qty}*",
        "continue_shopping": "🔙  ግዢ ይቀጥሉ",
        "cart_title": "   🛒  *የእርስዎ ጋሪ*  🛒",
        "cart_empty": "😔 *ጋሪዎ ባዶ ነው*\n\nምናሌያችንን ይመልከቱ እና ጣፋጭ ምግቦችን ይጨምሩ!",
        "browse_menu": "🍽️  ምናሌ ይመልከቱ",
        "cart_total": "💰 *ጠቅላላ: {total} ብር*",
        "cart_items": "📦 *ዕቃዎች: {count}*",
        "clear_confirm": "⚠️ *ጋሪዎን ማጽዳት እርግጠኛ ነዎት?*",
        "clear_yes": "✅  አዎ፣ አጽዳ",
        "clear_no": "❌  ሰርዝ",
        "cart_cleared": "🗑️ *ጋሪ በተሳካ ሁኔታ ተጸድቷል።*",
        "cart_already_empty": "🛒 ጋሪዎ አስቀድሞ ባዶ ነው።",
        "order_summary_title": "   🎉  *የትዕዛዝ ማጠቃለያ*  🎉",
        "order_id": "🆔 *የትዕዛዝ መለያ:* `{id}`",
        "payment_methods": "💳 *የክፍያ መንገዶች*",
        "cbe_label": "🏦 *የኢትዮጵያ ንግድ ባንክ (CBE)*",
        "telebirr_label": "📱 *ቴሌብር ሞባይል ገንዘብ*",
        "account_label": "   አካውንት: `{acc}`",
        "number_label": "   ቁጥር: `{num}`",
        "name_label": "   ስም: {name}",
        "after_payment": "⚠️ *ከክፍያ በኋላ:*\n   1️⃣ ደረሰኝዎን ይጫኑ\n   2️⃣ እኛ አረጋግጠን ትዕዛዙን እናዘጋጃለን\n   3️⃣ ዝግጁ ሲሆን እናሳውቅዎታለን",
        "copy_cbe": "📋 CBE ቅዳ",
        "copy_tele": "📋 ቴሌብር ቅዳ",
        "copy_phone": "📋  ስልክ ቅዳ",
        "upload_receipt": "📤  ደረሰኝ ጫን",
        "have_paid": "✅  ከፍያለሁ",
        "receipt_title": "   📤  *ደረሰኝ ጫን*  📤",
        "receipt_instructions": "እባክዎ *ግልጽ ፎቶ* ወይም *PDF* የክፍያዎን ይላኩ።\n\n*እንዴት መጫን እንደሚቻል:*\n  1️⃣ 📎 (የወረቀት ክሊፕ ምልክት) ይጫኑ\n  2️⃣ *ፎቶ* ወይም *ፋይል* ይምረጡ\n  3️⃣ እዚህ ይላኩት",
        "waiting_receipt": "_⏳ ደረሰኝዎን በመጠበቅ ላይ..._",
        "cancel_upload": "❌  ጭነት ሰርዝ",
        "upload_cancelled": "❌ *ጭነት ተሰርዟል።*",
        "receipt_received": "   ✅  *ደረሰኝ ተቀብሏል!*",
        "receipt_thanks": "⏳ ክፍያዎ በመረጋገጥ ላይ ነው።\n👨‍🍳 ትዕዛዝዎን በቅርቡ እናዘጋጃለን።\n🔔 ዝግጁ ሲሆን እናሳውቅዎታለን!\n\n🙏 {name} ስለመረጡ እናመሰግናለን!",
        "send_photo_pdf": "❌ እባክዎ *ፎቶ* ወይም *PDF* ይላኩ።",
        "receipt_failed": "❌ ደረሰኙን ማስቀመጥ አልተሳካም። እባክዎ እንደገና ይሞክሩ።",
        "about_title": "   ℹ️  *ስለ እኛ*  ℹ️",
        "about_desc": "እኛ ባህላዊ የምግብ አሰራር እና ምርጥ የአካባቢ ግብዓቶችን በመጠቀም የተዘጋጁ ትክክለኛ የኢትዮጵያ ምግቦችን እናቀርባለን።",
        "follow_us": "*ይከተሉን:*",
        "location_title": "   📍  *አድራሻችን*  📍",
        "location_desc": "በባህርዳር እምብርት ውስጥ ይገኛል 🇪🇹",
        "location_hours": "🕐 *የስራ ሰዓት:*",
        "location_parking": "🚗 ነፃ የመኪና ማቆሚያ\n🚶 ከከተማ ማዕከል 5 ደቂቃ በእግር",
        "open_maps": "📍  በGoogle Maps ክፈት",
        "contact_title": "   📞  *አግኙን*  📞",
        "contact_desc": "እርዳታ ይፈልጋሉ ወይም ልዩ ጥያቄ አለዎት?",
        "contact_telegram": "💬 *ቴሌግራም:*",
        "contact_phone": "📞 *ስልክ:*",
        "contact_email": "📧 *ኢሜይል:*",
        "contact_response": "🕐 በ5-10 ደቂቃ ውስጥ እንመልሳለን",
        "message_admin": "💬  ለአስተዳዳሪ መልእክት",
        "main_menu_title": "🏠 *ዋና ምናሌ*",
        "welcome_back": "ወደ {name} እንኳን በደህና ተመለሱ!",
        "resume_cart": "⚡  ጋሪ ቀጥል ({count})",
        "help_title": "   ❓  *እርዳታ እና ትዕዛዞች*  ❓",
        "help_commands": "🍽️ *ያሉ ትዕዛዞች:*",
        "help_tips": "💡 *ምክሮች:*\n• ወደ ጋሪ ለመጨመር 🛒 ዕቃዎችን ይጫኑ\n• ብዛት ለመቀየር ➕/➖ ይጠቀሙ\n• ከክፍያ በኋላ ደረሰኝ ይጫኑ",
        "help_contact": "📞 እርዳታ ይፈልጋሉ? አስተዳዳሪን ያግኙ:\n{link}",
        "not_understood": "🤔 አልገባኝም: *{text}*\n\nእባክዎ ከታች ያሉትን ቁልፎች ተጠቅመው ይጓዙ።\nወይም /help ብለው ይጻፉ።",
        "copied_cbe": "✅ CBE ተቀድቷል: {value}",
        "copied_tele": "✅ ቴሌብር ተቀድቷል: {value}",
        "copied_phone": "✅ ስልክ ተቀድቷል: {value}",
        "invalid_item": "⚠️ የተሳሳተ ዕቃ",
        "no_featured": "❌ ዛሬ ልዩ ዕቃ የለም።",
        "category_not_found": "❌ ምድብ አልተገኘም።",
        "no_images": "❌ ፎቶዎች አልተገኙም።",
        "paid_thanks": "✅ አመሰግናለሁ! እባክዎ የክፍያ ደረሰኝዎን ይጫኑ።",
        "admin_new_order": "🧾 *አዲስ ትዕዛዝ ተቀብሏል*",
        "admin_order_id": "🆔 ትዕዛዝ: `{id}`",
        "admin_customer": "👤 ደንበኛ: {name}",
        "admin_username": "📱 የተጠቃሚ ስም: @{username}",
        "admin_user_id": "🆔 የተጠቃሚ መለያ: `{uid}`",
        "admin_total": "💰 ጠቅላላ: *{total} ብር*",
        "admin_items": "*ዕቃዎች:*",
        "admin_receipt": "📎 ደረሰኝ: `{path}`",
        "order_date": "📅 {date}",
        "prep_label": "⏱️ {prep}",
        "free_label": "ነፃ",
    }
}

# ==================== STORAGE ====================
user_orders = {}
users_sending_receipt = {}
user_languages = {}

# ==================== LANGUAGE HELPERS ====================
def get_lang(uid):
    return user_languages.get(uid, "en")

def set_lang(uid, lang):
    user_languages[uid] = lang

def t(uid, key, **kwargs):
    lang = get_lang(uid)
    text = TEXTS.get(lang, TEXTS["en"]).get(key, TEXTS["en"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text

def get_cat_name(category, uid):
    if category == "featured":
        return t(uid, "featured_button").strip()
    cat = MENU.get(category, {})
    lang = get_lang(uid)
    if lang == "am":
        return cat.get("name_am", cat.get("name", category))
    return cat.get("name", category)

def get_item_name_lang(category, item, uid):
    if get_lang(uid) == "am":
        return get_item_name_am(category, item)
    return get_item_name(category, item)

def get_item_name_am(category, item):
    if category == "featured":
        featured = get_featured_item()
        v = featured.get(item, {})
        return v.get("name_am", v.get("name", item.replace("_", " ").title()))
    details = MENU.get(category, {}).get("items", {}).get(item, {})
    return details.get("description_am", item.replace("_", " ").title())

def get_item_desc_lang(category, item, uid):
    lang = get_lang(uid)
    if category == "featured":
        v = get_featured_item().get(item, {})
        return v.get("desc_am" if lang == "am" else "description", "")
    details = MENU.get(category, {}).get("items", {}).get(item, {})
    return details.get("description_am" if lang == "am" else "description", "")

def get_restaurant_name(uid):
    return RESTAURANT_INFO.get("name_am" if get_lang(uid) == "am" else "name", "Selem Restaurant")

def get_restaurant_tagline(uid):
    return RESTAURANT_INFO.get("tagline_am" if get_lang(uid) == "am" else "tagline", "")

def get_restaurant_address(uid):
    return RESTAURANT_INFO.get("address_am" if get_lang(uid) == "am" else "address", "")

def get_restaurant_hours(uid):
    return RESTAURANT_INFO.get("hours_am" if get_lang(uid) == "am" else "hours", "")

def get_restaurant_rating(uid):
    return RESTAURANT_INFO.get("rating_am" if get_lang(uid) == "am" else "rating", "")

# ==================== HELPERS ====================
def get_featured_item():
    today = datetime.datetime.now().strftime("%A").lower()
    special = DAILY_SPECIALS.get(today)
    if special:
        return {
            special["item"]: {
                "price": special["price"],
                "description": special["desc"],
                "description_am": special["desc_am"],
                "name": special["name"],
                "name_am": special["name_am"],
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

def format_price(price, uid=None):
    if price > 0:
        return f"{price} ETB" if (uid is None or get_lang(uid) == "en") else f"{price} ብር"
    return t(uid, "free_label") if uid else "FREE"

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

def lang_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en"),
            InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="set_lang_am")
        ]
    ])

# ==================== SEND LOGO HELPER ====================
async def send_logo_with_caption(message, caption, reply_markup=None):
    """
    Send logo image with caption. Falls back to text if logo missing.
    """
    if os.path.exists(LOGO_PATH):
        try:
            with open(LOGO_PATH, "rb") as f:
                await message.reply_photo(
                    photo=f,
                    caption=caption,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
            return True
        except Exception as e:
            logger.error(f"Logo send failed: {e}")
    # Fallback to text
    await message.reply_text(
        caption,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    return False

# ==================== SEND LANGUAGE SELECTOR ====================
async def send_language_selector(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send language selector screen with logo."""
    caption = (
        f"🌟 *{RESTAURANT_INFO['name']}* 🌟\n"
        f"_{RESTAURANT_INFO['tagline']}_\n"
        f"{divider()}\n\n"
        f"🌐 *Select Your Language*\n"
        f"🌐 *ቋንቋ ይምረጡ*\n\n"
        f"Please choose your preferred language:\n"
        f"እባክዎ የሚፈልጉትን ቋንቋ ይምረጡ:"
    )
    await send_logo_with_caption(
        update.effective_message,
        caption,
        reply_markup=lang_keyboard()
    )

# ==================== SEND WELCOME ====================
async def send_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome/main menu screen with logo — the canonical home screen."""
    user = update.effective_user
    uid = user.id
    name = user.first_name or ("እንግዳ" if get_lang(uid) == "am" else "Guest")

    text = (
        f"{t(uid, 'welcome_title', name=get_restaurant_name(uid))}\n"
        f"_{get_restaurant_tagline(uid)}_\n"
        f"{divider()}\n\n"
        f"{t(uid, 'hello', name=name)}\n\n"
        f"{t(uid, 'welcome_intro', rating=get_restaurant_rating(uid), hours=get_restaurant_hours(uid))}\n\n"
        f"{t(uid, 'choose_option')}"
    )

    inline_kb = [
        [InlineKeyboardButton(t(uid, "btn_menu"), callback_data="menu")],
        [InlineKeyboardButton(t(uid, "btn_order"), callback_data="order")],
        [
            InlineKeyboardButton(t(uid, "btn_gallery"), callback_data="gallery"),
            InlineKeyboardButton(t(uid, "btn_about"), callback_data="about")
        ],
        [
            InlineKeyboardButton(t(uid, "btn_location"), callback_data="location"),
            InlineKeyboardButton(t(uid, "btn_contact"), callback_data="contact")
        ],
        [
            InlineKeyboardButton(t(uid, "btn_help"), callback_data="help"),
            InlineKeyboardButton(t(uid, "btn_language"), callback_data="language")
        ]
    ]

    # Add cart resume button if user has items
    cart_count = get_cart_count(uid)
    if cart_count > 0:
        inline_kb.insert(2, [
            InlineKeyboardButton(t(uid, "resume_cart", count=cart_count), callback_data="view_cart")
        ])

    await send_logo_with_caption(
        update.effective_message,
        text,
        reply_markup=InlineKeyboardMarkup(inline_kb)
    )

# ==================== START ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    
    # First-time users: show language selector with logo
    if uid not in user_languages:
        await send_language_selector(update, context)
        return
    
    # Returning users: show welcome with logo
    await send_welcome(update, context)

# ==================== BUTTON HANDLER ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data != "noop":
        await query.answer()
    else:
        return

    uid = update.effective_user.id

    # Helper: edit message safely (works for photo captions & text)
    async def safe_edit(caption_text, reply_markup=None):
        """Edit current message — handles both photo-caption and plain text."""
        try:
            if query.message.photo:
                await query.edit_message_caption(
                    caption=caption_text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await query.edit_message_text(
                    text=caption_text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
            return True
        except Exception as e:
            logger.warning(f"safe_edit failed: {e}")
            return False

    try:
        # ---------- LANGUAGE SELECTION ----------
        if data == "set_lang_en":
            set_lang(uid, "en")
            # Delete old message, resend welcome with new language + logo
            try:
                await query.message.delete()
            except Exception:
                pass
            await send_welcome(update, context)
            return

        elif data == "set_lang_am":
            set_lang(uid, "am")
            try:
                await query.message.delete()
            except Exception:
                pass
            await send_welcome(update, context)
            return

        elif data == "language":
            # Delete old, resend language selector with logo
            try:
                await query.message.delete()
            except Exception:
                pass
            await send_language_selector(update, context)
            return

        # ---------- MAIN NAVIGATION ----------
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
            # Delete current, resend welcome with logo
            try:
                await query.message.delete()
            except Exception:
                pass
            await send_welcome(update, context)
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
                await query.answer(t(uid, "invalid_item"), show_alert=True)
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
            await query.answer(t(uid, "copied_cbe", value=data.replace('copy_cbe_', '')), show_alert=True)
        elif data.startswith("copy_tele_"):
            await query.answer(t(uid, "copied_tele", value=data.replace('copy_tele_', '')), show_alert=True)
        elif data.startswith("copy_phone_"):
            await query.answer(t(uid, "copied_phone", value=RESTAURANT_INFO['phone']), show_alert=True)
        elif data == "upload_receipt":
            await upload_receipt_instructions(update, context)
        elif data == "cancel_upload":
            await cancel_upload(update, context)
        elif data == "payment_done":
            await query.answer(t(uid, "paid_thanks"), show_alert=True)
        elif data == "clear_confirm":
            user_orders[uid] = []
            await safe_edit(t(uid, "cart_cleared"))
    except Exception as e:
        logger.error(f"Handler error for {data}: {e}", exc_info=True)

# ==================== FULL MENU ====================
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    featured = get_featured_item()
    today = datetime.datetime.now().strftime("%A")
    
    msg = (
        f"╔══════════════════════════╗\n"
        f"{t(uid, 'full_menu_title')}\n"
        f"╚══════════════════════════╝\n\n"
    )
    
    if featured:
        msg += f"{t(uid, 'featured_today', day=today)}\n"
        msg += f"{divider('─')}\n"
        for k, v in featured.items():
            name = v.get("name_am" if get_lang(uid) == "am" else "name", v.get("name", k))
            desc = v.get("desc_am" if get_lang(uid) == "am" else "description", v.get("description", ""))
            msg += (
                f"⭐ *{name}*\n"
                f"   💰 *{format_price(v['price'], uid)}*\n"
                f"   📝 _{desc}_\n"
                f"   {t(uid, 'prep_label', prep=v.get('prep','20 min'))}\n\n"
            )
        msg += f"{divider()}\n\n"
    
    for ck, cd in MENU.items():
        if ck == "featured":
            continue
        icon = cd.get("icon", "🍽️")
        cat_name = cd.get("name_am" if get_lang(uid) == "am" else "name", cd.get("name", ck))
        msg += f"{icon} *{cat_name.upper()}*\n"
        msg += f"{divider('─')}\n"
        for item, details in cd["items"].items():
            p = format_price(details["price"], uid)
            i_icon = details.get("icon", "•")
            i_name = get_item_name_lang(ck, item, uid)
            i_desc = get_item_desc_lang(ck, item, uid)
            msg += f"{i_icon} *{i_name}* — `{p}`\n"
            if get_lang(uid) == "en":
                msg += f"     _{i_desc}_\n"
            else:
                msg += f"     _{details.get('description', '')}_\n"
        msg += "\n"
    
    msg += f"{divider()}\n"
    msg += t(uid, "menu_tip")
    
    kb = [
        [InlineKeyboardButton(t(uid, "btn_order"), callback_data="order")],
        [InlineKeyboardButton(t(uid, "btn_back_main"), callback_data="back_main")]
    ]
    
    try:
        await update.effective_message.reply_text(
            msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN
        )
    except Exception:
        await update.effective_message.reply_text(
            t(uid, "menu_too_long"),
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
        f"{t(uid, 'order_title')}\n"
        f"╚══════════════════════════╝\n\n"
    )
    
    if cart_count > 0:
        msg += f"{t(uid, 'cart_summary', count=cart_count, total=cart_total)}\n\n"
    
    msg += t(uid, "select_category")
    
    kb = []
    featured = get_featured_item()
    if featured:
        kb.append([InlineKeyboardButton(t(uid, "featured_button"), callback_data="category_featured")])
    
    for ck, cd in MENU.items():
        if ck == "featured":
            continue
        icon = cd.get("icon", "🍽️")
        cat_name = cd.get("name_am" if get_lang(uid) == "am" else "name", cd.get("name", ck))
        count = len(cd["items"])
        kb.append([InlineKeyboardButton(f"{icon}  {cat_name}  ({count})", callback_data=f"category_{ck}")])
    
    kb.append([InlineKeyboardButton(t(uid, "btn_view_cart"), callback_data="view_cart")])
    kb.append([InlineKeyboardButton(t(uid, "btn_back_main"), callback_data="back_main")])
    
    await update.effective_message.reply_text(
        msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN
    )

# ==================== CATEGORY ITEMS ====================
async def show_category_items(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    uid = update.effective_user.id
    
    if category == "featured":
        items = get_featured_item()
        if not items:
            await update.effective_message.reply_text(t(uid, "no_featured"))
            return
        title = t(uid, "featured_button").strip()
    else:
        if category not in MENU:
            await update.effective_message.reply_text(t(uid, "category_not_found"))
            return
        items = MENU[category]["items"]
        cat_name = MENU[category].get("name_am" if get_lang(uid) == "am" else "name", MENU[category]["name"])
        title = f"{MENU[category].get('icon','🍽️')} {cat_name}"
    
    msg = (
        f"╔══════════════════════════╗\n"
        f"   {title}\n"
        f"╚══════════════════════════╝\n\n"
        f"{t(uid, 'tap_to_add')}"
    )
    
    kb = []
    for item, details in items.items():
        name = get_item_name_lang(category, item, uid)
        p = format_price(details["price"], uid)
        icon = details.get("icon", "🍽️")
        kb.append([InlineKeyboardButton(f"{icon} {name}  —  {p}", callback_data=f"order_{category}_{item}")])
    
    kb.append([
        InlineKeyboardButton(t(uid, "btn_categories"), callback_data="order"),
        InlineKeyboardButton(t(uid, "btn_cart"), callback_data="view_cart")
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
    
    name = get_item_name_lang(category, item, uid)
    icon = get_item_icon(category, item)
    qty = next(e["qty"] for e in user_orders[uid] if e["category"] == category and e["item"] == item)
    count = get_cart_count(uid)
    total = get_cart_total(uid)
    
    await update.effective_message.reply_text(
        f"{t(uid, 'added_to_cart', icon=icon, name=name, qty=qty)}\n"
        f"{divider('─')}\n"
        f"{t(uid, 'cart_summary', count=count, total=total)}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(t(uid, "btn_view_cart"), callback_data="view_cart")],
            [InlineKeyboardButton(t(uid, "continue_shopping"), callback_data="order")]
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
            f"{t(uid, 'cart_title')}\n"
            f"╚══════════════════════════╝\n\n"
            f"{t(uid, 'cart_empty')}"
        )
        kb = [
            [InlineKeyboardButton(t(uid, "browse_menu"), callback_data="order")],
            [InlineKeyboardButton(t(uid, "btn_back_main"), callback_data="back_main")]
        ]
        await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
        return
    
    msg = (
        f"╔══════════════════════════╗\n"
        f"{t(uid, 'cart_title')}\n"
        f"╚══════════════════════════╝\n\n"
    )
    total = 0
    kb = []
    
    for idx, entry in enumerate(user_orders[uid], 1):
        c, i, q = entry["category"], entry["item"], entry["qty"]
        price = get_item_price(c, i)
        name = get_item_name_lang(c, i, uid)
        icon = get_item_icon(c, i)
        prep = get_item_prep(c, i)
        line_total = price * q
        total += line_total
        
        msg += (
            f"*{idx}.* {icon} *{name}*\n"
            f"     `{q} × {price} = {line_total}`\n"
            f"     {t(uid, 'prep_label', prep=prep)}\n\n"
        )
        
        kb.append([
            InlineKeyboardButton("➖", callback_data=f"qty_{c}_{i}_minus"),
            InlineKeyboardButton(f"  {q}  ", callback_data="noop"),
            InlineKeyboardButton("➕", callback_data=f"qty_{c}_{i}_plus"),
            InlineKeyboardButton("🗑️", callback_data=f"remove_{c}_{i}")
        ])
    
    msg += f"{divider()}\n"
    msg += f"{t(uid, 'cart_total', total=total)}\n"
    msg += f"{t(uid, 'cart_items', count=get_cart_count(uid))}\n"
    msg += f"{divider()}"
    
    kb.append([InlineKeyboardButton(t(uid, "btn_checkout"), callback_data="checkout")])
    kb.append([
        InlineKeyboardButton(t(uid, "btn_add_more"), callback_data="order"),
        InlineKeyboardButton(t(uid, "btn_clear"), callback_data="clear_cart")
    ])
    kb.append([InlineKeyboardButton(t(uid, "btn_back_main"), callback_data="back_main")])
    
    await update.effective_message.reply_text(
        msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN
    )

async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_orders or not user_orders[uid]:
        await update.effective_message.reply_text(t(uid, "cart_already_empty"))
        return
    
    kb = [
        [InlineKeyboardButton(t(uid, "clear_yes"), callback_data="clear_confirm")],
        [InlineKeyboardButton(t(uid, "clear_no"), callback_data="view_cart")]
    ]
    await update.effective_message.reply_text(
        t(uid, "clear_confirm"),
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN
    )

# ==================== CHECKOUT ====================
async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_orders or not user_orders[uid]:
        await update.effective_message.reply_text(t(uid, "cart_already_empty"))
        return
    
    services = [o for o in user_orders[uid] if o["category"] == "services"]
    food = [o for o in user_orders[uid] if o["category"] != "services"]
    
    for s in services:
        if s["item"] == "call_admin":
            kb = [[InlineKeyboardButton(t(uid, "copy_phone"), callback_data="copy_phone_")]]
            await update.effective_message.reply_text(
                f"{t(uid, 'contact_phone')}\n`{RESTAURANT_INFO['phone']}`",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode=ParseMode.MARKDOWN
            )
        elif s["item"] == "telegram_support":
            kb = [[InlineKeyboardButton(t(uid, "message_admin"), url=RESTAURANT_INFO["admin_telegram"])]]
            await update.effective_message.reply_text(
                t(uid, "message_admin"),
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
        name = get_item_name_lang(o["category"], o["item"], uid)
        icon = get_item_icon(o["category"], o["item"])
        qty = o["qty"]
        line_total = price * qty
        total += line_total
        items_lines.append(f"  {icon} {name}\n     `{qty} × {price} = {line_total}`")
    
    order_id = f"ORD-{datetime.datetime.now().strftime('%y%m%d%H%M%S')}-{uid % 10000}"
    context.user_data["last_order_id"] = order_id
    context.user_data["last_total"] = total
    
    msg = (
        f"╔══════════════════════════╗\n"
        f"{t(uid, 'order_summary_title')}\n"
        f"╚══════════════════════════╝\n\n"
        f"{t(uid, 'order_id', id=order_id)}\n"
        f"{t(uid, 'order_date', date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))}\n\n"
        f"{t(uid, 'admin_items')}\n" + "\n".join(items_lines) + "\n\n"
        f"{divider()}\n"
        f"{t(uid, 'cart_total', total=total)}\n"
        f"{divider()}\n\n"
        f"{t(uid, 'payment_methods')}\n\n"
        f"{t(uid, 'cbe_label')}\n"
        f"{t(uid, 'account_label', acc=RESTAURANT_INFO['cbe_account'])}\n"
        f"{t(uid, 'name_label', name=get_restaurant_name(uid))}\n\n"
        f"{t(uid, 'telebirr_label')}\n"
        f"{t(uid, 'number_label', num=RESTAURANT_INFO['telebirr_number'])}\n"
        f"{t(uid, 'name_label', name=get_restaurant_name(uid))}\n\n"
        f"{t(uid, 'after_payment')}"
    )
    
    kb = [
        [
            InlineKeyboardButton(t(uid, "copy_cbe"), callback_data=f"copy_cbe_{RESTAURANT_INFO['cbe_account']}"),
            InlineKeyboardButton(t(uid, "copy_tele"), callback_data=f"copy_tele_{RESTAURANT_INFO['telebirr_number']}")
        ],
        [InlineKeyboardButton(t(uid, "upload_receipt"), callback_data="upload_receipt")],
        [InlineKeyboardButton(t(uid, "have_paid"), callback_data="payment_done")],
        [InlineKeyboardButton(t(uid, "btn_back_main"), callback_data="back_main")]
    ]
    
    await update.effective_message.reply_text(
        msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN
    )

# ==================== RECEIPT ====================
async def upload_receipt_instructions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users_sending_receipt[uid] = True
    
    msg = (
        f"╔══════════════════════════╗\n"
        f"{t(uid, 'receipt_title')}\n"
        f"╚══════════════════════════╝\n\n"
        f"{t(uid, 'receipt_instructions')}\n\n"
        f"{t(uid, 'waiting_receipt')}"
    )
    kb = [[InlineKeyboardButton(t(uid, "cancel_upload"), callback_data="cancel_upload")]]
    await update.effective_message.reply_text(
        msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN
    )

async def cancel_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users_sending_receipt.pop(uid, None)
    try:
        await update.effective_message.delete()
    except Exception:
        pass
    await update.effective_message.reply_text(t(uid, "upload_cancelled"), parse_mode=ParseMode.MARKDOWN)

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
            await update.effective_message.reply_text(t(uid, "send_photo_pdf"), parse_mode=ParseMode.MARKDOWN)
            return
        
        users_sending_receipt.pop(uid, None)
        
        order_id = context.user_data.get("last_order_id", "N/A")
        total = context.user_data.get("last_total", 0)
        order_items = list(user_orders.get(uid, []))
        user_orders[uid] = []
        
        await update.effective_message.reply_text(
            f"╔══════════════════════════╗\n"
            f"{t(uid, 'receipt_received')}\n"
            f"╚══════════════════════════╝\n\n"
            f"{t(uid, 'order_id', id=order_id)}\n"
            f"{t(uid, 'admin_total', total=total)}\n\n"
            f"{t(uid, 'receipt_thanks', name=get_restaurant_name(uid))}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t(uid, "btn_back_main"), callback_data="back_main")]
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
                    f"🌐 Lang: {get_lang(uid)}\n"
                    f"💰 Total: *{total} ETB*\n\n"
                    f"*Items:*\n{items_text}\n\n"
                    f"📎 Receipt: `{path}`"
                ),
                parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        logger.error(f"Receipt error: {e}")
        await update.effective_message.reply_text(t(uid, "receipt_failed"))

# ==================== OTHER PAGES ====================
async def show_gallery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not os.path.exists(IMAGES_FOLDER):
        await update.effective_message.reply_text(t(uid, "no_images"))
        return
    files = [f for f in os.listdir(IMAGES_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
    if not files:
        await update.effective_message.reply_text(t(uid, "no_images"))
        return
    img = random.choice(files)
    try:
        with open(os.path.join(IMAGES_FOLDER, img), "rb") as f:
            await update.effective_message.reply_photo(
                photo=f,
                caption=(
                    f"📸 *{get_restaurant_name(uid)}*\n"
                    f"{divider('─')}\n"
                    f"🍽️ {get_restaurant_tagline(uid)}\n"
                    f"⭐ {get_restaurant_rating(uid)}"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄", callback_data="gallery")],
                    [InlineKeyboardButton(t(uid, "btn_back_main"), callback_data="back_main")]
                ]),
                parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        await update.effective_message.reply_text(f"❌ Error: {e}")

async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    msg = (
        f"╔══════════════════════════╗\n"
        f"{t(uid, 'about_title')}\n"
        f"╚══════════════════════════╝\n\n"
        f"🍽️ *{get_restaurant_name(uid)}*\n"
        f"_{get_restaurant_tagline(uid)}_\n\n"
        f"{t(uid, 'about_desc')}\n\n"
        f"{divider()}\n"
        f"⭐ {get_restaurant_rating(uid)}\n"
        f"📞 `{RESTAURANT_INFO['phone']}`\n"
        f"🕐 {get_restaurant_hours(uid)}\n"
        f"📍 {get_restaurant_address(uid)}\n"
        f"📧 `{RESTAURANT_INFO['email']}`\n"
        f"{divider()}\n\n"
        f"{t(uid, 'follow_us')}"
    )
    kb = [
        [InlineKeyboardButton("📱 Telegram", url=RESTAURANT_INFO["telegram"])],
        [InlineKeyboardButton("📘 Facebook", url=RESTAURANT_INFO["facebook"])],
        [InlineKeyboardButton(t(uid, "btn_back_main"), callback_data="back_main")]
    ]
    await update.effective_message.reply_text(
        msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN
    )

async def show_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    msg = (
        f"╔══════════════════════════╗\n"
        f"{t(uid, 'location_title')}\n"
        f"╚══════════════════════════╝\n\n"
        f"🏠 *{get_restaurant_name(uid)}*\n\n"
        f"📍 {get_restaurant_address(uid)}\n\n"
        f"{t(uid, 'location_desc')}\n\n"
        f"{t(uid, 'location_hours')}\n"
        f"   {get_restaurant_hours(uid)}\n\n"
        f"{t(uid, 'location_parking')}"
    )
    kb = [
        [InlineKeyboardButton(t(uid, "open_maps"), url="https://maps.google.com/?q=Bahir+Dar,Ethiopia")],
        [InlineKeyboardButton(t(uid, "btn_back_main"), callback_data="back_main")]
    ]
    await update.effective_message.reply_text(
        msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN
    )

async def show_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    msg = (
        f"╔══════════════════════════╗\n"
        f"{t(uid, 'contact_title')}\n"
        f"╚══════════════════════════╝\n\n"
        f"{t(uid, 'contact_desc')}\n\n"
        f"{divider()}\n"
        f"{t(uid, 'contact_telegram')}\n"
        f"   {RESTAURANT_INFO['admin_telegram']}\n\n"
        f"{t(uid, 'contact_phone')}\n"
        f"   `{RESTAURANT_INFO['phone']}`\n\n"
        f"{t(uid, 'contact_email')}\n"
        f"   `{RESTAURANT_INFO['email']}`\n"
        f"{divider()}\n\n"
        f"{t(uid, 'contact_response')}"
    )
    kb = [
        [InlineKeyboardButton(t(uid, "message_admin"), url=RESTAURANT_INFO["admin_telegram"])],
        [InlineKeyboardButton(t(uid, "copy_phone"), callback_data="copy_phone_")],
        [InlineKeyboardButton(t(uid, "btn_back_main"), callback_data="back_main")]
    ]
    await update.effective_message.reply_text(
        msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN
    )

# ==================== BACK TO MAIN ====================
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Compatibility wrapper — sends welcome screen with logo."""
    await send_welcome(update, context)

# ==================== COMMANDS ====================
async def menu_command(u, c): await show_menu(u, c)
async def order_command(u, c): await show_order_categories(u, c)
async def gallery_command(u, c): await show_gallery(u, c)
async def about_command(u, c): await show_about(u, c)
async def location_command(u, c): await show_location(u, c)
async def contact_command(u, c): await show_contact(u, c)
async def cart_command(u, c): await view_cart(u, c)

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_language_selector(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = (
        f"╔══════════════════════════╗\n"
        f"{t(uid, 'help_title')}\n"
        f"╚══════════════════════════╝\n\n"
        f"{t(uid, 'help_commands')}\n\n"
        f"/start    – {t(uid, 'main_menu_title').replace('*','').replace('🏠','').strip()}\n"
        f"/menu     – {t(uid, 'btn_menu').replace('🍽️','').strip()}\n"
        f"/order    – {t(uid, 'btn_order').replace('🛒','').strip()}\n"
        f"/cart     – {t(uid, 'btn_cart').replace('🛒','').strip()}\n"
        f"/gallery  – {t(uid, 'btn_gallery').replace('📸','').strip()}\n"
        f"/about    – {t(uid, 'btn_about').replace('ℹ️','').strip()}\n"
        f"/location – {t(uid, 'btn_location').replace('📍','').strip()}\n"
        f"/contact  – {t(uid, 'btn_contact').replace('📞','').strip()}\n"
        f"/language – {t(uid, 'btn_language').replace('🌐','').strip()}\n"
        f"/help     – {t(uid, 'btn_help').replace('❓','').strip()}\n\n"
        f"{divider()}\n"
        f"{t(uid, 'help_tips')}\n\n"
        f"{t(uid, 'help_contact', link=RESTAURANT_INFO['admin_telegram'])}"
    )
    kb = [[InlineKeyboardButton(t(uid, "btn_back_main"), callback_data="back_main")]]
    await update.effective_message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN
    )

# ==================== TEXT MESSAGE HANDLER ====================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()
    
    if uid not in user_languages:
        await send_language_selector(update, context)
        return
    
    await update.message.reply_text(
        t(uid, "not_understood", text=text),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(t(uid, "btn_back_main"), callback_data="back_main")],
            [InlineKeyboardButton(t(uid, "btn_help"), callback_data="help")]
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
        BotCommand("language", "🌐 Change language"),
        BotCommand("help", "❓ Help"),
    ]
    await app.bot.set_my_commands(commands, scope=BotCommandScopeDefault())

# ==================== ERROR HANDLER ====================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}", exc_info=True)

# ==================== MAIN ====================
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("order", order_command))
    app.add_handler(CommandHandler("cart", cart_command))
    app.add_handler(CommandHandler("gallery", gallery_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("location", location_command))
    app.add_handler(CommandHandler("contact", contact_command))
    app.add_handler(CommandHandler("language", language_command))
    app.add_handler(CommandHandler("help", help_command))
    
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_payment_receipt))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)
    
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
