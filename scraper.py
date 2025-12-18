import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import random
import logging

class FollowerScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.base_url = "https://letterboxd.com"
        self.logger = logging.getLogger(__name__)

    def _get_headers(self):
        """Generate random headers to mimic a real browser."""
        return {
            'User-Agent': self.ua.random,
            'Referer': self.base_url,
            'Accept-Language': 'en-US,en;q=0.9',
        }

    def _random_delay(self, min_seconds=2.0, max_seconds=5.0):
        """Sleep for a random amount of time to be polite."""
        delay = random.uniform(min_seconds, max_seconds)
        self.logger.info(f"sleeping for {delay:.2f} seconds...")
        time.sleep(delay)

    def get_followers(self, username, max_pages=3):
        """
        Scrape followers for a given username.
        
        Args:
            username (str): The letterboxd username to scan.
            max_pages (int): Limit scraping to this many pages (25 users per page).
            
        Returns:
            list: A list of dicts containing user info {'username': str, 'avatar_url': str, 'display_name': str}
        """
        followers = []
        url = f"{self.base_url}/{username}/followers/"
        
        page = 1
        while page <= max_pages:
            self.logger.info(f"Scraping {username} followers - Page {page}")
            
            try:
                response = requests.get(f"{url}page/{page}/", headers=self._get_headers())
                
                if response.status_code == 404:
                    self.logger.warning("User or page not found.")
                    break
                elif response.status_code != 200:
                    self.logger.error(f"Failed to fetch page {page}: {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Letterboxd follower table rows (updated selector)
                table_rows = soup.select('table.member-table tbody tr')
                
                if not table_rows:
                    self.logger.info("No more followers found.")
                    # DEBUG: Save HTML to inspect later
                    with open("debug_response.html", "w") as f:
                        f.write(soup.prettify())
                    self.logger.info("Saved debug_response.html for inspection.")
                    break

                for row in table_rows:
                    # 1. Avatar (inside .table-person .person-summary .avatar)
                    avatar_link = row.select_one('.table-person .person-summary a.avatar')
                    avatar_img = avatar_link.find('img') if avatar_link else None
                    avatar_url = avatar_img['src'] if avatar_img else None
                    
                    # 2. Name/Username (inside .table-person .person-summary h3.title-3 a.name)
                    name_link = row.select_one('.table-person .person-summary h3.title-3 a.name')
                    
                    if name_link:
                        u_name = name_link['href'].strip('/') # e.g. /someuser/ -> someuser
                        display_name = name_link.text.strip()
                        
                        followers.append({
                            'username': u_name,
                            'display_name': display_name,
                            'avatar_url': avatar_url,
                            'profile_url': f"{self.base_url}/{u_name}/"
                        })

                # Check for "Next" button to decide if we continue
                next_button = soup.select_one('.paginate-nextprev .next')
                if not next_button:
                    break
                
                page += 1
                self._random_delay()
                
            except Exception as e:
                self.logger.error(f"Error scraping page {page}: {e}")
                break

        self.logger.info(f"Scraped {len(followers)} unique followers for {username}.")
        return followers

    def profile_is_active(self, username, days_threshold=30):
        """
        Check if a user has logged any activity in the last X days.
        Basic check: Look for 'Recent Activity' or 'Diary' dates.
        For MVP: We'll check if the 'Recent Activity' section exists on profile.
        """
        url = f"{self.base_url}/{username}/"
        self._random_delay(1.5, 3.0) # Shorter delay for checks
        
        try:
            response = requests.get(url, headers=self._get_headers())
            if response.status_code != 200:
                return False
                
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for recent diary entries or activity
            # A simple heuristic: check if the 'recent-activity' section is populated
            activity_section = soup.select_one('#recent-activity')
            
            # TODO: Improve date parsing logic for high accuracy. 
            # For now, if they have *any* recent activity visible, we valid them.
            if activity_section:
                return True
                
            return False 
        except Exception as e:
            self.logger.error(f"Error checking activity for {username}: {e}")
            return False

    def follow_user(self, target_username, cookies_str):
        """
        Follow a user using the provided session cookies.
        Returns: (success: bool, message: str)
        """
        # Parse cookie string into dict
        cookies = {}
        try:
            if not cookies_str or not isinstance(cookies_str, str):
                return False, "Empty or invalid cookie string provided."

            for item in cookies_str.split(';'):
                if '=' in item:
                    k, v = item.split('=', 1)
                    cookies[k.strip()] = v.strip()
            
            if not cookies:
                 return False, "No cookies found. Format: 'key=value;'"

        except Exception as e:
            self.logger.error(f"Invalid cookie format: {e}")
            return False, f"Cookie parse error: {e}"

        profile_url = f"{self.base_url}/{target_username}/"
        
        try:
            # Step 1: Get CSRF Token
            self.logger.info(f"Fetching profile for {target_username} to get CSRF...")
            response = requests.get(profile_url, headers=self._get_headers(), cookies=cookies)
            
            if "Sign in" in response.text and "person" not in response.text:
                 self.logger.error("Cookies invalid or expired (Not logged in).")
                 return False, "Session expired/invalid (Not logged in)"

            # Extract CSRF from JS variable
            csrf_token = None
            for line in response.text.split('\n'):
                if "supermodelCSRF" in line:
                    parts = line.split("'")
                    if len(parts) >= 3:
                        csrf_token = parts[1]
                        break
            
            if not csrf_token:
                self.logger.error("Could not find CSRF token.")
                return False, "CSRF token missing (Auth failed?)"
                
            # Step 2: Send Follow Request
            self._random_delay(2.0, 4.0)
            follow_url = f"{self.base_url}/{target_username}/follow/"
            
            # AJAX Headers are CRITICAL for Letterboxd actions
            headers = self._get_headers()
            headers.update({
                'Origin': self.base_url,
                'Referer': profile_url,
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            })

            payload = {
                '__csrf': csrf_token
            }
            
            self.logger.info(f"Sending FOLLOW request to {target_username}...")
            post_response = requests.post(follow_url, headers=headers, cookies=cookies, data=payload)
            
            if post_response.status_code == 200:
                try:
                    result_json = post_response.json()
                except Exception:
                    return False, f"Not JSON (Login redir?): {post_response.text[:100]}"

                if result_json.get('result'):
                    self.logger.info(f"Successfully followed {target_username}!")
                    return True, "Followed"
                else:
                    msgs = result_json.get('messages', [])
                    fail_reasons = ", ".join(msgs) if msgs else "Unknown"
                    return False, f"LB Error: {fail_reasons} | Raw: {str(result_json)[:100]}"
            
            self.logger.error(f"Follow failed: {post_response.status_code}")
            return False, f"Follow failed: {post_response.status_code} Body: {post_response.text[:50]}"

        except Exception as e:
            self.logger.error(f"Exception during follow: {e}")
            return False, f"Error: {str(e)}"

if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    scraper = FollowerScraper()
    
    # Test Scrape
    users = scraper.get_followers("vilibazmio", max_pages=1)
    print(f"Found {len(users)} users.")
    
    # Test Active Check on a known ACTIVE user ('vilibazmio' themselves)
    known_active = "vilibazmio"
    is_active = scraper.profile_is_active(known_active)
    print(f"User {known_active} is active? {is_active}")

