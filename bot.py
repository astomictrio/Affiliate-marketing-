import os
import logging
import requests
import re
from telethon import TelegramClient, events

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Bot Credentials (From Environment Variables)
API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
SOURCE_CHANNEL = os.environ.get("SOURCE_CHANNEL", "")
TARGET_CHANNEL = os.environ.get("TARGET_CHANNEL", "")
AMAZON_TAG = os.environ.get("AMAZON_TAG", "")

# ✅ Check if all credentials are set
if not all([API_ID, API_HASH, BOT_TOKEN, SOURCE_CHANNEL, TARGET_CHANNEL, AMAZON_TAG]):
    raise ValueError("⚠️ Missing environment variables! Check your Render settings.")

# ✅ Connect to Telegram Bot
client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ✅ Function to Fetch Image from Amazon Link
def fetch_amazon_image(product_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(product_url, headers=headers, timeout=10)
        image_url_match = re.search(r'"hiRes":"(https://[^"]+)"', response.text)
        if image_url_match:
            return image_url_match.group(1)
    except Exception as e:
        logger.error(f"❌ Error fetching image: {e}")
    return None

# ✅ Message Forwarding & Image Fetching
@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def forward_and_replace(event):
    text = event.message.text or ""

    # ✅ Amazon Affiliate Link Replacement
    amazon_link_match = re.search(r"(https?://www\.amazon\.in[^\s]+)", text)
    if amazon_link_match:
        original_link = amazon_link_match.group(1)
        affiliate_link = original_link.split("?")[0] + f"?tag={AMAZON_TAG}"
        text = text.replace(original_link, affiliate_link)

        # ✅ Fetch Image from Amazon if no image in message
        if not event.message.photo:
            image_url = fetch_amazon_image(original_link)
            if image_url:
                await client.send_file(TARGET_CHANNEL, image_url, caption=text)
                logger.info("✅ Image fetched & forwarded successfully!")
                return

    # ✅ Forwarding with Image (If Available)
    if event.message.photo:
        await client.send_file(TARGET_CHANNEL, event.message.photo, caption=text)
        logger.info("✅ Image + Text forwarded successfully!")
    else:
        await client.send_message(TARGET_CHANNEL, text)
        logger.info("✅ Text forwarded successfully!")

# ✅ Start Bot
logger.info("🤖 Bot is running...")
client.run_until_disconnected()
