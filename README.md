 # Telegram Data Analysis Bot

A Telegram bot for analyzing your Telegram data and providing insights into your messaging habits.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Usage](#usage)
- [Analysis Options](#analysis-options)
- [Dependencies](#dependencies)

## Introduction

Welcome to the Telegram Data Analysis Bot! This bot is designed to help you analyze your Telegram data and extract valuable insights from your messaging history.

## Features

- Total message count analysis
- Sent vs. received messages analysis with a pie chart
- Word frequency analysis with a word cloud
- Most used emoji analysis with a bar chart
- Chat champions analysis to identify the most active users
- Peak hours analysis for message distribution throughout the day
- Forwarded from analysis to find the top users from whom messages are forwarded

## Getting Started

### Installation

To use the Telegram Data Analysis Bot, follow these steps:

1. Clone the repository: `git clone https://github.com/your-username/telegram-data-analysis-bot.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up a Telegram bot on [BotFather](https://t.me/botfather) and obtain the token.
4. Replace the placeholder token in the code with your actual bot token.

### Usage

1. Start the bot by running the script: `python telegram_data_analysis_bot.py`
2. Send your Telegram data file in JSON format to the bot (Please note that if your file is more than 20mb consider sending your file in ZIP format).
3. Choose from various analysis options using the provided inline buttons.

## Analysis Options

- **Total Messages:** Analyze and display the total number of messages.
- **Sent vs. Received:** Compare the number of sent and received messages with a pie chart.
- **Word Frequency:** Find the top 10 most frequently used words and display them with a pie chart.
- **Most Used Emoji:** Identify the top 10 most frequently used emojis and visualize them with a bar chart.
- **Chat Champions:** Discover the top 5 most active users and view their message counts with a bar chart.
- **Peak Hours:** Analyze the distribution of messages throughout the day and identify the top 5 most active daytimes.
- **Forwarded From:** Explore the top 5 users from whom messages are most frequently forwarded.

## Dependencies

Before running the Telegram Data Analysis Bot, ensure that you have the necessary Python packages installed. You can install them using the following steps:

### [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)

This is the official library for interacting with the Telegram Bot API. It provides the tools required to create a Telegram bot, handle messages, and more.

### [matplotlib](https://matplotlib.org/)

Matplotlib is a popular plotting library in Python. In this project, it is used for creating various charts, such as pie charts and bar charts, to visualize the analysis results.

```bash
pip install pyTelegramBotAPI
pip install matplotlib
