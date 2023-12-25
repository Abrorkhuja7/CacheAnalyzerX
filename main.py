import telebot
from telebot import types, TeleBot
import time
import matplotlib
import matplotlib.pyplot as plt
import io
import json
import re
from collections import Counter
from datetime import datetime
import calendar
import zipfile

calendar.setfirstweekday(calendar.MONDAY)
matplotlib.use('Agg')
# Initialize the Telegram bot
bot: TeleBot = telebot.TeleBot("YOUR_TOKEN")
# Global variables
username = None
nickname = None
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


# Handle files sent by the user
@bot.message_handler(content_types=["document"])
def handle_file(message):
    try:
        global filename
        global nickname
        global username

        username = message.from_user.username
        nickname = message.from_user.first_name or message.from_user.last_name

        # Check if the file is a ZIP file
        if not message.document.file_name.endswith(".zip"):
            bot.send_message(message.chat.id, "Please send a valid ZIP file.")
            return

        # Analyze the ZIP file and prepare for further actions
        analysis_message = bot.send_message(message.chat.id,
                                            "Analyzing your ZIP file... ⏳\n\n<b><i>It will take 20-30 seconds</i></b>",
                                            parse_mode="HTML")
        # To reduce CPU Usage (or just delaying message)
        time.sleep(0)

        # Choose a filename based on available information
        if username:
            filename = f"{username}.json"
        elif nickname:
            filename = f"{nickname}.json"
        else:
            filename = "default.json"  # Provide a default filename if no username or nickname is available

        # Download the ZIP file
        file_info = bot.get_file(message.document.file_id)
        zip_file = bot.download_file(file_info.file_path)

        # Extract the contents of the ZIP file
        with zipfile.ZipFile(io.BytesIO(zip_file), 'r') as zip_ref:
            # Assume there is only one JSON file in the ZIP for simplicity
            json_filename = zip_ref.namelist()[0]
            json_data = zip_ref.read(json_filename)

        # Convert bytes to string (assumes the content is a valid JSON)
        json_str = json_data.decode('utf-8')

        # Save the JSON data with the chosen filename
        with open(filename, "w", encoding="utf-8") as fhandle:
            fhandle.write(json_str)

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


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    # Define global variables
    global nickname
    global username
    global filename
    # Choose a filename based on available information
    if username:
        filename = f"{username}.json"
    elif nickname:
        filename = f"{nickname}.json"
    else:
        filename = "default.json"
        
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
        print(f"Username: {username}")
        print(f"Nickname: {nickname}")
        bot.send_message(callback.message.chat.id, f"📊 Total messages: {total_message_count}")

    # Analyze sent vs. received messages and send with pie-chart
    elif callback.data == "sent_received":
        # Initialize variables for counting sent and total messages
        sent_count = 0
        total_message_count = 0

        # Open the JSON file for reading
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
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
                            message_from = message['from']
                            if message_from == nickname or message_from == username:
                                sent_count += 1

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

                        # Use an improved regular expression to find emojis specifically
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
                       f"🔝Top 10 used emojis:\n\n{result_message_emoji}")
    elif callback.data == "active_days":
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Counter to store the frequency of messages on each day of the week
        activity_by_day = Counter()

        for chat in data['chats']['list']:
            if 'messages' in chat:
                for message in chat['messages']:
                    if 'date' in message:
                        # Extract the day of the week from the timestamp
                        timestamp = int(message['date_unixtime'])
                        day_of_week = datetime.utcfromtimestamp(timestamp).weekday()

                        # Update the counter
                        activity_by_day.update([day_of_week])

        # Get the names of the days of the week
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Extract data for plotting
        message_counts = [activity_by_day.get(day, 0) for day in range(7)]

        # Find the index of the most active day
        most_active_index = max(range(7), key=message_counts.__getitem__)

        # Define colors for the bar graph
        bar_colors = ['lightskyblue' if i != most_active_index else 'deepskyblue' for i in range(7)]

        # Create a bar graph
        plt.figure(figsize=(10, 6))
        plt.bar(days_of_week, message_counts, color=bar_colors, alpha=0.7)
        plt.xlabel('Day of the Week')
        plt.ylabel('Message Count')
        plt.title('Message Distribution Throughout the Week')

        # Save the plot to a BytesIO object
        image_buffer = io.BytesIO()
        plt.savefig(image_buffer, format='png')
        plt.close()

        # Move the cursor to the beginning of the BytesIO object
        image_buffer.seek(0)

        # Create a caption with information about the count of messages for each day of the week
        caption_text = "\n".join(
            [f"{i + 1}) {days_of_week[day]}: {count} messages {'🌟' if i == most_active_index else ''}" for
             i, (day, count) in
             enumerate(zip(range(7), message_counts))]
        )
        caption_text = f'📊🔝 Message Count for Each Day of the Week:\n\n{caption_text}'

        # Send both the caption and the image in one message
        bot.send_photo(callback.message.chat.id, photo=image_buffer, caption=caption_text)
    elif callback.data == "chat_champs":
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

        all_user_counts = Counter()

        for chat in data['chats']['list']:
            if 'messages' in chat:
                for message in chat['messages']:
                    if 'from' in message:
                        # Extract and split sentences
                        user = message['from']
                        if user == username or user == nickname:
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
        # Print the results
        result_message_user = "\n".join(
            [f"{i + 1}) {user}: {count} messages" for i, (user, count) in enumerate(top_users)])

        # Manually include the bot's name at the end of the message
        # Hyperlink to bot
        # bot_name = "[CacheAnalyzerX](https://t.me/cachestat_bot)"

        # Send the text message with the bar chart image
        bot.send_photo(callback.message.chat.id, open(chart_image_path, 'rb'),
                       f"🚀 Top 5 Chat Champions:\n{result_message_user}")
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
                        if user == username or user == nickname:
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
