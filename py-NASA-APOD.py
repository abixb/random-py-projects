# This is a simple script withI wrote built with NASA APOD API and the image/video library API
# It displays the astronomy picture of the day from NASA

import requests
# import json -- use this in case the 'requests' library
import webbrowser
import os
from datetime import datetime, timedelta
import random
import time
from PIL import Image
from io import BytesIO

def clear_screen():
    """Clear the terminal screen based on OS"""
    os.system('cls' if os.name == 'nt' else 'clear')

class NASAExplorer:
    def __init__(self):
        # REPLACE WITH YOUR OWN API KEY OBTAINED FROM NASA
        self.api_key = "DEMO"
        self.apod_url = "https://api.nasa.gov/planetary/apod"
        self.image_search_url = "https://images-api.nasa.gov/search"
        
    def get_astronomy_picture_of_the_day(self, date=None):
        """Get NASA's Astronomy Picture of the Day"""
        params = {"api_key": self.api_key}
        if date:
            params["date"] = date
            
        try:
            response = requests.get(self.apod_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching APOD: {e}")
            return None
    
    def get_random_apod(self, count=1):
        """Get random APODs from the past year"""
        today = datetime.now()
        
        # Generate random dates from the past year
        random_dates = []
        for _ in range(count):
            days_back = random.randint(1, 365)
            random_date = today - timedelta(days=days_back)
            random_dates.append(random_date.strftime('%Y-%m-%d'))
        
        results = []
        for date in random_dates:
            result = self.get_astronomy_picture_of_the_day(date)
            if result:
                results.append(result)
            time.sleep(1)  # Respect API rate limits
            
        return results
    
    def search_nasa_images(self, query, page=1):
        """Search NASA's image library"""
        params = {
            "q": query,
            "media_type": "image",
            "page": page
        }
        
        try:
            response = requests.get(self.image_search_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error searching NASA images: {e}")
            return None
            
    def display_image_in_terminal(self, image_url):
        """Attempt to display an image in the terminal (basic ASCII art)"""
        try:
            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content))
            
            # Resize for terminal display
            width, height = 80, 25
            image = image.resize((width, height))
            image = image.convert('L')  # Convert to grayscale
            
            # ASCII characters for different brightness levels
            ascii_chars = '@%#*+=-:. '
            
            print("\nImage Preview (ASCII):")
            for y in range(height):
                line = ""
                for x in range(width):
                    pixel = image.getpixel((x, y))
                    # Map pixel brightness to ASCII character
                    char_idx = min(len(ascii_chars) - 1, pixel * len(ascii_chars) // 256)
                    line += ascii_chars[char_idx]
                print(line)
        except Exception as e:
            print(f"Couldn't display image preview: {e}")
            print("Use option to open in browser instead.")

def main():
    explorer = NASAExplorer()
    
    while True:
        clear_screen()
        print("🚀 NASA Space Explorer 🚀")
        print("=" * 30)
        print("1. Today's Astronomy Picture of the Day")
        print("2. Random Astronomy Pictures")
        print("3. Search NASA Image Library")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == "1":
            clear_screen()
            print("Fetching today's astronomy picture...")
            apod = explorer.get_astronomy_picture_of_the_day()
            
            if apod:
                print("\n" + "=" * 50)
                print(f"Title: {apod['title']}")
                print(f"Date: {apod['date']}")
                print("-" * 50)
                print(f"Explanation: {apod['explanation'][:500]}...")
                print("-" * 50)
                
                if apod.get('media_type') == 'image':
                    print(f"Image URL: {apod['url']}")
                    
                    view_option = input("\nOptions: [1] View in browser [2] ASCII preview [3] Back: ")
                    if view_option == "1":
                        webbrowser.open(apod['url'])
                    elif view_option == "2":
                        explorer.display_image_in_terminal(apod['url'])
                else:
                    print(f"Media Type: {apod.get('media_type', 'Unknown')}")
                    if 'url' in apod:
                        print(f"Media URL: {apod['url']}")
                        view_option = input("\nOptions: [1] View in browser [2] Back: ")
                        if view_option == "1":
                            webbrowser.open(apod['url'])
            
            input("\nPress Enter to continue...")
            
        elif choice == "2":
            clear_screen()
            count = input("How many random pictures do you want (1-5)? ")
            try:
                count = min(5, max(1, int(count)))
                print(f"Fetching {count} random astronomy pictures...")
                random_apods = explorer.get_random_apod(count)
                
                for i, apod in enumerate(random_apods, 1):
                    print("\n" + "=" * 50)
                    print(f"[{i}/{len(random_apods)}] {apod['title']} ({apod['date']})")
                    print("-" * 50)
                    print(f"Explanation: {apod['explanation'][:300]}...")
                    
                    if apod.get('media_type') == 'image' and 'url' in apod:
                        view_option = input("\nOptions: [1] View in browser [2] Next image [3] Back to menu: ")
                        if view_option == "1":
                            webbrowser.open(apod['url'])
                        elif view_option == "3":
                            break
                    else:
                        input("\nPress Enter for next image...")
                        
            except ValueError:
                print("Please enter a valid number.")
            
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            clear_screen()
            query = input("Enter search terms (e.g., 'mars rover', 'nebula'): ")
            if query:
                print(f"Searching NASA image library for '{query}'...")
                results = explorer.search_nasa_images(query)
                
                if results and 'collection' in results and 'items' in results['collection']:
                    items = results['collection']['items']
                    total_hits = results['collection'].get('metadata', {}).get('total_hits', 0)
                    
                    print(f"\nFound {total_hits} results. Showing first {len(items)}:")
                    
                    for i, item in enumerate(items[:10], 1):
                        print("\n" + "-" * 50)
                        data = item.get('data', [{}])[0]
                        print(f"[{i}] {data.get('title', 'No title')}")
                        
                        description = data.get('description', 'No description')
                        if description:
                            # Truncate long descriptions
                            if len(description) > 200:
                                description = description[:200] + "..."
                            print(f"Description: {description}")
                        
                        print(f"Date: {data.get('date_created', 'Unknown')}")
                        
                    print("\n" + "-" * 50)
                    item_choice = input("Enter number to view image (or 'b' for back): ")
                    
                    try:
                        if item_choice.lower() == 'b':
                            continue
                            
                        item_idx = int(item_choice) - 1
                        if 0 <= item_idx < len(items):
                            links = items[item_idx].get('links', [])
                            image_links = [link for link in links if link.get('render') == 'image']
                            
                            if image_links:
                                image_url = image_links[0]['href']
                                print(f"Image URL: {image_url}")
                                
                                view_option = input("\nOptions: [1] View in browser [2] ASCII preview [3] Back: ")
                                if view_option == "1":
                                    webbrowser.open(image_url)
                                elif view_option == "2":
                                    explorer.display_image_in_terminal(image_url)
                            else:
                                print("No image available for this item.")
                        else:
                            print("Invalid selection.")
                    except ValueError:
                        print("Please enter a valid number.")
                else:
                    print("No results found or error in search.")
            
            input("\nPress Enter to continue...")
            
        elif choice == "4":
            print("\nThank you for exploring space with NASA! Goodbye! 🌠")
            break
            
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)

if __name__ == "__main__":
    main()