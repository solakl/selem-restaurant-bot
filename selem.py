from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import os
import random

TOKEN = '8663191953:AAG2ygZFsjlhZOfQN9jy4SAOsfBkSvY3x24'

# Path to your images folder
IMAGES_FOLDER = '/home/akl/Desktop/imagebot'

# Categorized Ethiopian Restaurant Menu
MENU = {
    'traditional': {
        'name': '🇪🇹 Traditional Ethiopian',
        'items': {
            'injera': {'price': 30, 'description': 'Traditional sourdough flatbread', 'image': 'mobra.jpg'},
            'doro_wat': {'price': 250, 'description': 'Spicy chicken stew with boiled egg', 'image': 'photo_2025-01-20_12-13-28.jpg'},
            'tibs': {'price': 200, 'description': 'Sautéed beef with onions and peppers', 'image': 'ChatGPT Image Apr 24, 2026, 10_41_48 AM.png'},
            'shiro': {'price': 120, 'description': 'Chickpea stew with spices', 'image': 'mobra.jpg'},
            'kitfo': {'price': 280, 'description': 'Ethiopian minced raw beef with spices', 'image': 'photo_2025-01-20_12-13-28.jpg'},
            'beyaynetu': {'price': 180, 'description': 'Vegetarian platter with various dishes', 'image': 'ChatGPT Image Apr 24, 2026, 10_41_48 AM.png'},
            'misir_wat': {'price': 140, 'description': 'Spicy red lentil stew', 'image': 'mobra.jpg'},
            'gomen': {'price': 100, 'description': 'Collard greens with spices', 'image': 'photo_2025-01-20_12-13-28.jpg'},
            'key_wat': {'price': 220, 'description': 'Spicy beef stew', 'image': 'ChatGPT Image Apr 24, 2026, 10_41_48 AM.png'},
            'ayib': {'price': 80, 'description': 'Ethiopian cottage cheese', 'image': 'mobra.jpg'},
        }
    },
    'fast_food': {
        'name': '🍔 Fast Food',
        'items': {
            'burger': {'price': 150, 'description': 'Classic beef burger with fries', 'image': 'mobra.jpg'},
            'pizza_slice': {'price': 80, 'description': 'Cheese pizza slice', 'image': 'photo_2025-01-20_12-13-28.jpg'},
            'french_fries': {'price': 60, 'description': 'Crispy golden fries', 'image': 'ChatGPT Image Apr 24, 2026, 10_41_48 AM.png'},
            'chicken_wings': {'price': 180, 'description': 'Spicy chicken wings (6 pcs)', 'image': 'mobra.jpg'},
            'samosa': {'price': 50, 'description': 'Fried pastry with meat filling', 'image': 'photo_2025-01-20_12-13-28.jpg'},
        }
    },
    'drinks': {
        'name': '🥤 Soft Drinks & Beverages',
        'items': {
            'coca_cola': {'price': 40, 'description': 'Coca-Cola 500ml', 'image': 'mobra.jpg'},
            'fanta': {'price': 40, 'description': 'Fanta Orange 500ml', 'image': 'photo_2025-01-20_12-13-28.jpg'},
            'sprite': {'price': 40, 'description': 'Sprite 500ml', 'image': 'ChatGPT Image Apr 24, 2026, 10_41_48 AM.png'},
            'water': {'price': 20, 'description': 'Bottled water 500ml', 'image': 'mobra.jpg'},
            'juice': {'price': 60, 'description': 'Fresh fruit juice', 'image': 'photo_2025-01-20_12-13-28.jpg'},
            'coffee': {'price': 50, 'description': 'Ethiopian coffee', 'image': 'ChatGPT Image Apr 24, 2026, 10_41_48 AM.png'},
            'tea': {'price': 30, 'description': 'Traditional tea', 'image': 'mobra.jpg'},
        }
    },
    'desserts': {
        'name': '🍰 Desserts',
        'items': {
            'cake_slice': {'price': 100, 'description': 'Chocolate cake slice', 'image': 'mobra.jpg'},
            'ice_cream': {'price': 80, 'description': 'Vanilla ice cream', 'image': 'photo_2025-01-20_12-13-28.jpg'},
            'fruit_salad': {'price': 90, 'description': 'Fresh fruit salad', 'image': 'ChatGPT Image Apr 24, 2026, 10_41_48 AM.png'},
        }
    }
}

# Restaurant Info with Payment Details
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

# Get list of image files
IMAGE_FILES = [f for f in os.listdir(IMAGES_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

# User orders storage (in memory)
user_orders = {}

# Track users who are expected to send receipts
users_sending_receipt = {}


async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("🍽️ Menu", callback_data='menu')],
        [InlineKeyboardButton("🛒 Order", callback_data='order')],
        [InlineKeyboardButton("📸 Gallery", callback_data='gallery')],
        [InlineKeyboardButton("ℹ️ About Us", callback_data='about')],
        [InlineKeyboardButton("📍 Location", callback_data='location')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_message.reply_text(
        f"🇪🇹 Welcome to {RESTAURANT_INFO['name']}!\n\n"
        f"Experience authentic Ethiopian cuisine.\n\n"
        f"Choose an option:",
        reply_markup=reply_markup
    )


async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == 'menu':
        await show_menu(update)
    elif query.data == 'order':
        await show_order_categories(update)
    elif query.data == 'gallery':
        await show_gallery(update)
    elif query.data == 'about':
        await show_about(update)
    elif query.data == 'location':
        await show_location(update)
    elif query.data.startswith('category_'):
        category = query.data.split('_', 1)[1]
        await show_category_items(update, category)
    elif query.data.startswith('order_'):
        rest = query.data[6:]
        category = None
        item = None
        for cat_key in MENU.keys():
            if rest.startswith(cat_key + '_'):
                category = cat_key
                item = rest[len(cat_key) + 1:]
                break
        
        if category and item:
            await add_to_order(update, category, item, context)
        else:
            await query.answer("⚠️ Invalid item selected.", show_alert=True)
            
    elif query.data == 'view_cart':
        await view_cart(update, context)
    elif query.data == 'checkout':
        await checkout(update, context)
    elif query.data == 'clear_cart':
        await clear_cart(update, context)
    elif query.data.startswith('copy_cbe_'):
        account = query.data.replace('copy_cbe_', '')
        await query.answer(f"Copied: {account}", show_alert=True)
    elif query.data.startswith('copy_tele_'):
        number = query.data.replace('copy_tele_', '')
        await query.answer(f"Copied: {number}", show_alert=True)
    elif query.data == 'upload_receipt':
        await upload_receipt_instructions(update, context)
    elif query.data == 'cancel_upload':
        await cancel_upload(update, context)
    elif query.data == 'payment_done':
        await query.answer("Thank you! Please upload your payment receipt using the button above. ", show_alert=True)


async def show_menu(update: Update):
    msg = "🍽️ *Our Menu*\n\n"
    for category_key, category_data in MENU.items():
        msg += f"*{category_data['name']}*\n\n"
        for item, details in category_data['items'].items():
            msg += f"  • {item.replace('_', ' ').title()} - {details['price']} ETB\n"
            msg += f"    _{details['description']}_\n"
        msg += "\n"

    keyboard = [[InlineKeyboardButton("🛒 Place Order", callback_data='order')]]
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')


async def show_order_categories(update: Update):
    msg = " *Select a category to order:*\n\n"
    keyboard = []
    for category_key, category_data in MENU.items():
        keyboard.append([InlineKeyboardButton(category_data['name'], callback_data=f'category_{category_key}')])
    keyboard.append([InlineKeyboardButton("👀 View Cart", callback_data='view_cart')])
    
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')


async def show_category_items(update: Update, category: str):
    if category not in MENU:
        await update.effective_message.reply_text(f"❌ Category '{category}' not found!")
        return

    category_data = MENU[category]
    msg = f"*{category_data['name']}*\n\n"

    keyboard = []
    for item, details in category_data['items'].items():
        item_name = item.replace('_', ' ').title()
        keyboard.append([InlineKeyboardButton(f"{item_name} - {details['price']} ETB", callback_data=f'order_{category}_{item}')])

    keyboard.append([InlineKeyboardButton("🔙 Back to Categories", callback_data='order')])
    keyboard.append([InlineKeyboardButton("👀 View Cart", callback_data='view_cart')])
    
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')


async def add_to_order(update: Update, category: str, item: str, context):
    user_id = update.effective_user.id
    if user_id not in user_orders:
        user_orders[user_id] = []

    user_orders[user_id].append({'category': category, 'item': item})
    item_name = item.replace('_', ' ').title()
    
    await update.effective_message.reply_text(
        f"✅ Added *{item_name}* to your cart!\n\n"
        f"Current items: {len(user_orders[user_id])}",
        parse_mode='Markdown'
    )


async def view_cart(update: Update, context):
    user_id = update.effective_user.id

    if user_id not in user_orders or not user_orders[user_id]:
        await update.effective_message.reply_text("🛒 Your cart is empty!")
        return

    msg = "🛒 *Your Cart*\n\n"
    total = 0
    valid_orders = []

    for order_item in user_orders[user_id]:
        category = order_item.get('category')
        item = order_item.get('item')
        
        if category in MENU and item in MENU[category]['items']:
            price = MENU[category]['items'][item]['price']
            total += price
            item_name = item.replace('_', ' ').title()
            msg += f"• {item_name} - {price} ETB\n"
            valid_orders.append(order_item)

    if not valid_orders:
        await update.effective_message.reply_text("🛒 Your cart is empty or contains invalid items. Please clear and start over.")
        user_orders[user_id] = []
        return

    user_orders[user_id] = valid_orders
    msg += f"\n*Total: {total} ETB*"

    keyboard = [
        [InlineKeyboardButton("💳 Checkout & Pay", callback_data='checkout')],
        [InlineKeyboardButton("🗑️ Clear Cart", callback_data='clear_cart')],
        [InlineKeyboardButton("🔙 Continue Shopping", callback_data='order')]
    ]
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')


async def clear_cart(update: Update, context):
    user_id = update.effective_user.id
    user_orders[user_id] = []
    await update.effective_message.reply_text("🗑️ Cart cleared!")


async def checkout(update: Update, context):
    user_id = update.effective_user.id

    if user_id not in user_orders or not user_orders[user_id]:
        await update.effective_message.reply_text("🛒 Your cart is empty!")
        return

    total = sum(MENU[o['category']]['items'][o['item']]['price'] for o in user_orders[user_id])
    order_items = ', '.join([o['item'].replace('_', ' ').title() for o in user_orders[user_id]])

    payment_msg = (
        f" *Order Confirmed!*\n\n"
        f"Items: {order_items}\n"
        f"💰 *Total Amount: {total} ETB*\n\n"
        f"Please pay using one of the methods below:\n\n"
        f"🏦 *Commercial Bank of Ethiopia (CBE)*\n"
        f"Account: `{RESTAURANT_INFO['cbe_account']}`\n"
        f"Name: Selem Restaurant\n\n"
        f"📱 *Telebirr*\n"
        f"Number: `{RESTAURANT_INFO['telebirr_number']}`\n"
        f"Name: Selem Restaurant\n\n"
    )

    keyboard = [
        [InlineKeyboardButton("📋 Copy CBE Account", callback_data=f'copy_cbe_{RESTAURANT_INFO["cbe_account"]}'),
         InlineKeyboardButton("📋 Copy Telebirr", callback_data=f'copy_tele_{RESTAURANT_INFO["telebirr_number"]}')],
        [InlineKeyboardButton("📤 Upload Payment Receipt", callback_data='upload_receipt')],
        [InlineKeyboardButton("✅ I Have Paid", callback_data='payment_done')]
    ]
    
    await update.effective_message.reply_text(payment_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    user_orders[user_id] = []


async def upload_receipt_instructions(update: Update, context):
    """Show instructions for uploading receipt"""
    user_id = update.effective_user.id
    users_sending_receipt[user_id] = True
    
    upload_msg = (
        "📤 *Upload Your Payment Receipt*\n\n"
        "Please send a screenshot or photo of your payment receipt.\n\n"
        "📸 *To upload:*\n"
        "• Click the 📎 *paperclip* icon (or 📷 camera icon) below the chat\n"
        "• Select your payment screenshot/photo from your gallery\n"
        "• Send it to this chat\n\n"
        "💡 *Accepted formats:* JPG, PNG, PDF\n\n"
        "_Waiting for your receipt..._"
    )
    
    keyboard = [
        [InlineKeyboardButton("❌ Cancel Upload", callback_data='cancel_upload')]
    ]
    
    await update.effective_message.reply_text(
        upload_msg, 
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode='Markdown'
    )


async def cancel_upload(update: Update, context):
    """Cancel the receipt upload process"""
    user_id = update.effective_user.id
    if user_id in users_sending_receipt:
        del users_sending_receipt[user_id]
    
    # Delete the instruction message and cancel button
    try:
        await update.effective_message.delete()
    except:
        pass
    
    await update.effective_message.reply_text(
        "❌ Upload cancelled.\n\n"
        "If you need to send your receipt later, just click 📤 *Upload Payment Receipt* button again or send it directly in the chat.",
        parse_mode='Markdown'
    )


async def handle_payment_receipt(update: Update, context):
    """Handle when user sends a photo (payment receipt)"""
    user_id = update.effective_user.id
    
    # Get the photo file
    photo = update.message.photo[-1]  # Get highest resolution
    file = await photo.get_file()
    
    # Save the receipt (optional - you can store it)
    receipt_path = f"receipts/{user_id}_{random.randint(1000, 9999)}.jpg"
    os.makedirs('receipts', exist_ok=True)
    await file.download_to_drive(receipt_path)
    
    # Clear the sending flag
    if user_id in users_sending_receipt:
        del users_sending_receipt[user_id]
    
    # Send confirmation
    await update.effective_message.reply_text(
        "✅ *Receipt Received Successfully!*\n\n"
        "Thank you for your payment. Our team will verify it shortly.\n\n"
        "🍽️ Your order will be prepared once payment is confirmed.\n"
        "We'll notify you when it's ready!\n\n"
        f"📍 Pickup at: {RESTAURANT_INFO['address']}",
        parse_mode='Markdown'
    )


async def show_gallery(update: Update):
    if not IMAGE_FILES:
        await update.effective_message.reply_text("❌ No images available!")
        return

    image_name = random.choice(IMAGE_FILES)
    image_path = os.path.join(IMAGES_FOLDER, image_name)

    try:
        with open(image_path, 'rb') as photo:
            await update.effective_message.reply_photo(
                photo=photo,
                caption=f"🇪🇹 {RESTAURANT_INFO['name']} Gallery\n📸 {image_name}"
            )
    except Exception as e:
        await update.effective_message.reply_text(f" Error: {e}")


async def show_about(update: Update):
    msg = (
        f"ℹ️ *About {RESTAURANT_INFO['name']}*\n\n"
        f"We serve authentic Ethiopian cuisine with traditional flavors!\n\n"
        f"📞 Phone: `{RESTAURANT_INFO['phone']}`\n"
        f"🕐 Hours: {RESTAURANT_INFO['hours']}\n"
        f"📍 Address: {RESTAURANT_INFO['address']}\n\n"
        f"*Follow Us:*\n"
        f"📱 [Telegram Channel]({RESTAURANT_INFO['telegram']})\n"
        f"📘 [Facebook Page]({RESTAURANT_INFO['facebook']})\n"
        f"📧 Email: `{RESTAURANT_INFO['email']}`\n\n"
        f"Visit us for an unforgettable dining experience! 🇪🇹"
    )

    keyboard = [
        [InlineKeyboardButton("📱 Telegram Channel", url=RESTAURANT_INFO['telegram'])],
        [InlineKeyboardButton("📘 Facebook Page", url=RESTAURANT_INFO['facebook'])],
    ]
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')


async def show_location(update: Update):
    msg = (
        f"📍 *Our Location*\n\n"
        f"{RESTAURANT_INFO['address']}\n\n"
        f"️ We're located in the heart of Bahir Dar!\n"
        f"Easy to find, hard to leave! 🇪🇹"
    )
    keyboard = [
        [InlineKeyboardButton("📍 Open in Google Maps", url="https://maps.google.com/?q=Bahir+Dar,Ethiopia")]
    ]
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')


# Command handlers
async def menu_command(update: Update, context):
    await show_menu(update)

async def order_command(update: Update, context):
    await show_order_categories(update)

async def gallery_command(update: Update, context):
    await show_gallery(update)

async def about_command(update: Update, context):
    await show_about(update)

async def location_command(update: Update, context):
    await show_location(update)

async def help_command(update: Update, context):
    msg = (
        f"🇪🇹 *{RESTAURANT_INFO['name']} Bot Commands*\n\n"
        "/start - Main menu\n"
        "/menu - View our categorized menu\n"
        "/order - Place an order\n"
        "/gallery - See our gallery\n"
        "/about - About us & social media\n"
        "/location - Our location\n"
        "/help - This help message"
    )
    await update.effective_message.reply_text(msg, parse_mode='Markdown')


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("order", order_command))
    app.add_handler(CommandHandler("gallery", gallery_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("location", location_command))
    app.add_handler(CommandHandler("help", help_command))

    # Handle payment receipts (photos)
    app.add_handler(MessageHandler(filters.PHOTO, handle_payment_receipt))
    
    # Handle callback queries
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🇪🇹 Selem Restaurant Bot is running...")
    print(" Receipts will be saved in: /opt/receipts/")
    app.run_polling()


if __name__ == '__main__':
    main()
