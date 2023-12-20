import telebot
from telebot import types, TeleBot
import time
import matplotlib.pyplot as plt
import io
import json
import re
import os
from collections import Counter
from datetime import datetime
# Initialize the Telegram bot (add your TOKEN)
bot: TeleBot = telebot.TeleBot(" ")
# Global variables
username = None
nickname = None
WORD_ENTER, COUNT_RESULTS = range(2)

filename = None


# Handle the /start command
@bot.message_handler(commands=['start'])
def start(message):
    # Send a welcome message and request the user to share their Telegram data file
    bot.send_message(message.chat.id,
                     f"👋 Hello there! Welcome aboard! 🚀\nCould you please share your " f"Telegram data file with us? We prefer it in JSON format. Thanks a bunch!\n If "f"you're not sure how to do it 🤷, just type /help")


# Handle the /help command
@bot.message_handler(commands=['help'])
def help(message):
    # Provide help text with a link to a tutorial on how to download Telegram data
    help_text = (
        "To learn how to download your Telegram data, check out this helpful tutorial 🎥:  [link]("
        "https://www.youtube.com/watch?v=fjpojvyxgtQ)\n\n"
        "Sending your data as a JSON file would be greatly appreciated and will expedite the process. 💨 Thanks a "
        "bunch! 🙏🚀"

    )
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")


# Handle all messages to capture user information
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    global nickname
    global username

    username = message.from_user.username
    nickname = message.from_user.first_name or message.from_user.last_name


# Handle files sent by the user
@bot.message_handler(content_types=["document"])
def handle_file(message):
    try:
        global filename
        # Check if the file is a JSON file
        if not message.document.file_name.endswith(".json"):
            bot.send_message(message.chat.id, "Please send a valid JSON file.")
            return

        # Analyze the JSON file and prepare for further actions
        analysis_message = bot.send_message(message.chat.id,
                                            "Analyzing your JSON file... ⏳\n\n<b><i>It will take 20-30 seconds</i></b>",
                                            parse_mode="HTML")
        # To reduce CPU Usage (or just delaying message)
        time.sleep(0)

        # Choose a filename based on available information
        global nickname
        global username
        if nickname:
            filename = f"{username}.json"
        elif username:
            filename = f"{nickname}.json"
        else:
            unknown_file_count = 1
            filename = f"user{unknown_file_count}.json"

        # Download and save message file with chosen filename
        file_info = bot.get_file(message.document.file_id)
        message_file = bot.download_file(file_info.file_path)
        with open(filename, "wb") as fhandle:
            fhandle.write(message_file)

        # Delete the "Analyzing..." message
        bot.delete_message(message.chat.id, analysis_message.message_id)

        # Add a delay before sending the analysis options
        time.sleep(0)

        markup = types.InlineKeyboardMarkup()
        # Inline buttons with callback data
        markup.add(types.InlineKeyboardButton("Total messages", callback_data="total_messages"))
        markup.add(types.InlineKeyboardButton("Sent vs. received", callback_data="sent_received"))
        markup.add(types.InlineKeyboardButton("Word frequency", callback_data="word_freq"))
        markup.add(types.InlineKeyboardButton("Most used emoji", callback_data="used_emoji"))
        markup.add(types.InlineKeyboardButton("Most active days", callback_data="active_days"))
        markup.add(types.InlineKeyboardButton("Chat Champions", callback_data="chat_champs"))
        markup.add(types.InlineKeyboardButton("Peak Hours", callback_data="activity"))
        markup.add(types.InlineKeyboardButton("Forwarded from", callback_data="forwarded_from"))
        markup.add(types.InlineKeyboardButton("Search word", callback_data="search"))

        bot.reply_to(message, "Choose what to analyze:", reply_markup=markup)

    except Exception as e:
        # Handle any errors that occur during the process
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")


# Handle callback queries for different analysis options
@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    # Define global variables
    global nickname
    global username
    global filename
    # Choose a filename based on available information
    if nickname:
        filename = f"{username}.json"
    elif username:
        filename = f"{nickname}.json"
    else:
        unknown_file_count = 1
        filename = f"user{unknown_file_count}.json"

    # Analyze total message count and send
    if callback.data == "total_messages":
        total_message_count = 0
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            for chat in data['chats']['list']:
                if 'messages' in chat:
                    for message in chat['messages']:
                        if 'type' in message:
                            # Extract and split sentences
                            message_type = message['type']
                            if message_type == "message":
                                total_message_count += 1

        bot.send_message(callback.message.chat.id, f"Total messages: {total_message_count}")

    # Analyze sent vs. received messages and send with pie-chart
    elif callback.data == "sent_received":
        # Initialize variables for counting sent and total messages
        sent_count = 0
        total_message_count = 0
        user = None  # Variable to store the user's name (nickname or username)

        # Open the JSON file for reading
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)  # Load JSON data from the file
            if nickname:
                user = nickname  # Set user to nickname if available
            elif username:
                user = username  # Set user to username if nickname is not available

            # Loop through chats and messages in the JSON data
            for chat in data['chats']['list']:
                if 'messages' in chat:
                    for message in chat['messages']:
                        if 'type' in message:
                            # Check if the message type is 'message'
                            type = message['type']
                            if type == "message":
                                total_message_count += 1  # Increment the total message count

            # Loop through chats and messages again to count sent messages
            for chat in data['chats']['list']:
                if 'messages' in chat:
                    for message in chat['messages']:
                        if 'from' in message:
                            # Extract the sender's name and convert to lowercase
                            message_from = message['from'].lower()
                            if message_from == f"Abrorkhujaᅠ":
                                sent_count += 1  # Increment sent_count if message is from 'Abrorkhujaᅠ'

        # Calculate received messages count
        received_count = total_message_count - sent_count

        # Calculate percentages of sent and received messages
        p_sent_count = round((sent_count / (sent_count + received_count)) * 100, 2)
        p_received_count = round((received_count / (sent_count + received_count)) * 100, 2)

        # Prepare data for a pie chart
        labels = ['Sent messages', 'Received messages']
        sizes = [sent_count, received_count]

        # Create a pie chart using Matplotlib
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')

        # Save the pie chart as an image in a BytesIO buffer
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)

        # Send the pie chart image along with a summary message
        bot.send_photo(
            callback.message.chat.id,
            img_buf,
            f"➡️ Number of sent messages: {sent_count} ({p_sent_count}%)\n"
            f"⬅️ Number of received messages: {received_count} ({p_received_count}%)"
        )

        # Close the Matplotlib plot
        plt.close()

    elif callback.data == "word_freq":
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

        all_word_counts = Counter()

        for chat in data['chats']['list']:
            if 'messages' in chat:
                for message in chat['messages']:
                    if 'text' in message:
                        # Extract and split sentences
                        text = message['text']
                        if isinstance(text, list):
                            # If text is a list of dictionaries, extract the 'text' key from each dictionary
                            texts = [item.get('text', '') for item in text if isinstance(item, dict)]
                            text = ' '.join(texts)
                        else:
                            # If text is a string, leave it as is
                            text = str(text)
                        words = re.findall(r'\b\w+\b', text.lower())
                        all_word_counts.update(words)
        # Get the top 10 most frequently used words
        top_words = all_word_counts.most_common(10)
        # Create a pie chart
        labels, sizes = zip(*top_words)
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        # Save the plot as an image
        image_path = 'word_freq_pie_chart.png'
        plt.savefig(image_path)
        # Close the figure
        plt.close()
        # Construct the text message
        result_message_words = "\n".join(
            [f"{i + 1}) {emoji}: {count} times" for i, (emoji, count) in enumerate(top_words)])
        # Send the text message with the pie chart image
        bot.send_photo(callback.message.chat.id, open(image_path, 'rb'),
                       f"Top 10 used words:\n\n{result_message_words}")

    elif callback.data == "used_emoji":
        with open("result.json", 'r', encoding='utf-8') as file:
            data = json.load(file)

        all_emoji_counts = Counter()

        for chat in data['chats']['list']:
            if 'messages' in chat:
                for message in chat['messages']:
                    if 'text' in message:
                        # Extract and split sentences
                        text = message['text']
                        if isinstance(text, list):
                            # If text is a list of dictionaries, extract the 'text' key from each dictionary
                            texts = [item.get('text', '') for item in text if isinstance(item, dict)]
                            text = ' '.join(texts)
                        else:
                            # If text is a string, leave it as is
                            text = str(text)

                        # Regular expression to find emojis specifically
                        emojis = re.findall(r'[\U0001F000-\U0001F9FF]', text)

                        all_emoji_counts.update(emojis)
        # Get the top 10 most frequently used emojis
        top_emojis = all_emoji_counts.most_common(10)

        # Create a bar chart
        labels, counts = zip(*top_emojis)
        plt.figure(figsize=(10, 6))
        plt.bar(labels, counts, color='skyblue')
        plt.xlabel('Emoji')
        plt.ylabel('Occurrences')
        plt.title('Top 10 most used emojis')

        # Save the bar chart as an image
        chart_image_path = 'top_emojis_bar_chart.png'
        plt.savefig(chart_image_path)

        # Close the plot to avoid displaying it in the console
        plt.close()

        # Construct the text message
        result_message_emoji = "\n".join(
            [f"{i + 1}) {emoji}: {count} times" for i, (emoji, count) in enumerate(top_emojis)])

        # Send the text message with the bar chart image
        bot.send_photo(callback.message.chat.id, open(chart_image_path, 'rb'),
                       f"Top 10 used emojis:\n\n{result_message_emoji}")

    elif callback.data == "chat_champs":
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

        all_user_counts = Counter()

        for chat in data['chats']['list']:
            if 'messages' in chat:
                for message in chat['messages']:
                    if 'from' in message:
                        user = message['from']
                        if user == 'Abrorkhujaᅠ':
                            continue
                        elif isinstance(user, list):
                            users = [item.get('from', '') for item in user if isinstance(item, dict)]
                            user = ' '.join(users)
                        else:
                            user = str(user)

                        all_user_counts.update([user])

        # Get the top 5 most frequently used users
        top_users = all_user_counts.most_common(5)

        # Create a bar chart
        labels, counts = zip(*top_users)
        plt.figure(figsize=(10, 6))
        plt.bar(labels, counts, color='lightgreen')
        plt.xlabel(' ')
        plt.ylabel(' ')
        plt.title('Top 5 most used users')

        # Save the bar chart as an image
        chart_image_path = 'top_users_bar_chart.png'
        plt.savefig(chart_image_path)

        # Close the plot to avoid displaying it in the console
        plt.close()

        # Print the results
        result_message_user = "\n".join(
            [f"{i + 1}) {user}: {count} messages" for i, (user, count) in enumerate(top_users)])

        # Send the text message with the bar chart image
        bot.send_photo(callback.message.chat.id, open(chart_image_path, 'rb'),
                       f"Top 5 Chat Champions:\n\n{result_message_user}")
    elif callback.data == "activity":
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Counter to store the frequency of messages in each hour
        activity_by_hour = Counter()

        for chat in data['chats']['list']:
            if 'messages' in chat:
                for message in chat['messages']:
                    if 'date' in message:
                        # Extract the hour from the timestamp
                        timestamp = int(message['date_unixtime'])
                        hour = datetime.utcfromtimestamp(timestamp).hour

                        # Update the counter
                        activity_by_hour.update([hour])

        # Extract data for plotting
        hours, message_counts = zip(*activity_by_hour.items())

        # Get the top 5 most active daytimes
        top_daytimes = Counter(activity_by_hour).most_common(5)

        # Create a bar graph
        plt.figure(figsize=(10, 6))
        plt.bar(hours, message_counts, color='blue', alpha=0.7)
        plt.xlabel('Hour of the Day')
        plt.ylabel('Message Count')
        plt.title('Message Distribution Throughout the Day')
        plt.xticks(range(24))  # Ensure all hours are shown on the x-axis

        # Save the plot to a BytesIO object
        image_buffer = io.BytesIO()
        plt.savefig(image_buffer, format='png')
        plt.close()

        # Move the cursor to the beginning of the BytesIO object
        image_buffer.seek(0)

        # Create a caption with information about the top 5 most active daytimes
        caption_text = "\n".join(
            [f"{i + 1}) Hour {hour}: {count} messages" for i, (hour, count) in enumerate(top_daytimes)])
        caption_text = f'Top 5 Most Active Daytimes:\n\n{caption_text}'

        # Send both the caption and the image in one message
        bot.send_photo(callback.message.chat.id, photo=image_buffer, caption=caption_text)
    elif callback.data == "forwarded_from":
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

        all_user_counts = Counter()

        for chat in data['chats']['list']:
            if 'messages' in chat:
                for message in chat['messages']:
                    if 'forwarded_from' in message:
                        # Extract and split sentences
                        user = message['forwarded_from']
                        if user == 'Abrorkhujaᅠ':
                            continue
                        elif isinstance(user, list):
                            users = [item.get('forwarded_from', '') for item in user if isinstance(item, dict)]
                            user = ' '.join(users)
                        else:
                            user = str(user)

                        all_user_counts.update([user])

        # Get the top 5 most frequently used users
        top_users = all_user_counts.most_common(5)

        # Create a bar chart
        labels, counts = zip(*top_users)
        plt.figure(figsize=(10, 6))
        plt.bar(labels, counts, color='lightgreen')
        plt.xlabel(' ')
        plt.ylabel(' ')
        plt.title('Top 5 most forwarded from users')

        # Save the bar chart as an image
        chart_image_path = 'top_forwarded_users_bar_chart.png'
        plt.savefig(chart_image_path)

        # Close the plot to avoid displaying it in the console
        plt.close()

        # Print the results
        result_message_forwarded = "\n".join(
            [f"{i + 1}) {user}: {count} messages" for i, (user, count) in enumerate(top_users)])

        # Send the text message with the bar chart image
        bot.send_photo(callback.message.chat.id, open(chart_image_path, 'rb'),
                       f"Top 5 Most Forwarded From Users:\n\n{result_message_forwarded}")


bot.polling(none_stop=True)
