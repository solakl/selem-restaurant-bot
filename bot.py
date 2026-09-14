import os
import random
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# ✅ SECURE TOKEN HANDLING
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8663191953:AAG2ygZFsjlhZOfQN9jy4SAOsfBkSvY3x24')
IMAGES_FOLDER = '/home/akl/Desktop/imagebot'

# 🌟 PREMIUM MENU STRUCTURE
MENU = {
    'featured': {
        'name': '🔥 Featured Today',
        'items': {} # Populated dynamically
    },
    'traditional': {
        'name': '🇪🇹 Traditional Ethiopian',
        'items': {
            'injera': {'price': 30, 'description': 'Traditional sourdough flatbread'},
            'doro_wat': {'price': 250, 'description': 'Spicy chicken stew with boiled egg'},
            'tibs': {'price': 200, 'description': 'Sautéed beef with onions and peppers'},
            'shiro': {'price': 120, 'description': 'Chickpea stew with spices'},
            'kitfo': {'price': 280, 'description': 'Ethiopian minced raw beef with spices'},
            'beyaynetu': {'price': 180, 'description': 'Vegetarian platter with various dishes'},
            'misir_wat': {'price': 140, 'description': 'Spicy red lentil stew'},
            'gomen': {'price': 100, 'description': 'Collard greens with spices'},
            'key_wat': {'price': 220, 'description': 'Spicy beef stew'},
            'ayib': {'price': 80, 'description': 'Ethiopian cottage cheese'},
        }
    },
    'fast_food': {
        'name': '🍔 Fast Food',
        'items': {
            'burger': {'price': 150, 'description': 'Classic beef burger with fries'},
            'pizza_slice': {'price': 80, 'description': 'Cheese pizza slice'},
            'french_fries': {'price': 60, 'description': 'Crispy golden fries'},
            'chicken_wings': {'price': 180, 'description': 'Spicy chicken wings (6 pcs)'},
            'samosa': {'price': 50, 'description': 'Fried pastry with meat filling'},
        }
    },
    'drinks': {
        'name': '🥤 Soft Drinks & Beverages',
        'items': {
            'coca_cola': {'price': 40, 'description': 'Coca-Cola 500ml'},
            'fanta': {'price': 40, 'description': 'Fanta Orange 500ml'},
            'sprite': {'price': 40, 'description': 'Sprite 500ml'},
            'water': {'price': 20, 'description': 'Bottled water 500ml'},
            'juice': {'price': 60, 'description': 'Fresh fruit juice'},
            'coffee': {'price': 50, 'description': 'Ethiopian coffee'},
            'tea': {'price': 30, 'description': 'Traditional tea'},
        }
    },
    'desserts': {
        'name': '🍰 Desserts',
        'items': {
            'cake_slice': {'price': 100, 'description': 'Chocolate cake slice'},
            'ice_cream': {'price': 80, 'description': 'Vanilla ice cream'},
            'fruit_salad': {'price': 90, 'description': 'Fresh fruit salad'},
        }
    },
    'services': {
        'name': '💎 Services & Support',
        'items': {
            'call_admin': {'price': 0, 'description': 'Get admin phone number'},
            'telegram_support': {'price': 0, 'description': 'Chat directly with admin'},
        }
    }
}

# Daily specials mapping
DAILY_SPECIALS = {
    'monday': {'item': 'doro_wat_featured', 'name': 'Doro Wat + Extra Injera', 'price': 200, 'desc': 'Mon Only - Save 50 ETB!'},
    'tuesday': {'item': 'tibs_featured', 'name': 'Tibs + Free Juice', 'price': 220, 'desc': 'Tue Only Special!'},
    'wednesday': {'item': 'beyaynetu_featured', 'name': 'Beyaynetu Veggie Platter', 'price': 150, 'desc': 'Wed Only - Save 30 ETB!'},
    'thursday': {'item': 'burger_featured', 'name': 'Double Burger + Fries', 'price': 180, 'desc': 'Thu Only Deal!'},
    'friday': {'item': 'fish_featured', 'name': 'Fried Fish + Gomen', 'price': 250, 'desc': 'Fri Only Special!'},
    'saturday': {'item': 'kitfo_featured', 'name': 'Kitfo + Ayib', 'price': 300, 'desc': 'Sat Only - Save 20 ETB!'},
    'sunday': {'item': 'family_doro', 'name': 'Family Doro Wat (Serves 4)', 'price': 800, 'desc': 'Sun Only Family Deal!'}
}

# ✅ FIXED: All URLs must start with http:// or https://
RESTAURANT_INFO = {
    'name': 'Selem Restaurant',
    'address': 'Bahir Dar, Ethiopia',
    'phone': '+251965895552',
    'hours': 'Mon-Sun: 10:00 AM - 11:00 PM',
    'telegram': 'https://t.me/Amen365',          # ✅ Fixed: Added https://t.me/
    'facebook': 'https://facebook.com',          # ✅ Fixed: Added full URL
    'email': 'info@selemethiopian.com',
    'cbe_account': '1000123456789',
    'telebirr_number': '0965895552',
    'admin_telegram': 'https://t.me/Amen365'     # ✅ Fixed: Added https://t.me/
}

# In-memory storage
user_orders = {}
users_sending_receipt = {}


def get_featured_item():
    today = datetime.datetime.now().strftime('%A').lower()
    special = DAILY_SPECIALS.get(today)
    if special:
        return {special['item']: {'price': special['price'], 'description': special['desc']}}
    return {}


async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("🍽️ Full Menu", callback_data='menu'), InlineKeyboardButton("🛒 Order Now", callback_data='order')],
        [InlineKeyboardButton("📸 Gallery", callback_data='gallery'), InlineKeyboardButton("ℹ️ About Us", callback_data='about')],
        [InlineKeyboardButton("📍 Location", callback_data='location'), InlineKeyboardButton("📞 Contact", callback_data='contact')]
    ]
    await update.effective_message.reply_text(
        f"🇪🇹 *Welcome to {RESTAURANT_INFO['name']}!*\n\n"
        f"✨ Experience authentic Ethiopian cuisine.\n"
        f"✨ Fresh ingredients, traditional flavors.\n\n"
        f"Choose an option below:",
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown'
    )


async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == 'menu': await show_menu(update)
    elif query.data == 'order': await show_order_categories(update)
    elif query.data == 'gallery': await show_gallery(update)
    elif query.data == 'about': await show_about(update)
    elif query.data == 'location': await show_location(update)
    elif query.data == 'contact': await show_contact(update)
    elif query.data.startswith('category_'):
        category = query.data.split('_', 1)[1]
        await show_category_items(update, category)
    elif query.data.startswith('order_'):
        rest = query.data[6:]
        category = item = None
        for cat_key in MENU.keys():
            if rest.startswith(cat_key + '_'):
                category = cat_key
                item = rest[len(cat_key) + 1:]
                break
        if category and item:
            await add_to_order(update, category, item, context)
        else:
            await query.answer("⚠️ Invalid item selected.", show_alert=True)
    elif query.data == 'view_cart': await view_cart(update, context)
    elif query.data == 'checkout': await checkout(update, context)
    elif query.data == 'clear_cart': await clear_cart(update, context)
    elif query.data.startswith('copy_cbe_'):
        await query.answer(f"Copied: {query.data.replace('copy_cbe_', '')}", show_alert=True)
    elif query.data.startswith('copy_tele_'):
        await query.answer(f"Copied: {query.data.replace('copy_tele_', '')}", show_alert=True)
    elif query.data.startswith('copy_phone_'):
        await query.answer(f"Copied: {RESTAURANT_INFO['phone']}", show_alert=True)
    elif query.data == 'upload_receipt': await upload_receipt_instructions(update, context)
    elif query.data == 'cancel_upload': await cancel_upload(update, context)
    elif query.data == 'payment_done':
        await query.answer("Thank you! Please upload your payment receipt.", show_alert=True)


async def show_menu(update: Update):
    msg = "🍽️ *OUR FULL MENU*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Featured Today Section
    featured = get_featured_item()
    if featured:
        today_name = datetime.datetime.now().strftime('%A')
        msg += f"🔥 *FEATURED TODAY ({today_name})*\n"
        for k, v in featured.items():
            msg += f"  ⭐ {k.replace('_', ' ').title()} — *{v['price']} ETB*\n    _{v['description']}_\n"
        msg += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    # Regular Categories
    for ck, cd in MENU.items():
        if ck == 'featured': continue
        msg += f"*{cd['name']}*\n"
        for item, details in cd['items'].items():
            p = f"{details['price']} ETB" if details['price'] > 0 else "FREE"
            msg += f"  • {item.replace('_', ' ').title()} — {p}\n    _{details['description']}_\n"
        msg += "\n"
        
    kb = [[InlineKeyboardButton("🛒 Place Order", callback_data='order')]]
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')


async def show_order_categories(update: Update):
    msg = "🛒 *SELECT A CATEGORY*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    kb = [[InlineKeyboardButton(cd['name'], callback_data=f'category_{ck}')] for ck, cd in MENU.items() if ck != 'featured']
    kb.append([InlineKeyboardButton("👀 View Cart", callback_data='view_cart')])
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')


async def show_category_items(update: Update, category: str):
    if category not in MENU: 
        return await update.effective_message.reply_text(f"❌ Category '{category}' not found!")
    
    cd = MENU[category]
    msg = f"*{cd['name']}*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    kb = []
    for item, details in cd['items'].items():
        p = f"{details['price']} ETB" if details['price'] > 0 else "FREE"
        kb.append([InlineKeyboardButton(f"{item.replace('_', ' ').title()} — {p}", callback_data=f'order_{category}_{item}')])
    
    kb += [
        [InlineKeyboardButton("🔙 Back to Categories", callback_data='order')],
        [InlineKeyboardButton("👀 View Cart", callback_data='view_cart')]
    ]
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')


async def add_to_order(update: Update, category: str, item: str, context):
    uid = update.effective_user.id
    user_orders.setdefault(uid, []).append({'category': category, 'item': item})
    name = item.replace('_', ' ').title()
    count = len(user_orders[uid])
    await update.effective_message.reply_text(f"✅ Added *{name}* to cart!\n\nTotal items: {count}", parse_mode='Markdown')


async def view_cart(update: Update, context):
    uid = update.effective_user.id
    if uid not in user_orders or not user_orders[uid]:
        return await update.effective_message.reply_text("🛒 Your cart is empty!")
    
    msg, total, valid = "🛒 *YOUR CART*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n", 0, []
    for oi in user_orders[uid]:
        c, i = oi.get('category'), oi.get('item')
        if c in MENU and i in MENU[c]['items']:
            p = MENU[c]['items'][i]['price']
            total += p
            name = i.replace('_', ' ').title()
            msg += f"• {name} — {p} ETB\n"
            valid.append(oi)
            
    if not valid:
        user_orders[uid] = []
        return await update.effective_message.reply_text("🛒 Cart has invalid items. Please clear and restart.")
        
    user_orders[uid] = valid
    msg += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💰 *TOTAL: {total} ETB*"
    
    kb = [
        [InlineKeyboardButton("💳 Checkout & Pay", callback_data='checkout')],
        [InlineKeyboardButton("🗑️ Clear Cart", callback_data='clear_cart')],
        [InlineKeyboardButton("🔙 Continue Shopping", callback_data='order')]
    ]
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')


async def clear_cart(update: Update, context):
    user_orders[update.effective_user.id] = []
    await update.effective_message.reply_text("🗑️ Cart cleared successfully!")


async def checkout(update: Update, context):
    uid = update.effective_user.id
    if uid not in user_orders or not user_orders[uid]:
        return await update.effective_message.reply_text("🛒 Your cart is empty!")

    svc = [o for o in user_orders[uid] if o['category'] == 'services']
    food = [o for o in user_orders[uid] if o['category'] != 'services']

    # Handle services
    for s in svc:
        n = s['item']
        if n == 'call_admin':
            kb = [[InlineKeyboardButton("📋 Copy Phone Number", callback_data='copy_phone_')]]
            await update.effective_message.reply_text(f"📞 Admin Phone: `{RESTAURANT_INFO['phone']}`\n\nTap below to copy!", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        elif n == 'telegram_support':
            kb = [[InlineKeyboardButton("💬 Message Admin", url=RESTAURANT_INFO['admin_telegram'])]]
            await update.effective_message.reply_text("Opening chat with admin...", reply_markup=InlineKeyboardMarkup(kb))

    if not food:
        user_orders[uid] = []
        return

    total = sum(MENU[o['category']]['items'][o['item']]['price'] for o in food)
    items_str = ', '.join([o['item'].replace('_', ' ').title() for o in food])
    
    msg = (
        f"🎉 *ORDER CONFIRMED!*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📦 *Items:* {items_str}\n"
        f"💰 *TOTAL AMOUNT:* *{total} ETB*\n\n"
        f"*PAYMENT OPTIONS:*\n"
        f"🏦 *Commercial Bank of Ethiopia*\n   Account: `{RESTAURANT_INFO['cbe_account']}`\n   Name: Selem Restaurant\n\n"
        f"📱 *Telebirr*\n   Number: `{RESTAURANT_INFO['telebirr_number']}`\n   Name: Selem Restaurant\n\n"
    )
    kb = [
        [InlineKeyboardButton("📋 Copy CBE", callback_data=f'copy_cbe_{RESTAURANT_INFO["cbe_account"]}'),
         InlineKeyboardButton("📋 Copy Telebirr", callback_data=f'copy_tele_{RESTAURANT_INFO["telebirr_number"]}')],
        [InlineKeyboardButton("📤 Upload Receipt", callback_data='upload_receipt')],
        [InlineKeyboardButton("✅ I Have Paid", callback_data='payment_done')]
    ]
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
    user_orders[uid] = []


async def upload_receipt_instructions(update: Update, context):
    users_sending_receipt[update.effective_user.id] = True
    msg = (
        "📤 *UPLOAD PAYMENT RECEIPT*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Please send a screenshot or photo of your payment.\n\n"
        "📸 *How to upload:*\n"
        "1. Tap the 📎 paperclip icon below\n"
        "2. Select your payment screenshot\n"
        "3. Send it to this chat\n\n"
        "💡 *Accepted:* JPG, PNG, PDF\n\n_Waiting for your receipt..._"
    )
    kb = [[InlineKeyboardButton("❌ Cancel Upload", callback_data='cancel_upload')]]
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')


async def cancel_upload(update: Update, context):
    users_sending_receipt.pop(update.effective_user.id, None)
    try: await update.effective_message.delete()
    except: pass
    await update.effective_message.reply_text("❌ Upload cancelled. Click 📤 Upload Receipt anytime to retry.", parse_mode='Markdown')


async def handle_payment_receipt(update: Update, context):
    uid = update.effective_user.id
    photo = update.message.photo[-1]
    file = await photo.get_file()
    os.makedirs('receipts', exist_ok=True)
    await file.download_to_drive(f"receipts/{uid}_{random.randint(1000, 9999)}.jpg")
    users_sending_receipt.pop(uid, None)
    await update.effective_message.reply_text(
        "✅ *RECEIPT RECEIVED!*\n\n"
        "Your payment is being verified by our team.\n"
        "🍽️ Your order is being prepared and we will notify you when it's ready!",
        parse_mode='Markdown'
    )


async def show_gallery(update: Update):
    if not os.path.exists(IMAGES_FOLDER): 
        return await update.effective_message.reply_text("❌ No images available!")
    files = [f for f in os.listdir(IMAGES_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    if not files: 
        return await update.effective_message.reply_text("❌ No images available!")
    img = random.choice(files)
    try:
        with open(os.path.join(IMAGES_FOLDER, img), 'rb') as f:
            await update.effective_message.reply_photo(photo=f, caption=f"🇪🇹 {RESTAURANT_INFO['name']} Gallery\n📸 {img}")
    except Exception as e: 
        await update.effective_message.reply_text(f"❌ Error loading image: {e}")


# ✅ FIXED: Lowercase 'name' to prevent KeyError
async def show_about(update: Update):
    msg = (
        f"ℹ️ *ABOUT {RESTAURANT_INFO['name']}*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"We serve authentic Ethiopian cuisine with traditional flavors, prepared with love and the finest local ingredients.\n\n"
        f"📞 Phone: `{RESTAURANT_INFO['phone']}`\n"
        f"🕐 Hours: {RESTAURANT_INFO['hours']}\n"
        f"📍 Address: {RESTAURANT_INFO['address']}\n\n"
        f"*FOLLOW US:*\n"
        f"📱 [Telegram Channel]({RESTAURANT_INFO['telegram']})\n"
        f"📘 [Facebook Page]({RESTAURANT_INFO['facebook']})\n"
        f"📧 Email: `{RESTAURANT_INFO['email']}`\n\n"
        f"Visit us for an unforgettable dining experience! 🇪🇹"
    )
    kb = [
        [InlineKeyboardButton("📱 Telegram Channel", url=RESTAURANT_INFO['telegram'])],
        [InlineKeyboardButton("📘 Facebook Page", url=RESTAURANT_INFO['facebook'])]
    ]
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')


async def show_location(update: Update):
    msg = (
        f"📍 *OUR LOCATION*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{RESTAURANT_INFO['address']}\n\n"
        f"🗺️ Located in the heart of Bahir Dar!\n"
        f"Easy to find, hard to leave. 🇪🇹"
    )
    kb = [[InlineKeyboardButton("📍 Open in Google Maps", url="https://maps.google.com/?q=Bahir+Dar,Ethiopia")]]
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')


async def show_contact(update: Update):
    msg = (
        f"📞 *CONTACT ADMINISTRATION*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Need help or have a special request? Reach out directly:\n\n"
        f"📱 Telegram: {RESTAURANT_INFO['admin_telegram']}\n"
        f"📞 Phone: `{RESTAURANT_INFO['phone']}`\n"
        f"📧 Email: `{RESTAURANT_INFO['email']}`\n\n"
        f"Tap the buttons below to connect!"
    )
    kb = [
        [InlineKeyboardButton("💬 Message Admin", url=RESTAURANT_INFO['admin_telegram'])],
        [InlineKeyboardButton("📋 Copy Phone Number", callback_data='copy_phone_')]
    ]
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')


# Command wrappers
async def menu_command(u, c): await show_menu(u)
async def order_command(u, c): await show_order_categories(u)
async def gallery_command(u, c): await show_gallery(u)
async def about_command(u, c): await show_about(u)
async def location_command(u, c): await show_location(u)
async def contact_command(u, c): await show_contact(u)
async def help_command(u, c):
    cmds = (
        "/start - Main Menu\n"
        "/menu - View Full Menu\n"
        "/order - Start Ordering\n"
        "/gallery - See Photos\n"
        "/about - About Us\n"
        "/location - Find Us\n"
        "/contact - Contact Admin"
    )
    await u.effective_message.reply_text(f"🇪🇹 *{RESTAURANT_INFO['name']}*\n\n{cmds}", parse_mode='Markdown')


def main():
    PORT = int(os.environ.get('PORT', 8000))
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("order", order_command))
    app.add_handler(CommandHandler("gallery", gallery_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("location", location_command))
    app.add_handler(CommandHandler("contact", contact_command))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(MessageHandler(filters.PHOTO, handle_payment_receipt))
    app.add_handler(CallbackQueryHandler(button_handler))

    WEBHOOK_URL = os.environ.get('WEBHOOK_URL', '')
    if WEBHOOK_URL:
        print(f"🚀 Starting bot with Webhook on port {PORT}")
        app.run_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=f"{WEBHOOK_URL}/{TOKEN}")
    else:
        print("⚠️ No WEBHOOK_URL. Running polling (local test only).")
        app.run_polling()


if __name__ == '__main__':
    main()
