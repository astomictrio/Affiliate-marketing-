from telethon import TelegramClient, events
import requests
from bs4 import BeautifulSoup
import re

# 🛠 Telegram API Credentials (https://my.telegram.org/apps se lein)
api_id = 123456  # Replace with your API ID
api_hash = "your_api_hash"

# 📌 Bot Token (Agar Bot Se Chalana Hai)
bot_token = "7661788811:AAFNLhxjgl5zC6JXMaAWM5ve6AtRspKiIA4"

# 📌 Source & Target Channels
source_channel = "@source_channel"  # Yeh source channel hai jahan se deals aayengi
target_group = "@target_group"  # Yeh target group hai jahan bot deals bhejega

# 🏷 Amazon Affiliate Tag
affiliate_tag = "yourtag-21"  # Replace with your Amazon affiliate tag

client = TelegramClient('bot_session', api_id, api_hash)

def get_amazon_product_image(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        image_tag = soup.find("img", {"id": "landingImage"})
        if image_tag:
            return image_tag["src"]
    return None

def replace_affiliate_link(original_url):
    match = re.search(r'/dp/([A-Z0-9]+)/', original_url)
    if match:
        product_id = match.group(1)
        return f"https://www.amazon.in/dp/{product_id}/?tag={affiliate_tag}"
    return original_url

@client.on(events.NewMessage(chats=source_channel))
async def forward_with_affiliate_link(event):
    text = event.message.text
    amazon_link = None
    
    for word in text.split():
        if "amazon" in word and "dp" in word:
            amazon_link = word  # Extract Amazon Product Link
            break
    
    if amazon_link:
        new_affiliate_link = replace_affiliate_link(amazon_link)
        text = text.replace(amazon_link, new_affiliate_link)  # Replace link

        image_url = get_amazon_product_image(amazon_link)
        if image_url:
            await client.send_file(target_group, image_url, caption=text)
        else:
            await client.send_message(target_group, text)
    else:
        await client.send_message(target_group, text)

print("🤖 Bot is running and replacing Amazon links with your affiliate link...")
client.start()
client.run_until_disconnected()
