import os
import time

def take_screenshot(driver, name):
    os.makedirs("screenshots", exist_ok=True)

    timestamp = int(time.time() * 1000)
    file_path = f"screenshots/{name}_{timestamp}.png"

    driver.save_screenshot(file_path)
    return file_path