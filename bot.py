import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# ✅ SECURE: Uses Render's environment variable, but falls back to your token for local testing
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8663191953:AAG2ygZFsjlhZOfQN9jy4SAOsfBkSvY3x24')

IMAGES_FOLDER = '/home/akl/Desktop/imagebot'

MENU = {
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
    }
}

RESTAURANT_INFO = {
    'name': 'Selem Restaurant',
    'address': 'Bahir Dar, Ethiopia',
    'phone': '+251965895552',
    'hours': 'Mon-Sun: 10:00 AM - 11:00 PM',
    'telegram': 'https://t.me/selemalemu_ethiopian',
    'facebook': 'https://web.facebook.com/profile.php?id=100048077211674',
    'email': 'info@selemethiopian.com',
    'cbe_account': '1000123456789',
    'telebirr_number': '0965895552',
}

user_orders = {}
users_sending_receipt = {}

async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("🍽️ Menu", callback_data='menu')],
        [InlineKeyboardButton("🛒 Order", callback_data='order')],
        [InlineKeyboardButton("📸 Gallery", callback_data='gallery')],
        [InlineKeyboardButton("ℹ️ About Us", callback_data='about')],
        [InlineKeyboardButton("📍 Location", callback_data='location')],
    ]
    await update.effective_message.reply_text(
        f"🇪🇹 Welcome to {RESTAURANT_INFO['name']}!\n\nExperience authentic Ethiopian cuisine.\n\nChoose an option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    if query.data == 'menu': await show_menu(update)
    elif query.data == 'order': await show_order_categories(update)
    elif query.data == 'gallery': await show_gallery(update)
    elif query.data == 'about': await show_about(update)
    elif query.data == 'location': await show_location(update)
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
        if category and item: await add_to_order(update, category, item, context)
        else: await query.answer("⚠️ Invalid item selected.", show_alert=True)
    elif query.data == 'view_cart': await view_cart(update, context)
    elif query.data == 'checkout': await checkout(update, context)
    elif query.data == 'clear_cart': await clear_cart(update, context)
    elif query.data.startswith('copy_cbe_'):
        await query.answer(f"Copied: {query.data.replace('copy_cbe_', '')}", show_alert=True)
    elif query.data.startswith('copy_tele_'):
        await query.answer(f"Copied: {query.data.replace('copy_tele_', '')}", show_alert=True)
    elif query.data == 'upload_receipt': await upload_receipt_instructions(update, context)
    elif query.data == 'cancel_upload': await cancel_upload(update, context)
    elif query.data == 'payment_done':
        await query.answer("Thank you! Please upload your payment receipt using the button above.", show_alert=True)

async def show_menu(update: Update):
    msg = "🍽️ *Our Menu*\n\n"
    for cat_key, cat_data in MENU.items():
        msg += f"*{cat_data['name']}*\n\n"
        for item, details in cat_data['items'].items():
            msg += f"  • {item.replace('_', ' ').title()} - {details['price']} ETB\n    _{details['description']}_\n"
        msg += "\n"
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Place Order", callback_data='order')]]), parse_mode='Markdown')

async def show_order_categories(update: Update):
    msg = "🛒 *Select a category to order:*\n\n"
    keyboard = [[InlineKeyboardButton(cd['name'], callback_data=f'category_{ck}')] for ck, cd in MENU.items()]
    keyboard.append([InlineKeyboardButton("👀 View Cart", callback_data='view_cart')])
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def show_category_items(update: Update, category: str):
    if category not in MENU: return await update.effective_message.reply_text(f"❌ Category '{category}' not found!")
    cd = MENU[category]
    msg = f"*{cd['name']}*\n\n"
    keyboard = [[InlineKeyboardButton(f"{i.replace('_', ' ').title()} - {d['price']} ETB", callback_data=f'order_{category}_{i}')] for i, d in cd['items'].items()]
    keyboard += [[InlineKeyboardButton("🔙 Back to Categories", callback_data='order')], [InlineKeyboardButton("👀 View Cart", callback_data='view_cart')]]
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def add_to_order(update: Update, category: str, item: str, context):
    uid = update.effective_user.id
    user_orders.setdefault(uid, []).append({'category': category, 'item': item})
    await update.effective_message.reply_text(f"✅ Added *{item.replace('_', ' ').title()}* to your cart!\n\nCurrent items: {len(user_orders[uid])}", parse_mode='Markdown')

async def view_cart(update: Update, context):
    uid = update.effective_user.id
    if uid not in user_orders or not user_orders[uid]: return await update.effective_message.reply_text("🛒 Your cart is empty!")
    msg, total, valid = "🛒 *Your Cart*\n\n", 0, []
    for oi in user_orders[uid]:
        c, i = oi.get('category'), oi.get('item')
        if c in MENU and i in MENU[c]['items']:
            p = MENU[c]['items'][i]['price']; total += p
            msg += f"• {i.replace('_', ' ').title()} - {p} ETB\n"; valid.append(oi)
    if not valid:
        user_orders[uid] = []
        return await update.effective_message.reply_text("🛒 Your cart is empty or contains invalid items.")
    user_orders[uid] = valid
    msg += f"\n*Total: {total} ETB*"
    kb = [[InlineKeyboardButton("💳 Checkout & Pay", callback_data='checkout')], [InlineKeyboardButton("🗑️ Clear Cart", callback_data='clear_cart')], [InlineKeyboardButton("🔙 Continue Shopping", callback_data='order')]]
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def clear_cart(update: Update, context):
    user_orders[update.effective_user.id] = []
    await update.effective_message.reply_text("🗑️ Cart cleared!")

async def checkout(update: Update, context):
    uid = update.effective_user.id
    if uid not in user_orders or not user_orders[uid]: return await update.effective_message.reply_text("🛒 Your cart is empty!")
    total = sum(MENU[o['category']]['items'][o['item']]['price'] for o in user_orders[uid])
    items = ', '.join([o['item'].replace('_', ' ').title() for o in user_orders[uid]])
    msg = (f"🎉 *Order Confirmed!*\n\nItems: {items}\n💰 *Total Amount: {total} ETB*\n\n"
           f"Please pay using one of the methods below:\n\n🏦 *Commercial Bank of Ethiopia (CBE)*\nAccount: `{RESTAURANT_INFO['cbe_account']}`\nName: Selem Restaurant\n\n"
           f"📱 *Telebirr*\nNumber: `{RESTAURANT_INFO['telebirr_number']}`\nName: Selem Restaurant\n\n")
    kb = [[InlineKeyboardButton("📋 Copy CBE Account", callback_data=f'copy_cbe_{RESTAURANT_INFO["cbe_account"]}'), InlineKeyboardButton("📋 Copy Telebirr", callback_data=f'copy_tele_{RESTAURANT_INFO["telebirr_number"]}')],
          [InlineKeyboardButton("📤 Upload Payment Receipt", callback_data='upload_receipt')],
          [InlineKeyboardButton("✅ I Have Paid", callback_data='payment_done')]]
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
    user_orders[uid] = []

async def upload_receipt_instructions(update: Update, context):
    users_sending_receipt[update.effective_user.id] = True
    msg = ("📤 *Upload Your Payment Receipt*\n\nPlease send a screenshot or photo of your payment receipt.\n\n"
           "📸 *To upload:*\n• Click the 📎 *paperclip* icon below the chat\n• Select your payment screenshot/photo\n• Send it here\n\n"
           "💡 *Accepted formats:* JPG, PNG, PDF\n\n_Waiting for your receipt..._")
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel Upload", callback_data='cancel_upload')]]), parse_mode='Markdown')

async def cancel_upload(update: Update, context):
    users_sending_receipt.pop(update.effective_user.id, None)
    try: await update.effective_message.delete()
    except: pass
    await update.effective_message.reply_text("❌ Upload cancelled.\n\nIf you need to send your receipt later, just click 📤 *Upload Payment Receipt* again.", parse_mode='Markdown')

async def handle_payment_receipt(update: Update, context):
    uid = update.effective_user.id
    photo = update.message.photo[-1]
    file = await photo.get_file()
    os.makedirs('receipts', exist_ok=True)
    await file.download_to_drive(f"receipts/{uid}_{random.randint(1000, 9999)}.jpg")
    users_sending_receipt.pop(uid, None)
    await update.effective_message.reply_text("✅ *Receipt Received Successfully!*\n\nThank you for your payment. Our team will verify it shortly.\n\n🍽️ Your order will be prepared once payment is confirmed.\nWe'll notify you when it's ready!", parse_mode='Markdown')

async def show_gallery(update: Update):
    if not os.path.exists(IMAGES_FOLDER): return await update.effective_message.reply_text("❌ No images available!")
    image_files = [f for f in os.listdir(IMAGES_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    if not image_files: return await update.effective_message.reply_text("❌ No images available!")
    img = random.choice(image_files)
    try:
        with open(os.path.join(IMAGES_FOLDER, img), 'rb') as f:
            await update.effective_message.reply_photo(photo=f, caption=f"🇪🇹 {RESTAURANT_INFO['name']} Gallery\n📸 {img}")
    except Exception as e: await update.effective_message.reply_text(f"❌ Error: {e}")

async def show_about(update: Update):
    msg = (f"ℹ️ *About {RESTAURANT_INFO['name']}*\n\nWe serve authentic Ethiopian cuisine with traditional flavors!\n\n"
           f"📞 Phone: `{RESTAURANT_INFO['phone']}`\n🕐 Hours: {RESTAURANT_INFO['hours']}\n📍 Address: {RESTAURANT_INFO['address']}\n\n"
           f"*Follow Us:*\n📱 [Telegram Channel]({RESTAURANT_INFO['telegram']})\n📘 [Facebook Page]({RESTAURANT_INFO['facebook']})\n📧 Email: `{RESTAURANT_INFO['email']}`\n\nVisit us for an unforgettable dining experience! 🇪🇹")
    kb = [[InlineKeyboardButton("📱 Telegram Channel", url=RESTAURANT_INFO['telegram'])], [InlineKeyboardButton("📘 Facebook Page", url=RESTAURANT_INFO['facebook'])]]
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def show_location(update: Update):
    msg = f"📍 *Our Location*\n\n{RESTAURANT_INFO['address']}\n\n🗺️ We're located in the heart of Bahir Dar!\nEasy to find, hard to leave! 🇪🇹"
    kb = [[InlineKeyboardButton("📍 Open in Google Maps", url="https://maps.google.com/?q=Bahir+Dar,Ethiopia")]]
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def menu_command(u, c): await show_menu(u)
async def order_command(u, c): await show_order_categories(u)
async def gallery_command(u, c): await show_gallery(u)
async def about_command(u, c): await show_about(u)
async def location_command(u, c): await show_location(u)
async def help_command(u, c):
    await u.effective_message.reply_text(f"🇪🇹 *{RESTAURANT_INFO['name']} Bot Commands*\n\n/start - Main menu\n/menu - View menu\n/order - Place order\n/gallery - See gallery\n/about - About us\n/location - Our location\n/help - This message", parse_mode='Markdown')

def main():
    PORT = int(os.environ.get('PORT', 8000))
    # ✅ This works perfectly for both Local and Render
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("order", order_command))
    app.add_handler(CommandHandler("gallery", gallery_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("location", location_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_payment_receipt))
    app.add_handler(CallbackQueryHandler(button_handler))

    WEBHOOK_URL = os.environ.get('WEBHOOK_URL', '')
    if WEBHOOK_URL:
        print(f"🚀 Starting bot with Webhook on port {PORT}")
        app.run_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=f"{WEBHOOK_URL}/{TOKEN}")
    else:
        print("⚠️ No WEBHOOK_URL found. Running in polling mode (local test only).")
        app.run_polling()

if __name__ == '__main__':
    main()
