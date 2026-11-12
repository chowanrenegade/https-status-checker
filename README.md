# Real Website Status Checker 🌐

A lightweight, cross-platform Python application built with **Tkinter** and the **`requests`** library. 

Unlike traditional terminal `ping` commands (which only check if a server responds to basic network packets), this tool performs a **real HTTP/HTTPS request** to verify whether a web service is actually up, responding, and returning proper status codes (like `200 OK`).

---

## Why Use This Instead of `ping`?
Traditional `ping` uses ICMP packets. A server can respond perfectly to a ping while its actual web application, login portals, or database are completely crashing (a classic issue during major cloud outages like Microsoft 365 or Outlook going down). This app acts like a browser—asking the server for the actual page and reporting the real-world status.

---

## ✨ Features

* **Real HTTP Status Checking:** Reports exact HTTP status codes (`200 Success`, `503 Service Unavailable`, etc.) and detects connection timeouts or DNS errors.
* **Non-Blocking UI:** Runs network checks in a background thread so the Tkinter graphical window never freezes or grays out.
* **Smart URL Handling:** Automatically ensures proper formatting (`https://`) so you can paste raw web addresses easily.
* **Clean Dark Theme Output:** Features a modern, readable code-style output window.

---

## 🚀 Getting Started

### Prerequisites
Make sure you have Python installed on your system. You will also need the `requests` library.

Open your terminal or command prompt and install `requests`:
```bash
pip install requests
