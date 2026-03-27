import random
import os
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

# Store user states
user_data = {}

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🎲 Random Number", callback_data="number"),
            InlineKeyboardButton("👥 Pick People", callback_data="people"),
        ],
        [
            InlineKeyboardButton("🪙 Coin Flip", callback_data="coin"),
            InlineKeyboardButton("🎲 Dice Roll", callback_data="dice"),
        ],
        [
            InlineKeyboardButton("🎯 Random Choice", callback_data="choice"),
            InlineKeyboardButton("🔀 Shuffle List", callback_data="shuffle"),
        ],
        [
            InlineKeyboardButton("👥 Random Teams", callback_data="teams"),
            InlineKeyboardButton("🔐 Random Password", callback_data="password"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Choose a feature:",
        reply_markup=reply_markup
    )

# Button Click Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "number":
        user_data[query.from_user.id] = {"state": "number_start"}
        await query.message.reply_text("Enter start number:")

    elif query.data == "people":
        user_data[query.from_user.id] = {"state": "people_names"}
        await query.message.reply_text(
            "Send names separated by comma or new line:"
        )

    elif query.data == "coin":
        result = random.choice(["Heads", "Tails"])
        await query.message.reply_text(f"🪙 Coin Flip: {result}")
        # Ask if want another task
        user_data[query.from_user.id] = {"state": "ask_again"}
        keyboard = [
            [
                InlineKeyboardButton("Yes", callback_data="yes"),
                InlineKeyboardButton("No", callback_data="no"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "Do you want to do another task?",
            reply_markup=reply_markup
        )

    elif query.data == "dice":
        user_data[query.from_user.id] = {"state": "dice_sides"}
        await query.message.reply_text("Enter number of sides (default 6):")

    elif query.data == "choice":
        user_data[query.from_user.id] = {"state": "choice_options"}
        await query.message.reply_text("Enter options separated by comma or new line:")

    elif query.data == "shuffle":
        user_data[query.from_user.id] = {"state": "shuffle_list"}
        await query.message.reply_text("Enter list items separated by comma or new line:")

    elif query.data == "teams":
        user_data[query.from_user.id] = {"state": "teams_names"}
        await query.message.reply_text("Enter names separated by comma or new line:")

    elif query.data == "password":
        user_data[query.from_user.id] = {"state": "password_length"}
        await query.message.reply_text("Enter password length (default 8):")

    elif query.data == "yes":
        user_data[query.from_user.id] = {"state": "start"}
        keyboard = [
            [
                InlineKeyboardButton("🎲 Random Number", callback_data="number"),
                InlineKeyboardButton("👥 Pick People", callback_data="people"),
            ],
            [
                InlineKeyboardButton("🪙 Coin Flip", callback_data="coin"),
                InlineKeyboardButton("🎲 Dice Roll", callback_data="dice"),
            ],
            [
                InlineKeyboardButton("🎯 Random Choice", callback_data="choice"),
                InlineKeyboardButton("🔀 Shuffle List", callback_data="shuffle"),
            ],
            [
                InlineKeyboardButton("👥 Random Teams", callback_data="teams"),
                InlineKeyboardButton("🔐 Random Password", callback_data="password"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            "Choose a feature:",
            reply_markup=reply_markup
        )

    elif query.data == "no":
        await query.message.edit_text("Goodbye!")
        user_data.pop(query.from_user.id, None)

# Message Handler
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in user_data:
        return

    state = user_data[user_id]["state"]

    # --- NUMBER FLOW ---
    if state == "number_start":
        try:
            user_data[user_id]["start"] = int(text)
            user_data[user_id]["state"] = "number_end"
            await update.message.reply_text("Enter end number:")
        except ValueError:
            await update.message.reply_text("Please enter a valid number.")

    elif state == "number_end":
        try:
            user_data[user_id]["end"] = int(text)
            user_data[user_id]["state"] = "number_count"
            await update.message.reply_text("How many numbers to pick?")
        except ValueError:
            await update.message.reply_text("Please enter a valid number.")

    elif state == "number_count":
        try:
            count = int(text)
            start = user_data[user_id]["start"]
            end = user_data[user_id]["end"]
            numbers = list(range(start, end + 1))
            if count > len(numbers):
                await update.message.reply_text("Cannot pick more numbers than available in the range.")
                return
            result = random.sample(numbers, count)
            await update.message.reply_text(
                f"🎲 Selected Numbers:\n{result}"
            )
            # Ask if want another task
            user_data[user_id]["state"] = "ask_again"
            keyboard = [
                [
                    InlineKeyboardButton("Yes", callback_data="yes"),
                    InlineKeyboardButton("No", callback_data="no"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Do you want to do another task?",
                reply_markup=reply_markup
            )
        except ValueError:
            await update.message.reply_text("Please enter a valid number.")

    # --- PEOPLE FLOW ---
    elif state == "people_names":
        names = [n.strip() for n in text.replace("\n", ",").split(",") if n.strip()]
        if not names:
            await update.message.reply_text("Please provide at least one name.")
            return
        user_data[user_id]["names"] = names
        user_data[user_id]["state"] = "people_count"
        await update.message.reply_text("How many people to pick?")

    elif state == "people_count":
        try:
            count = int(text)
            names = user_data[user_id]["names"]
            if count > len(names):
                await update.message.reply_text("Cannot pick more people than available names.")
                return
            selected = random.sample(names, count)
            await update.message.reply_text(
                "👥 Selected People:\n" + "\n".join(selected)
            )
            # Ask if want another task
            user_data[user_id]["state"] = "ask_again"
            keyboard = [
                [
                    InlineKeyboardButton("Yes", callback_data="yes"),
                    InlineKeyboardButton("No", callback_data="no"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Do you want to do another task?",
                reply_markup=reply_markup
            )
        except ValueError:
            await update.message.reply_text("Please enter a valid number.")

    # --- DICE FLOW ---
    elif state == "dice_sides":
        try:
            sides = int(text) if text.strip() else 6
            if sides <= 1:
                await update.message.reply_text("Number of sides must be greater than 1.")
                return
            result = random.randint(1, sides)
            await update.message.reply_text(f"🎲 Dice Roll ({sides} sides): {result}")
            # Ask if want another task
            user_data[user_id]["state"] = "ask_again"
            keyboard = [
                [
                    InlineKeyboardButton("Yes", callback_data="yes"),
                    InlineKeyboardButton("No", callback_data="no"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Do you want to do another task?",
                reply_markup=reply_markup
            )
        except ValueError:
            await update.message.reply_text("Please enter a valid number.")

    # --- CHOICE FLOW ---
    elif state == "choice_options":
        options = [o.strip() for o in text.replace("\n", ",").split(",") if o.strip()]
        if not options:
            await update.message.reply_text("Please provide at least one option.")
            return
        result = random.choice(options)
        await update.message.reply_text(f"🎯 Random Choice: {result}")
        # Ask if want another task
        user_data[user_id]["state"] = "ask_again"
        keyboard = [
            [
                InlineKeyboardButton("Yes", callback_data="yes"),
                InlineKeyboardButton("No", callback_data="no"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Do you want to do another task?",
            reply_markup=reply_markup
        )

    # --- SHUFFLE FLOW ---
    elif state == "shuffle_list":
        items = [i.strip() for i in text.replace("\n", ",").split(",") if i.strip()]
        if not items:
            await update.message.reply_text("Please provide at least one item.")
            return
        random.shuffle(items)
        await update.message.reply_text("🔀 Shuffled List:\n" + "\n".join(items))
        # Ask if want another task
        user_data[user_id]["state"] = "ask_again"
        keyboard = [
            [
                InlineKeyboardButton("Yes", callback_data="yes"),
                InlineKeyboardButton("No", callback_data="no"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Do you want to do another task?",
            reply_markup=reply_markup
        )

    # --- TEAMS FLOW ---
    elif state == "teams_names":
        names = [n.strip() for n in text.replace("\n", ",").split(",") if n.strip()]
        if not names:
            await update.message.reply_text("Please provide at least one name.")
            return
        user_data[user_id]["names"] = names
        user_data[user_id]["state"] = "teams_count"
        await update.message.reply_text("How many teams?")

    elif state == "teams_count":
        try:
            num_teams = int(text)
            if num_teams <= 0 or num_teams > len(user_data[user_id]["names"]):
                await update.message.reply_text("Invalid number of teams. Must be between 1 and the number of names.")
                return
            names = user_data[user_id]["names"]
            random.shuffle(names)
            teams = [names[i::num_teams] for i in range(num_teams)]
            response = ""
            for idx, team in enumerate(teams, 1):
                response += f"Team {idx}: {', '.join(team)}\n"
            await update.message.reply_text(f"👥 Random Teams:\n{response}")
            # Ask if want another task
            user_data[user_id]["state"] = "ask_again"
            keyboard = [
                [
                    InlineKeyboardButton("Yes", callback_data="yes"),
                    InlineKeyboardButton("No", callback_data="no"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Do you want to do another task?",
                reply_markup=reply_markup
            )
        except ValueError:
            await update.message.reply_text("Please enter a valid number.")

    # --- PASSWORD FLOW ---
    elif state == "password_length":
        try:
            length = int(text) if text.strip() else 8
            if length <= 0:
                await update.message.reply_text("Length must be positive.")
                return
            chars = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(random.choice(chars) for _ in range(length))
            await update.message.reply_text(f"🔐 Random Password: {password}")
            # Ask if want another task
            user_data[user_id]["state"] = "ask_again"
            keyboard = [
                [
                    InlineKeyboardButton("Yes", callback_data="yes"),
                    InlineKeyboardButton("No", callback_data="no"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Do you want to do another task?",
                reply_markup=reply_markup
            )
        except ValueError:
            await update.message.reply_text("Please enter a valid number.")

# Main Function
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()