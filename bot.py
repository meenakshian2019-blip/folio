"""
Pulse - Ultimate Summary, Scraper & Portfolio Sync Bot
Fetches: Weather (OpenWeatherMap), Quote (ZenQuotes), Headlines (3 News Feeds), GitHub Repos (GitHub API)
Compiles: Formatted HTML Email digest & structured 'projects.json'
Runs: Automated daily routines + updates portfolio code dynamically on repository changes
"""

import os
import requests
import json
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

# TASK 3 ENVIRONMENT VARIABLES
GITHUB_USER = "meenakshian2019-blip"  
GH_TOKEN = os.environ.get("PORTFOLIO_SYNC_TOKEN")

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
            weather_summary += " (⚠️ High Temp Alert)"
        if is_raining:
            weather_summary += " (⚠️ Rain Warning)"
            
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
# NEWS SCRAPER FUNCTION
# ==========================================
def scrape_news_feeds():
    feeds = {
        "BBC World News": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "Times of India": "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
        "NPR International": "https://feeds.npr.org/1004/rss.xml"
    }
    
    news_data = {}
    for source, url in feeds.items():
        news_data[source] = []
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            articles = root.findall(".//item")[:3]
            
            for item in articles:
                title = item.find("title").text if item.find("title") is not None else "No Title"
                link = item.find("link").text if item.find("link") is not None else "#"
                pub_time = item.find("pubDate").text if item.find("pubDate") is not None else "Unknown Time"
                
                if " +0000" in pub_time:
                    pub_time = pub_time.replace(" +0000", " GMT")
                elif len(pub_time) > 22:
                    pub_time = pub_time[:22]
                    
                news_data[source].append({"title": title, "link": link, "time": pub_time})
        except Exception as e:
            news_data[source].append({"title": f"Feed unavailable ({e})", "link": "#", "time": "N/A"})
    return news_data

# ==========================================
# COMPILE BEAUTIFUL HTML EMAIL TEMPLATE
# ==========================================
def generate_html_body(today_str, weather_text, quote_text, news_digest):
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

    html_wrapper = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f6f7; padding: 20px; margin: 0;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <div style="background: linear-gradient(135deg, #2c3e50, #3498db); color: #ffffff; padding: 25px; text-align: center;">
                <h1 style="margin: 0; font-size: 24px;">PULSE AUTOMATION DIGEST</h1>
                <p style="margin: 5px 0 0 0; opacity: 0.8; font-size: 14px;">{today_str}</p>
            </div>
            <div style="padding: 25px; line-height: 1.6; color: #333333;">
                <div style="background-color: #f8fafc; border-left: 4px solid #3498db; padding: 15px; margin-bottom: 25px;">
                    <h2 style="margin: 0 0 5px 0; font-size: 14px; color: #7f8c8d; text-transform: uppercase;">Live Weather</h2>
                    <p style="margin: 0; font-size: 16px; font-weight: bold;">{weather_text}</p>
                </div>
                <div style="margin-bottom: 25px;">
                    <h2 style="margin: 0 0 15px 0; font-size: 18px; color: #2c3e50;">📰 Top World Headlines</h2>
                    {news_html}
                </div>
                <div style="background-color: #fffdf5; border: 1px dashed #f1c40f; padding: 15px; text-align: center; font-style: italic; border-radius: 6px;">
                    <p style="margin: 0; color: #7f8c8d;">{quote_text}</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html_wrapper

def dispatch_html_email(html_payload):
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("Email skipped: Credentials missing.")
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🗞️ Pulse Daily Digest: {date.today().strftime('%b %d, %Y')}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = SENDER_EMAIL
    msg.attach(MIMEText(html_payload, "html"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("HTML Digest successfully dispatched to inbox!")
    except Exception as e:
        print(f"SMTP Error: {e}")

# ==========================================
# TASK 3: GITHUB REPO HARVESTER ENGINE
# ==========================================
def sync_github_repositories():
    """Queries the GitHub REST API, extracts project items, and builds an updated clean JSON."""
    if not GITHUB_USER or GITHUB_USER == "your-github-username":
        print("Portfolio Sync Skipped: Please configure your explicit GITHUB_USER string.")
        return False

    print(f"Connecting to GitHub REST API for profile data harvest: @{GITHUB_USER}...")
    url = f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100&sort=updated"
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GH_TOKEN:
        headers["Authorization"] = f"token {GH_TOKEN}"
        
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        repos_raw = response.json()
        
        projects_list = []
        
        for repo in repos_raw:
            # Skip fork repos so the payload only displays your genuine work projects
            if repo.get("fork"):
                continue
                
            project_item = {
                "name": repo.get("name", "Unnamed Project").replace("-", " ").replace("_", " ").title(),
                "description": repo.get("description") or "An automated project artifact created inside my developer workflow environment.",
                "html_url": repo.get("html_url", "#"),
                "language": repo.get("language") or "Python",
                "stars": repo.get("stargazers_count", 0),
                "updated_at": repo.get("updated_at", "")[:10]  # Extracts YYYY-MM-DD cleanly
            }
            projects_list.append(project_item)
            
        # Compile structured data directly into the standard deployment asset file
        with open("projects.json", "w", encoding="utf-8") as f:
            json.dump(projects_list, f, indent=4, ensure_ascii=False)
            
        print(f"Successfully serialized {len(projects_list)} repository nodes into projects.json!")
        return True
    except Exception as e:
        print(f"Critical error mapping repository nodes from GitHub API: {e}")
        return False

# ==========================================
# MASTER RUN ENGINE
# ==========================================
def run():
    print("Initializing Pulse master automation hub pipeline...")
    today_str = date.today().strftime("%A, %B %d, %Y")
    
    # Run Task 1 & 2 Streams
    weather_text, alert_triggered, temp, desc = get_weather_and_check_alerts()
    quote_text = get_quote()
    news_digest = scrape_news_feeds()
    
    html_content = generate_html_body(today_str, weather_text, quote_text, news_digest)
    dispatch_html_email(html_content)
    
    # Run Task 3 Stream
    sync_github_repositories()
    
    print("Pulse system operational loop complete.")

if __name__ == "__main__":
    run()