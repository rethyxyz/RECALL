import time
import mss
import mss.tools
from PIL import Image, ImageDraw
import os
from datetime import datetime
import threading
import pystray
from pystray import MenuItem as item
from plyer import notification
import lzma
import io

# Variables to control the recall process
recall_active = False
interval = 2
output_dir = 'screenshots'
JPEG_QUALITY = 30  # Lower quality for higher compression
ICON_PATH = "icon.ico"  # Update this path to your icon file

# Function to take a combined screenshot of all monitors
def take_combined_screenshot():
    global recall_active
    with mss.mss() as sct:
        while recall_active:
            # Get dimensions of all monitors
            monitor_dimensions = [(monitor["left"], monitor["top"], monitor["width"], monitor["height"]) for monitor in sct.monitors[1:]]
            total_width = sum(width for _, _, width, _ in monitor_dimensions)
            max_height = max(height for _, _, _, height in monitor_dimensions)

            # Create a blank image with total width and max height
            combined_img = Image.new('RGB', (total_width, max_height))

            current_x = 0
            for monitor in sct.monitors[1:]:
                screenshot = sct.grab(monitor)
                img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
                
                # Paste the current monitor screenshot into the combined image
                combined_img.paste(img, (current_x, 0))
                current_x += screenshot.width

            # Get current time for filename
            now = datetime.now()
            timestamp = now.strftime("%d-%m-%Y_%H-%M-%S")
            filename = f'{output_dir}/{timestamp} RECALL.jpg'

            # Save the combined image with JPEG compression to a buffer
            buffer = io.BytesIO()
            combined_img.save(buffer, 'JPEG', quality=JPEG_QUALITY, optimize=True)
            jpeg_data = buffer.getvalue()

            # Compress the JPEG data using lzma
            compressed_data = lzma.compress(jpeg_data)

            # Save the compressed data to a file
            with open(filename + ".lzma", 'wb') as f:
                f.write(compressed_data)

            print(f'Compressed screenshot saved to {filename}.lzma')
            
            time.sleep(interval)

# Function to start the recall process
def start_recall():
    global recall_active
    if not recall_active:
        recall_active = True
        threading.Thread(target=take_combined_screenshot, daemon=True).start()
        notification.notify(
            title='RECALL',
            message='RECALL process started',
            app_name='RECALL',
            app_icon=ICON_PATH
        )
        print("RECALL started")

# Function to stop the recall process
def stop_recall():
    global recall_active
    if recall_active:
        recall_active = False
        notification.notify(
            title='RECALL',
            message='RECALL process stopped',
            app_name='RECALL',
            app_icon=ICON_PATH
        )
        print("RECALL stopped")

# Function to exit the application
def exit_app(icon, item):
    stop_recall()
    icon.stop()
    print("Exiting application")

# Function to setup the tray icon and menu
def setup_tray():
    icon = pystray.Icon("recall_icon")
    
    # Load the custom icon image
    icon_path = ICON_PATH  # Ensure this file exists in the same directory
    icon_image = Image.open(icon_path)
    
    menu = pystray.Menu(
        item('Start', lambda: start_recall()),
        item('Stop', lambda: stop_recall()),
        item('Exit', lambda: exit_app(icon, None))
    )
    
    icon.menu = menu
    icon.icon = icon_image
    icon.title = "RECALL"
    icon.run()

# Main function to start the application
def main():
    # Create the output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Notify that RECALL has been added to the system tray
    notification.notify(
        title='RECALL',
        message='RECALL added to the system tray',
        app_name='RECALL',
        app_icon=ICON_PATH
    )

    # Start the tray icon
    setup_tray()

# Entry point of the script
if __name__ == "__main__":
    main()