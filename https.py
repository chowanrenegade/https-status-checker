import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
import urllib.parse
import requests  # Make sure to run 'pip install requests' in your terminal


class WebsiteStatusApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Real Website Status Checker")
    self.root.geometry("600x450")

    # Input Frame
    input_frame = tk.Frame(root, padx=10, pady=10)
    input_frame.pack(fill=tk.X)

    self.label = tk.Label(
        input_frame, text="Enter Full URL (e.g., https://outlook.live.com):"
    )
    self.label.pack(anchor="w", pady=(0, 5))

    self.entry = tk.Entry(input_frame, width=50, font=("Arial", 10))
    self.entry.pack(side=tk.LEFT, padx=(0, 10), pady=5)
    self.entry.insert(0, "https://outlook.live.com")
    self.entry.bind("<Return>", lambda event: self.start_check_thread())

    self.check_button = tk.Button(
        input_frame,
        text="Check Status",
        command=self.start_check_thread,
        width=12,
        bg="#007ACC",
        fg="white",
    )
    self.check_button.pack(side=tk.LEFT, pady=5)

    # Output Area
    output_frame = tk.Frame(root, padx=10, pady=5)
    output_frame.pack(fill=tk.BOTH, expand=True)

    self.text_area = scrolledtext.ScrolledText(
        output_frame,
        wrap=tk.WORD,
        state="disabled",
        bg="#1e1e1e",
        fg="#d4d4d4",
        font=("Consolas", 10),
    )
    self.text_area.pack(fill=tk.BOTH, expand=True)

  def start_check_thread(self):
    url = self.entry.get().strip()
    if not url:
      messagebox.showerror("Error", "Please enter a URL.")
      return

    # Ensure URL has a scheme (http/https)
    if not url.startswith("http://") and not url.startswith("https://"):
      url = "https://" + url

    self.check_button.config(state="disabled")
    self.text_area.config(state="normal")
    self.text_area.delete(1.0, tk.END)
    self.text_area.insert(
        tk.END, f"Checking HTTP status for: {url}...\n\nPlease wait...\n\n"
    )
    self.text_area.config(state="disabled")

    threading.Thread(
        target=self.check_website, args=(url,), daemon=True
    ).start()

  def check_website(self, url):
    try:
      # Timeout after 10 seconds so it doesn't freeze on dead servers
      response = requests.get(url, timeout=10, allow_redirects=True)

      status_code = response.status_code
      # 200-299 means success
      if 200 <= status_code < 300:
        result = (
            f"[ONLINE] Success!\n"
            f"Status Code: {status_code} {response.reason}\n"
            f"The website is up and responding normally."
        )
      else:
        result = (
            f"[DEGRADED / ERROR] The server responded, but with an error.\n"
            f"Status Code: {status_code} {response.reason}\n"
            f"The site might be experiencing issues."
        )
    except requests.exceptions.ConnectTimeout:
      result = (
          f"[DOWN] Connection Timeout.\n"
          f"The server took too long to respond. It is likely down."
      )
    except requests.exceptions.ConnectionError:
      result = (
          f"[DOWN] Connection Refused / DNS Error.\n"
          f"Could not connect to the web server. The service is down."
      )
    except Exception as e:
      result = f"[ERROR] An unexpected error occurred: {e}"

    self.root.after(0, self.update_output, result)

  def update_output(self, result):
    self.text_area.config(state="normal")
    self.text_area.insert(tk.END, result)
    self.text_area.config(state="disabled")
    self.check_button.config(state="normal")


if __name__ == "__main__":
  root = tk.Tk()
  app = WebsiteStatusApp(root)
  root.mainloop()