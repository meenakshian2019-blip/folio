#Pulse - Upgraded Summary, News Scraper & Alert Bot
#Fetches: Weather (OpenWeatherMap), Quote (ZenQuotes), Headlines (3 News Sites via RSS)
#Compiles: Formatted HTML Email digest
#Runs: Every day at 7 AM IST via GitHub Actions


import os
import requests
import smtplib
import xml.etree.ElementTree as ET
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# =====================================================================
# CONFIGURATION & ENVIRONMENT VARIABLES
# =====================================================================
CITY = "Thiruvananthapuram"
API_KEY = os.environ.get("OPENWEATHER_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")

# ==========================================
# WEATHER & ALERTS FUNCTION
# ==========================================
def get_weather_and_check_alerts():
    if not API_KEY:
        return "Weather unavailable (Missing API Key)", False, 0, "N/A"
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        temp = data["main"]["temp"]
        weather_condition = data["weather"][0]["main"].lower()
        description = data["weather"][0]["description"].title()
        
        is_too_hot = temp > 35
        is_raining = "rain" in weather_condition or "drizzle" in weather_condition
        
        alert_triggered = is_too_hot or is_raining
        weather_summary = f"{temp}°C, {description}"
        
        if is_too_hot:
            weather_summary += " (⚠️ High Temperature Alert)"
        if is_raining:
            weather_summary += " (⚠️ Rainfall Warning)"
            
        return weather_summary, alert_triggered, temp, description
    except Exception as e:
        return f"Weather unavailable ({e})", False, 0, "N/A"

# ==========================================
# QUOTE FUNCTION
# ==========================================
def get_quote():
    url = "https://zenquotes.io/api/random"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()       
        return f'"{data[0]["q"]}" — {data[0]["a"]}'
    except Exception as e:
        return '"Keep moving forward." — Unknown'

# ==========================================
# TASK 2: NEWS SCRAPER FUNCTION
# ==========================================
def scrape_news_feeds():
    """Scrapes 3 distinct news RSS XML endpoints for top headlines, times, and links."""
    feeds = {
        "BBC World News": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "Times of India": "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
        "CNN Top Stories": "http://rss.cnn.com/rss/edition.rss"
    }
    
    news_data = {}
    
    for source, url in feeds.items():
        news_data[source] = []
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse XML structures natively
            root = ET.fromstring(response.content)
            
            # Scrape up to 3 top articles from each feed source
            articles = root.findall(".//item")[:3]
            
            for item in articles:
                title = item.find("title").text if item.find("title") is not None else "No Title"
                link = item.find("link").text if item.find("link") is not None else "#"
                pub_time = item.find("pubDate").text if item.find("pubDate") is not None else "Unknown Time"
                
                # Clean up timezone strings for human reading comfort
                if " +0000" in pub_time:
                    pub_time = pub_time.replace(" +0000", " GMT")
                elif " GMT" not in pub_time and len(pub_time) > 12:
                    pub_time = pub_time[:22]
                    
                news_data[source].append({
                    "title": title,
                    "link": link,
                    "time": pub_time
                })
        except Exception as e:
            news_data[source].append({
                "title": f"Failed to load headlines for {source} ({e})",
                "link": "#",
                "time": "N/A"
            })
            
    return news_data

# ==========================================
# COMPILE BEAUTIFUL HTML EMAIL TEMPLATE
# ==========================================
def generate_html_body(today_str, weather_text, quote_text, news_digest):
    """Assembles data fragments inside a responsive inline-styled HTML container."""
    
    # Generate HTML block for scraped news
    news_html = ""
    for source, articles in news_digest.items():
        news_html += f'<h3 style="color: #2c3e50; margin-bottom: 5px; border-bottom: 1px solid #ecf0f1; padding-bottom: 5px;">{source}</h3>'
        news_html += '<ul style="padding-left: 20px; margin-top: 5px;">'
        for art in articles:
            news_html += f"""
            <li style="margin-bottom: 10px;">
                <a href="{art['link']}" style="color: #3498db; text-decoration: none; font-weight: bold;">{art['title']}</a><br>
                <small style="color: #7f8c8d; font-size: 11px;">Published: {art['time']}</small>
            </li>
            """
        news_html += '</ul>'

    # Master Email UI Layout Wrapper
    html_wrapper = f"""
    <html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f7; padding: 20px; margin: 0;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden; border: 1px solid #e2e8f0;">
            
            <div style="background: linear-gradient(135deg, #2c3e50, #3498db); color: #ffffff; padding: 25px; text-align: center;">
                <h1 style="margin: 0; font-size: 24px; letter-spacing: 1px;">PULSE DAILY DIGEST</h1>
                <p style="margin: 5px 0 0 0; opacity: 0.8; font-size: 14px;">{today_str}</p>
            </div>
            
            <div style="padding: 25px; color: #333333; line-height: 1.6;">
                
                <div style="background-color: #f8fafc; border-left: 4px solid #3498db; padding: 15px; margin-bottom: 25px; border-radius: 0 4px 4px 0;">
                    <h2 style="margin: 0 0 5px 0; font-size: 16px; color: #2c3e50; text-transform: uppercase; letter-spacing: 0.5px;">Live Weather Condition</h2>
                    <p style="margin: 0; font-size: 15px; font-weight: 500;">{weather_text}</p>
                </div>
                
                <div style="margin-bottom: 25px;">
                    <h2 style="margin: 0 0 15px 0; font-size: 18px; color: #2c3e50; font-weight: bold;">📰 Top World Headlines</h2>
                    {news_html}
                </div>
                
                <div style="background-color: #fffdf5; border: 1px dashed #f1c40f; padding: 15px; text-align: center; font-style: italic; border-radius: 6px; margin-top: 20px;">
                    <p style="margin: 0; color: #7f8c8d; font-size: 14px;">{quote_text}</p>
                </div>
                
            </div>
            
            <div style="background-color: #ecf0f1; text-align: center; padding: 15px; font-size: 12px; color: #95a5a6;">
                <p style="margin: 0;">Automated via GitHub Actions • Built with Python</p>
            </div>
            
        </div>
    </body>
    </html>
    """
    return html_wrapper

# ==========================================
# DISPATCH HTML DIGEST FUNCTION
# ==========================================
def dispatch_html_email(html_payload):
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("Email transmission skipped: Setup credentials missing from vault.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🗞️ Pulse Daily Digest: {date.today().strftime('%b %d, %Y')}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = SENDER_EMAIL

    # Attach HTML component to structural email wrapper
    msg.attach(MIMEText(html_payload, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("HTML Digest successfully dispatched to your email inbox!")
    except Exception as e:
        print(f"SMTP error transmitting HTML digest email: {e}")

# ==========================================
# MASTER RUN ENGINE
# ==========================================
def run():
    print("Initializing Pulse daily processing pipeline...")
    today_str = date.today().strftime("%A, %B %d, %Y")
    
    # Run streams
    weather_text, alert_triggered, temp, desc = get_weather_and_check_alerts()
    quote_text = get_quote()
    news_digest = scrape_news_feeds()
    
    # Compile template code
    html_content = generate_html_body(today_str, weather_text, quote_text, news_digest)
    
    # Task 2 requirement: Send EVERY morning (dispatches HTML daily regardless of thresholds)
    dispatch_html_email(html_content)
    
    # Save a flat file log artifact for archive history tracking
    with open("daily_summary.txt", "w", encoding="utf-8") as f:
        # Simple plain text fallback for terminal logging metrics
        f.write(f"Pulse Digest Run: {today_str}\nWeather: {weather_text}\nQuote: {quote_text}\n")
        
    print("Pulse system operation routine completed.")

if __name__ == "__main__":
    run()