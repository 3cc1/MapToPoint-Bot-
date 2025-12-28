from typing import Final
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from db import init_db
from db import save_event
from db import get_all_events 
from db import get_events_page, get_events_count
import math 
import os 
from typing import Final
from dotenv import load_dotenv
load_dotenv()

TOKEN: Final = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_USERNAME: Final = '@MapToPoint_bot'
NEARBY_WAITING_LOCATION = "NEARBY_WAITING_LOCATION"
PAGE_SIZE = 15 

#Keep track of data
user_states = {}
user_events = {}

#commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states[user_id] = None 
    await update.message.reply_text(
        "Hey! Thanks for starting MapPoint Bot! \n\n"
        "Use /add_event to add an event on the map! \n"
        "Use /help to see instructions."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("To record an event you need to specify: Location, Time, Description, Category, User ID, Media")

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Custom Command!")

async def add_event_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user_states[user_id] = 'WAITING_LOCATION'
    user_events[user_id] = {}

    await update.message.reply_text(
        "📍 Please send the location of the event."
    )
# Responses

def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hey There'

    return 'I do not understand what you wrote'

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2) 
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def format_events(events, page, total_pages):
    text = f"Events (Page{page + 1}/{total_pages}) \n\n"

    for i, (lat, lng, desc, cat, created) in enumerate(events, start = 1):
        text += (
            f"{i}. {created}\n"
            f"   📍 {lat:.5f}, {lng:.5f}\n"
            f"   📝 {desc}\n"
            f"   🏷 {cat}\n\n"
        )
    return text

def pagination_keyboard(page, total_pages):
    buttons = []

    if page > 0:
        buttons.append(
            InlineKeyboardButton("⬅️ Previous", callback_data=f"page_{page - 1}")
        )
        if page < total_pages - 1:
            buttons.append(
                InlineKeyboardButton("Next ➡️", callback_data=f"page_{page + 1}")
            )
        return InlineKeyboardMarkup([buttons]) if buttons else None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id =update.effective_user.id
    text: str = update.message.text

    state = user_states.get(user_id)

    if state == "WAITING_DESCRIPTION":
        user_events[user_id]['description'] = text
        user_states[user_id] = 'WAITING_CATEGORY'

        await update.message.reply_text(
            "Enter a category (Weather, Crime, Sports, etc.) or type 'skip':"
        )

    elif state == "WAITING_CATEGORY":
        if text.lower() == 'skip':
            user_events[user_id]['category'] = 'Uncategorized'
        else:
            user_events[user_id]['category'] = text
        user_states[user_id] = None

        event = user_events[user_id]

        await update.message.reply_text(
            "Event Saved Successfully! \n\n"
            f"Location: {event['latitude']}, {event['longitude']}\n"
            f"Description: {event['description']}\n"
            f"Category: {event['category']}\n"
        )

        save_event(
            user_id=user_id, 
            lat=event["latitude"],
            lng=event["longitude"],
            description=event["description"],
            category=event["category"],
            
        )

        #save to database
        del user_events[user_id]
    else:
        await update.message.reply_text(
            "I don't understand. Use /add_event to begin."
        ) 


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    location = update.message.location 

    if user_states.get(user_id) == "WAITING_LOCATION":
        user_events[user_id]['latitude'] = location.latitude
        user_events[user_id]['longitude'] = location.longitude
        user_states[user_id] = "WAITING_DESCRIPTION"

        await update.message.reply_text(
            "Describe what happened at this location:"
        )
        return 

    if user_states.get(user_id) == NEARBY_WAITING_LOCATION:
        user_lat = location.latitude
        user_lng = location.longitude
        user_lng = location.longitude 
        radius_km = 5 # configurable 

        events = get_all_events()
        nearby = []

        for lat, lng, desc, cat, created in events:
            distance = haversine(user_lat, user_lng, lat, lng)
            if distance <= radius_km:
                nearby.append((distance, desc, cat))
        user_states[user_id] = None

        if not nearby:
            await update.message.reply_text(
                "No events found nearby."
            )
            return
        response = "Nearby Events wuthin 5 km: \n\n"
        for d, desc, cat in sorted(nearby):
            response += f" {desc} ({cat}) - {d:.2f} km \n"

        await update.message.reply_text(response)



async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

async def nearby_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states[user_id] = NEARBY_WAITING_LOCATION

    location_keyboard = KeyboardButton(
        text = "Send My Location",
        request_location = True
    )
    reply_markup = ReplyKeyboardMarkup(
        [[location_keyboard]],
        resize_keyboard= True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "Please send your location to find nearby events:",
        reply_markup = reply_markup
    )

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    page = 0
    total = get_events_count()

    if total == 0:
        await update.message.reply_text("No events have been recorded yet.")
        return
    total_pages = (total - 1) // PAGE_SIZE + 1
    events = get_events_page(PAGE_SIZE, page * PAGE_SIZE)

    text = format_events(events, page, total_pages)
    keyboard = pagination_keyboard(page, total_pages)

    await update.message.reply_text(text, reply_markup = keyboard)


async def list_events_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, page_str = query.data.split('_')
    page = int(page_str)

    total = get_events_count()
    total_pages = (total - 1) // PAGE_SIZE + 1

    events = get_events_page(PAGE_SIZE, page * PAGE_SIZE)

    text = format_events(events, page, total_pages)
    keyboard = pagination_keyboard(page, total_pages)

    await query.edit_message_text(text, reply_markup=keyboard)

if __name__ == '__main__':
    init_db()
    print('Starting Bot...')
    app = Application.builder().token(TOKEN).build()

    #commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('add_event', add_event_command))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler('nearby', nearby_command))
    app.add_handler(CommandHandler('list', list_command))
    app.add_handler(CallbackQueryHandler(list_events_callback, pattern=r"^page_"))
    #messages

    #Errors
    app.add_error_handler(error)
    print('Loading...')
    app.run_polling(poll_interval = 3)

