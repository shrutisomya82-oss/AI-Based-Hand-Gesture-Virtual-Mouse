import pyautogui
import os
from datetime import datetime

class GestureController:
    def __init__(self):
        # Disabling fail-safe prevents accidental app crashes when you move 
        # your mouse quickly to the extreme edges of the screen.
        pyautogui.FAILSAFE = False 

    def move_mouse(self, x, y, w, h):
        """
        Maps the camera coordinates to your actual screen resolution.
        """
        screen_w, screen_h = pyautogui.size()
        
        # Scale the coordinates based on your actual monitor size
        mouse_x = int(x * screen_w / w)
        mouse_y = int(y * screen_h / h)
        
        # Move the pointer to mapped desktop coordinates
        pyautogui.moveTo(mouse_x, mouse_y)

    def left_click(self):
        pyautogui.click()

    def right_click(self):
        pyautogui.click(button='right')

    def double_click(self):
        pyautogui.doubleClick()

    def mouse_down(self):
        """
        Holds down the left mouse click (used for Dragging).
        """
        pyautogui.mouseDown()

    def mouse_up(self):
        """
        Releases the left click (used to Drop).
        """
        pyautogui.mouseUp()

    def scroll_up(self):
        # Adjust scroll speed by changing this integer (e.g., 100, 150)
        pyautogui.scroll(120)  

    def scroll_down(self):
        pyautogui.scroll(-120)

    def take_screenshot(self):
        """
        Captures the desktop and saves it cleanly inside a folder.
        """
        # Create a screenshots directory in your project folder if it doesn't exist
        if not os.path.exists("Screenshots"):
            os.makedirs("Screenshots")
            
        # Create a unique filename using a timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filepath = f"Screenshots/screenshot_{timestamp}.png"
        
        # Take and save screenshot
        pyautogui.screenshot(filepath)
        print(f"[SYSTEM] Screenshot saved as {filepath}")