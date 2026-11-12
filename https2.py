import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import time
import requests


class WebsiteStatusApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Real Website Status Monitor")
        self.root.geometry("650x520")
        
        self.is_monitoring = False
        self.after_id = None

        # Handle clean exit when closing window
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Input & Control Frame
        input_frame = tk.Frame(root, padx=10, pady=10)
        input_frame.pack(fill=tk.X)

        self.label = tk.Label(
            input_frame, text="Enter Full URL (e.g., https://outlook.live.com):"
        )
        self.label.pack(anchor="w", pady=(0, 5))

        # URL Entry and Status Light Row
        row_frame = tk.Frame(input_frame)
        row_frame.pack(fill=tk.X, pady=5)

        self.entry = tk.Entry(row_frame, width=42, font=("Arial", 10))
        self.entry.pack(side=tk.LEFT, padx=(0, 10))
        self.entry.insert(0, "https://outlook.live.com")
        self.entry.bind("<Return>", lambda event: self.toggle_monitoring())

        # Status Indicator Circle (Canvas)
        self.canvas = tk.Canvas(row_frame, width=30, height=30, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=(5, 10))
        # Draw initial gray circle (Idle)
        self.status_circle = self.canvas.create_oval(5, 5, 25, 25, fill="gray", outline="")

        self.toggle_button = tk.Button(
            row_frame,
            text="Start Monitoring",
            command=self.toggle_monitoring,
            width=15,
            bg="#007ACC",
            fg="white",
            font=("Arial", 9, "bold")
        )
        self.toggle_button.pack(side=tk.LEFT)

        # Interval Options Frame (10-second option removed)
        interval_frame = tk.Frame(input_frame)
        interval_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(interval_frame, text="Check Interval:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.interval_var = tk.StringVar(value="1 Minute")
        self.interval_combo = ttk.Combobox(
            interval_frame, 
            textvariable=self.interval_var,
            values=["30 Seconds", "1 Minute", "2 Minutes", "5 Minutes"],
            state="readonly",
            width=15
        )
        self.interval_combo.pack(side=tk.LEFT)

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

    def toggle_monitoring(self):
        if not self.is_monitoring:
            url = self.entry.get().strip()
            if not url:
                messagebox.showerror("Error", "Please enter a URL.")
                return

            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url

            self.is_monitoring = True
            self.toggle_button.config(text="Stop Monitoring", bg="#D9534F")
            self.entry.config(state="disabled")
            self.interval_combo.config(state="disabled")
            
            self.log_message(f"Starting continuous monitor for: {url}\n")
            self.run_check_cycle(url)
        else:
            self.stop_monitoring()

    def stop_monitoring(self):
        self.is_monitoring = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
            
        self.toggle_button.config(text="Start Monitoring", bg="#007ACC")
        self.entry.config(state="normal")
        self.interval_combo.config(state="readonly")
        self.canvas.itemconfig(self.status_circle, fill="gray")
        self.log_message("Monitoring stopped by user.\n\n")

    def run_check_cycle(self, url):
        if not self.is_monitoring:
            return

        # Trigger background thread for checking
        threading.Thread(
            target=self.check_website, args=(url,), daemon=True
        ).start()

    def check_website(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            elapsed_time = round((time.time() - start_time) * 1000)

            status_code = response.status_code
            
            if 200 <= status_code < 300:
                result_text = f"[{timestamp}] [ONLINE] Status: {status_code} {response.reason} | Response Time: {elapsed_time}ms\n"
                status_color = "green"
            else:
                result_text = f"[{timestamp}] [DEGRADED] Status: {status_code} {response.reason} | Response Time: {elapsed_time}ms\n"
                status_color = "red"
        except requests.exceptions.ConnectTimeout:
            result_text = f"[{timestamp}] [DOWN] Connection Timeout.\n"
            status_color = "red"
        except requests.exceptions.ConnectionError:
            result_text = f"[{timestamp}] [DOWN] Connection Refused / DNS Error.\n"
            status_color = "red"
        except Exception as e:
            result_text = f"[{timestamp}] [ERROR] {e}\n"
            status_color = "red"

        # Safely update GUI on the main thread
        self.root.after(0, self.update_output, result_text, status_color, url)

    def update_output(self, result_text, status_color, url):
        self.log_message(result_text)
        self.canvas.itemconfig(self.status_circle, fill=status_color)

        # If still monitoring, schedule the next check based on user selection
        if self.is_monitoring:
            interval_str = self.interval_var.get()
            delay_ms = 60000  # default 1 min
            
            if "30 Seconds" in interval_str:
                delay_ms = 30000
            elif "1 Minute" in interval_str:
                delay_ms = 60000
            elif "2 Minutes" in interval_str:
                delay_ms = 120000
            elif "5 Minutes" in interval_str:
                delay_ms = 300000

            self.after_id = self.root.after(delay_ms, lambda: self.run_check_cycle(url))

    def log_message(self, message):
        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, message)
        self.text_area.see(tk.END)
        self.text_area.config(state="disabled")

    def on_close(self):
        self.stop_monitoring()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = WebsiteStatusApp(root)
    root.mainloop()