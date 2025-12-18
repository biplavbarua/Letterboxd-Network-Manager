# Letterboxd Network Manager

A safe, local tool to help you grow your Letterboxd network with active, high-quality connections.

### ✨ Features
*   **Smart Network Analysis**: Scrapes followers from a target user to find high-value accounts.
*   **Activity Detection**: Automatically scans profiles to identify active users (Green) vs. inactive ones (Red).
*   **Safe Following**: Built-in delays and headers to mimic real browser behavior.
*   **Paranoid Mode**:
    *   **Local Database**: Tracks your follow history to prevent re-following.
    *   **Daily Limit**: HARD limit of 50 follows per day to protect your account.
    *   **Cookie Auth**: Securely uses your session cookies without storing login credentials.

### 🛠️ Setup
1.  **Clone the repo**: `git clone https://github.com/biplavbarua/Letterboxd-Network-Manager.git`
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the application**:
    ```bash
    python app.py
    ```
    *Note: The first run initializes the local SQLite database.*
4.  **Open Dashboard**: Go to `http://127.0.0.1:5000`
5.  **Authenticate**: Paste your `letterboxd.com` cookie string to unlock the "Follow" features.

### ⚠️ Disclaimer
This tool is for educational purposes. Use responsively and respect Letterboxd's terms of service. Ideally, use it to find people and follow them manually if you prefer.
