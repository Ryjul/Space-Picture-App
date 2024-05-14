import tkinter as tk
from tkinter import messagebox, Toplevel
import requests
from PIL import Image, ImageTk
import json
import webbrowser
import datetime
import random
from io import BytesIO

class NASAImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NASA Photo of the Day")
        self.root.attributes('-fullscreen', True)
        self.root.geometry("800x480")
        self.root.configure(bg='white')  # Set background color of root window

        self.title_label = tk.Label(self.root, font=("Calibri", 20, "bold"), bg='white')
        self.title_label.pack(side=tk.TOP, pady=20)

        self.image_label = tk.Label(self.root)
        self.image_label.pack(expand=True, fill=tk.BOTH)

        self.current_date = None
        self.update_paused = False

        self.info_button = tk.Button(self.root, text="Info", command=self.show_info)
        self.info_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.next_button = tk.Button(self.root, text="Next", command=self.load_image_and_info)
        self.next_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.load_image_and_info()

        # Schedule the function to load a new image and info every 5 minutes
        self.root.after(300000, self.refresh_image_and_info)

    def random_date(self):
        current_date = datetime.datetime.now()
        end_date = datetime.datetime(1995, 6, 16)
        
        # Get a random number of seconds between current date and June 16, 1995
        random_seconds = random.randint(0, int((current_date - end_date).total_seconds()))
        
        # Generate a random date within the specified range
        random_datetime = end_date + datetime.timedelta(seconds=random_seconds)
        
        # Format the date as 'yyyy-mm-dd'
        formatted_date = random_datetime.strftime("%Y-%m-%d")
        
        return formatted_date

    def load_image_and_info(self):
        if not self.update_paused:
            date = self.random_date()
            api_key = "your_key_here"  # NASA API key
            url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}&date={date}"
            try:
                response = requests.get(url)
                data = json.loads(response.text)

                if response.status_code == 200:
                    self.title_label.config(text=f"Learn about: {data['title']}")
                    if data["media_type"] == "image":
                        image_url = data["url"]
                        image_response = requests.get(image_url)
                        if image_response.status_code == 200:
                            image_data = Image.open(BytesIO(image_response.content))
                            image_resized = self.resize_image(image_data, 800, 350)  # Resize the image
                            self.image = ImageTk.PhotoImage(image_resized)
                            self.image_label.configure(image=self.image)
                            self.current_date = date  # Set current date only if image is loaded
                        else:
                            self.load_image_and_info()  # Load a new image if error occurs
                    else:
                        self.load_image_and_info()  # Load a new image if no image available
                else:
                    self.load_image_and_info()  # Load a new image if error occurs
            except Exception as e:
                print(f"Error: {e}")
                self.load_image_and_info()  # Load a new image if an exception occurs

    def resize_image(self, image, width, height):
        aspect_ratio = image.width / image.height
        new_width = width
        new_height = int(width / aspect_ratio)

        # Resize the image
        resized_image = image.resize((new_width, new_height), Image.BILINEAR)

        # Check if the resized image height exceeds the specified height
        if new_height > height:
            resized_image = resized_image.resize((int(height * aspect_ratio), height), Image.BILINEAR)

        return resized_image

    def show_info(self):
        if self.current_date is not None:
            self.pause_updates()
            self.info_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)

            info_window = Toplevel(self.root)
            info_window.title("Information")
            info_window.geometry("600x400")
            info_window.configure(bg='white')  # Set background color of info window
            info_window.attributes("-toolwindow", True)

            api_key = "your_key_here"  # NASA API key
            url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}&date={self.current_date}"
            try:
                response = requests.get(url)
                data = json.loads(response.text)

                if response.status_code == 200:
                    info_text = tk.Text(info_window, wrap=tk.WORD, font=("Calibri", 12), bg='white')
                    info_text.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
                    info_text.insert(tk.END, f"Title: {data['title']}\n\n")
                    info_text.insert(tk.END, data["explanation"])
                    info_text.config(state=tk.DISABLED)  # Disable text modification
                else:
                    messagebox.showerror("Error", "Failed to fetch information")
            except Exception as e:
                print(f"Error: {e}")
                messagebox.showerror("Error", "Failed to fetch information")

            # Bind the resume_updates method to the closing event of the info window
            info_window.protocol("WM_DELETE_WINDOW", lambda: self.on_info_window_close(info_window))

            # Wait for the info window to be closed
            info_window.wait_window()
        else:
            messagebox.showerror("Error", "No image loaded yet")

    def on_info_window_close(self, info_window):
        info_window.destroy()  # Destroy the info window
        self.resume_updates()  # Resume image updates
        self.info_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.NORMAL)

        # Schedule the next image refresh after 5 minutes
        self.root.after(300000, self.refresh_image_and_info)

    def refresh_image_and_info(self):
        # Load new image and info
        self.load_image_and_info()

        # Schedule the next image refresh after 5 minutes
        self.root.after(300000, self.refresh_image_and_info)

    def pause_updates(self):
        self.update_paused = True

    def resume_updates(self):
        self.update_paused = False

    def open_browser(self, event):
        webbrowser.open_new(event.widget.cget("text"))


if __name__ == "__main__":
    root = tk.Tk()
    app = NASAImageApp(root)
    root.mainloop()

