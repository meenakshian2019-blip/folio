#Pulse - Upgraded Summary & Alert Bot
#Fetches: Weather (OpenWeatherMap API) & a quote (zenquotes.io)
#Monitors: Temperature > 35°C or Rain alerts via secure email
#Runs: every day at 8 AM IST via GitHub Actions

import os
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import date

# =====================================================================
# CONFIGURATION & ENVIRONMENT VARIABLES
# =====================================================================
CITY = "Thiruvananthapuram"  # Set your desired city
API_KEY = os.environ.get("OPENWEATHER_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")

# ==========================================
# UPGRADED FUNCTION 1: WEATHER & ALERTS
# ==========================================
def get_weather_and_check_alerts():
    """Fetch live data from OpenWeatherMap and determine if thresholds are breached."""
    if not API_KEY:
        return "Weather unavailable (Missing OpenWeatherMap API Key)", False

    # Standard metric (Celsius) API request to OpenWeatherMap
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Parse out raw metrics
        temp = data["main"]["temp"]
        weather_condition = data["weather"][0]["main"].lower()
        description = data["weather"][0]["description"].title()
        
        # Evaluate warning criteria conditions
        is_too_hot = temp > 35
        is_raining = "rain" in weather_condition or "drizzle" in weather_condition
        
        weather_summary = f"{CITY}: {temp}°C | {description}"
        alert_triggered = False
        reasons = []

        if is_too_hot:
            alert_triggered = True
            reasons.append(f"High Temperature Warning ({temp}°C > 35°C)")
        if is_raining:
            alert_triggered = True
            reasons.append(f"Rainfall Detected ({description})")
            
        if alert_triggered:
            weather_summary += f"\n⚠️ ALERTS ACTIVE: {', '.join(reasons)}"
            
        return weather_summary, alert_triggered

    except Exception as e:
        return f"Weather information unavailable ({e})", False

# ==========================================
# NEW FUNCTION: SMTP EMAIL DISPATCH
# ==========================================
def send_email_alert(weather_text):
    """Logs into an encrypted mail server and sends an alert email to yourself."""
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("Skipping Alert Dispatch: Email configuration credentials missing from secrets.")
        return

    msg = MIMEText(f"An automated weather alert rule condition was breached!\n\nCurrent Status:\n{weather_text}")
    msg["Subject"] = f"⚠️ CRITICAL WEATHER ALERT: Action Required in {CITY}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = SENDER_EMAIL  # Send the email to yourself

    try:
        # Connect securely to Gmail's SMTP server over SSL (Port 465)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("Alert notification email delivered successfully.")
    except Exception as e:
        print(f"Failed to transmit email alert via SMTP: {e}")

# ==========================================
# FUNCTION 2: QUOTE (Unchanged from original)
# ==========================================
def get_quote():
    """Fetch a random motivational quote from ZenQuotes."""
    url = "https://zenquotes.io/api/random"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()       
        return f'"{data[0]["q"]}" — {data[0]["a"]}'
    except Exception as e:
        return f"Quote unavailable ({e})"

# ==========================================
# FUNCTION 3: BUILD THE SUMMARY
# ==========================================
def build_summary():
    """Assemble the full daily summary and coordinate automated rules."""
    today = date.today().strftime("%A, %B %d, %Y")
    weather, alert_triggered = get_weather_and_check_alerts()
    quote = get_quote()
    
    summary = f"""------------------------------------
PULSE - Daily Summary (Alert Monitor Active)
{today}
------------------------------------

WEATHER REPORT
{weather}

TODAY'S QUOTE
{quote}
------------------------------------"""
    
    # Task 1 Condition Rule Execution
    if alert_triggered:
        print("Threshold reached! Triggering emergency alert transmission...")
        send_email_alert(weather)
        
    return summary

# ==========================================
# FUNCTION 4: RUN ENTRY GUARD
# ==========================================
def run():
    """Main entry point called by GitHub Actions or local executions."""
    summary = build_summary()
    print(summary)  # Outputs directly to terminal / GitHub Actions Log
    
    # Save text log summary file
    with open("daily_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)
        
    print("Pulse routine completed successfully.")

if __name__ == "__main__":
    run()