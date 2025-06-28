# 🤖 FactDrop — Your Daily Dose of Random

**FactDrop** is a simple Telegram bot that delivers weird, wonderful, and wildly random facts right to your DMs — daily. Built with Python, Supabase, and love for the bizarre.

Whether you’re bored, curious, or just love fun trivia, FactDrop has you covered with one new fact a day at the exact time you subscribed.

---

## 💡 What FactDrop Can Do

- `/start` — Subscribes you to receive a new random fact every day.
- `/random` — Instantly get a random fact on demand.
- `/time` — See what time your daily fact will arrive.
- `/unsubscribe` — Opt out of daily facts (but we’ll miss you 💔).

---

## 🛠 Tech Stack

- Python + [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)
- Supabase (to store subscribers and timestamps)
- APScheduler (to schedule daily messages)
- Deployed on Render

---

## 🚀 Deployment

To deploy on Render or any cloud platform, simply run:

```bash
python factdrop.py
