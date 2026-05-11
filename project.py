"""
=============================================================================
  COMPLETE PYTHON ASSIGNMENT
  ─────────────────────────────────────────────────────────────────────────
  SECTION A  — Client-Side Scripting with urllib
    Part 1 : HTTP GET  Request  (JSONPlaceholder API)
    Part 2 : HTTP POST Request  (httpbin.org echo server)
    Part 3 : Parameter Passing + Client-Side Validation

  SECTION B  — Server-Side Scripting with CGI
    Part 1 : CGI script + HTML form (saved as cgi-bin/form.cgi)
    Part 2 : Built-in HTTP server launcher with CGI enabled
    Part 3 : Server-side validation (name / email)

  SECTION C  — Tkinter Student Management System  (previous assignment)
    Part 1 : GUI  — Top-level window, menus, listbox, scrollbar, dialogs
    Part 2 : SQLite CRUD  — Insert / Read / Update / Delete + transactions
    Bonus  : Dining Philosophers process-synchronisation demo
=============================================================================
  HOW TO RUN
  ─────────────────────────────────────────────────────────────────────────
  python complete_assignment.py
  ↳ Opens the main launcher window with three tabs:
      [urllib Demo]  [CGI Server]  [Student Management]
=============================================================================
"""

# ── Standard-library imports only — no pip install needed ─────────────────
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, filedialog, scrolledtext
import sqlite3
import threading
import time
import random
import re
import os
import sys
import json
import http.server
import io

# urllib family
import urllib.request
import urllib.parse
import urllib.error


# =============================================================================
#  ███████╗███████╗ ██████╗████████╗██╗ ██████╗ ███╗   ██╗     █████╗
#  ██╔════╝██╔════╝██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║    ██╔══██╗
#  ███████╗█████╗  ██║        ██║   ██║██║   ██║██╔██╗ ██║    ███████║
#  ╚════██║██╔══╝  ██║        ██║   ██║██║   ██║██║╚██╗██║    ██╔══██║
#  ███████║███████╗╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║    ██║  ██║
#  ╚══════╝╚══════╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝    ╚═╝  ╚═╝
#  Client-Side urllib  (Part 1, 2, 3)
# =============================================================================

# ── Validation helpers (used by both client AND server sides) ─────────────

def validate_name(name: str):
    """Return (True, '') or (False, error_message)."""
    if not name.strip():
        return False, "Name is required."
    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters."
    return True, ""

def validate_email(email: str):
    """Return (True, '') or (False, error_message)."""
    if not email.strip():
        return False, "Email address is required."
    pattern = r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email.strip()):
        return False, "Invalid email format (e.g. user@example.com)."
    return True, ""


# ── Part 1 : HTTP GET ─────────────────────────────────────────────────────

def urllib_get_request(log):
    """
    Send a GET request to JSONPlaceholder and parse the JSON response.
    Extracts and displays the title + body of the first post.
    """
    url = "https://jsonplaceholder.typicode.com/posts" #fake data
    log("=" * 60)
    log("PART 1 — HTTP GET REQUEST")
    log(f"URL : {url}")
    log("-" * 60)

    try:
        # Build and send the request
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "PythonAssignment/1.0")

        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            log(f"HTTP Status : {status}")

            raw = response.read()                    # bytes
            data = json.loads(raw.decode("utf-8"))   # list of dicts

        # ── Parse JSON response ────────────────────────────────────────────
        first = data[0]
        log("\n── First Post ──────────────────────────────")
        log(f"  ID    : {first['id']}")
        log(f"  Title : {first['title']}")
        log(f"  Body  :\n    {first['body']}")
        log(f"\nTotal posts returned : {len(data)}")
        log("GET request completed successfully.\n")

    except urllib.error.HTTPError as e:
        log(f"HTTP Error {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        log(f"URL Error: {e.reason}")
    except Exception as e:
        log(f"Error: {e}")


# ── Part 2 : HTTP POST ────────────────────────────────────────────────────

def urllib_post_request(name: str, email: str, log):
    """
    Send a POST request carrying name + email to httpbin.org/post.
    httpbin echoes back exactly what we sent — perfect for testing.
    Uses urllib.parse.urlencode() and urllib.request.Request().
    """
    log("=" * 60)
    log("PART 2 — HTTP POST REQUEST")
    log("-" * 60)

    # ── Client-side validation BEFORE sending ─────────────────────────────
    ok_n, err_n = validate_name(name)
    ok_e, err_e = validate_email(email)

    if not ok_n:
        log(f"[CLIENT VALIDATION FAILED] {err_n}")
        return
    if not ok_e:
        log(f"[CLIENT VALIDATION FAILED] {err_e}")
        return

    log("[CLIENT VALIDATION] Name and email are valid. Sending...")

    # ── Encode parameters with urlencode() ────────────────────────────────
    params = {"name": name.strip(), "email": email.strip()}
    encoded_data = urllib.parse.urlencode(params)          # "name=...&email=..."
    data_bytes   = encoded_data.encode("utf-8")            # bytes required by urlopen

    log(f"Encoded data : {encoded_data}")

    url = "https://httpbin.org/post"
    log(f"POST to      : {url}")

    try:
        # urllib.request.Request() with data= makes it a POST automatically
        req = urllib.request.Request(url, data=data_bytes)
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        req.add_header("User-Agent", "PythonAssignment/1.0")

        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            log(f"HTTP Status  : {status}")

            raw  = response.read()
            resp = json.loads(raw.decode("utf-8"))

        # ── Display server's response ──────────────────────────────────────
        log("\n── Server Response (echo) ──────────────────")
        log(f"  form.name  : {resp['form'].get('name', 'N/A')}")
        log(f"  form.email : {resp['form'].get('email', 'N/A')}")
        log(f"  origin IP  : {resp.get('origin', 'N/A')}")
        log("POST request completed successfully.\n")

    except urllib.error.HTTPError as e:
        log(f"HTTP Error {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        log(f"URL Error: {e.reason}")
    except Exception as e:
        log(f"Error: {e}")


# ── Part 3 : GET with Parameters ─────────────────────────────────────────

def urllib_get_with_params(name: str, email: str, log):
    """
    Encode user input as query-string parameters and send as a GET request.
    Uses urllib.parse.urlencode() to build the query string.
    httpbin.org/get echoes the args back so we can verify them.
    """
    log("=" * 60)
    log("PART 3 — GET WITH URL PARAMETERS")
    log("-" * 60)

    # ── Client-side validation ─────────────────────────────────────────────
    ok_n, err_n = validate_name(name)
    ok_e, err_e = validate_email(email)

    if not ok_n:
        log(f"[CLIENT VALIDATION FAILED] {err_n}")
        return
    if not ok_e:
        log(f"[CLIENT VALIDATION FAILED] {err_e}")
        return

    log("[CLIENT VALIDATION] Passed. Building GET request...")

    # ── Build URL with encoded query string ────────────────────────────────
    base_url = "https://httpbin.org/get"
    params   = {"name": name.strip(), "email": email.strip()}
    query    = urllib.parse.urlencode(params)
    full_url = f"{base_url}?{query}"

    log(f"Full URL : {full_url}")

    try:
        req = urllib.request.Request(full_url)
        req.add_header("User-Agent", "PythonAssignment/1.0")

        with urllib.request.urlopen(req, timeout=10) as response:
            raw  = response.read()
            resp = json.loads(raw.decode("utf-8"))

        log("\n── Server Received Parameters ──────────────")
        log(f"  name  : {resp['args'].get('name', 'N/A')}")
        log(f"  email : {resp['args'].get('email', 'N/A')}")
        log("GET-with-params completed successfully.\n")

    except urllib.error.HTTPError as e:
        log(f"HTTP Error {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        log(f"URL Error: {e.reason}")
    except Exception as e:
        log(f"Error: {e}")


# =============================================================================
#  ███████╗███████╗ ██████╗████████╗██╗ ██████╗ ███╗   ██╗    ██████╗
#  ██╔════╝██╔════╝██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║    ██╔══██╗
#  ███████╗█████╗  ██║        ██║   ██║██║   ██║██╔██╗ ██║    ██████╔╝
#  ╚════██║██╔══╝  ██║        ██║   ██║██║   ██║██║╚██╗██║    ██╔══██╗
#  ███████║███████╗╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║    ██████╔╝
#  ╚══════╝╚══════╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝    ╚═════╝
#  CGI-Style Server  (Part 1, 2, 3)
#  NOTE: Python 3.13 removed the 'cgi' module.
#  We implement identical CGI behaviour manually using http.server +
#  urllib.parse.parse_qs() to read POST bodies — zero extra imports.
# =============================================================================

CGI_PORT = 8765

# ── HTML form served at http://localhost:8765/ ────────────────────────────
HTML_FORM = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>CGI-Style Form Demo</title>
<style>
  body  { font-family:Consolas,monospace; background:#1e1e2e;
          color:#e2e8f0; display:flex; justify-content:center; padding:40px; }
  .card { background:#2a2a3e; border-radius:12px; padding:32px; width:420px; }
  h2    { color:#a78bfa; margin-top:0; }
  label { display:block; margin-top:14px; font-size:13px; color:#94a3b8; }
  input { width:100%; padding:8px 10px; margin-top:4px; border-radius:6px;
          border:1px solid #334155; background:#13131f; color:#e2e8f0;
          font-family:Consolas,monospace; font-size:14px; box-sizing:border-box; }
  input:focus { outline:none; border-color:#7c3aed; }
  button { margin-top:20px; width:100%; padding:10px; background:#7c3aed;
           color:#fff; border:none; border-radius:6px; font-size:14px;
           font-weight:bold; cursor:pointer; }
  button:hover { background:#6d28d9; }
  .info { font-size:12px; color:#64748b; margin-top:16px; }
</style>
</head>
<body>
<div class="card">
  <h2>CGI Form — Server-Side Demo</h2>
  <form method="POST" action="/submit">
    <label>Full Name</label>
    <input type="text" name="name" placeholder="e.g. Alice Smith" required>
    <label>Email Address</label>
    <input type="email" name="email" placeholder="e.g. alice@example.com" required>
    <button type="submit">Submit to Server Script</button>
  </form>
  <p class="info">
    Data is sent via HTTP POST.<br>
    The Python server reads the POST body using<br>
    <b>urllib.parse.parse_qs()</b> — same concept as
    <b>cgi.FieldStorage()</b> (which was removed in Python 3.13).
  </p>
</div>
</body>
</html>
"""

def _cgi_field_storage(body_bytes):
    """
    Replicate cgi.FieldStorage() behaviour without the cgi module.
    Parses application/x-www-form-urlencoded POST body.
    Returns a plain dict  { field_name: value_string }
    This is the direct equivalent of:
        form = cgi.FieldStorage()
        name  = form.getvalue("name", "")
        email = form.getvalue("email", "")
    """
    body_str = body_bytes.decode("utf-8", errors="replace")#raw bytes to string
    # urllib.parse.parse_qs returns { key: [list_of_values] }
    parsed = urllib.parse.parse_qs(body_str, keep_blank_values=True)#parses query string
    # flatten to single values, same as FieldStorage.getvalue()
    return {k: v[0] if v else "" for k, v in parsed.items()}#list to single value


def _build_response_html(name, email):
    """
    Server-side processing — validate then build HTML response.
    Mirrors what the CGI script would do after cgi.FieldStorage().
    """
    # ── Server-side validation ─────────────────────────────────────────────
    errors = []
    ok_n, err_n = validate_name(name)
    ok_e, err_e = validate_email(email)
    if not ok_n: errors.append(err_n)
    if not ok_e: errors.append(err_e)

    CSS = ("body{font-family:Consolas,monospace;background:#1e1e2e;"
           "color:#e2e8f0;padding:40px}"
           ".card{background:#2a2a3e;border-radius:12px;padding:32px;"
           "max-width:500px;margin:auto}"
           "a{color:#a78bfa}")

    if errors:
        li = "".join(f"<li>{e}</li>" for e in errors)
        return (
            f"<!DOCTYPE html><html><head><meta charset='UTF-8'>"
            f"<title>Validation Error</title>"
            f"<style>{CSS} h2{{color:#f87171}} ul{{color:#fca5a5}}</style>"
            f"</head><body><div class='card'>"
            f"<h2>Validation Errors</h2><ul>{li}</ul>"
            f"<a href='/'>Go Back</a></div></body></html>"
        )
    else:
        return (
            f"<!DOCTYPE html><html><head><meta charset='UTF-8'>"
            f"<title>Success</title>"
            f"<style>{CSS} h2{{color:#86efac}}"
            f".tag{{background:#7c3aed;padding:2px 10px;border-radius:4px}}"
            f"</style></head><body><div class='card'>"
            f"<h2>Form Processed Successfully!</h2>"
            f"<p>Hello <span class='tag'>{name}</span>,<br><br>"
            f"We have received your email: "
            f"<span class='tag'>{email}</span></p>"
            f"<hr style='border-color:#334155;margin:20px 0'>"
            f"<p style='font-size:12px;color:#64748b'>"
            f"Method : POST<br>"
            f"Fields parsed via urllib.parse.parse_qs()<br>"
            f"(CGI-equivalent — works on Python 3.13+)</p>"
            f"<a href='/'>Submit another</a>"
            f"</div></body></html>"
        )


class CGIStyleHandler(http.server.BaseHTTPRequestHandler):
    """
    Pure http.server handler — no cgi module required.
    GET  /        → serve HTML form
    POST /submit  → parse body with urllib.parse.parse_qs()
                    validate server-side, return response
    This replicates exactly what a CGI script does.
    """

    def log_message(self, fmt, *args):
        pass   # suppress console noise; we log via GUI

    # ── GET ───────────────────────────────────────────────────────────────
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = HTML_FORM.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404, "Not Found")

    # ── POST ──────────────────────────────────────────────────────────────
    def do_POST(self):
        if self.path == "/submit":
            # Read Content-Length bytes from the request body
            length     = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(length)

            # ── Parse POST fields (replaces cgi.FieldStorage) ─────────────
            fields = _cgi_field_storage(body_bytes)
            name   = fields.get("name",  "").strip()
            email  = fields.get("email", "").strip()

            # ── Build validated HTML response ──────────────────────────────
            html  = _build_response_html(name, email)
            body  = html.encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404, "Not Found")


class ReusableHTTPServer(http.server.HTTPServer):
    """HTTPServer with SO_REUSEADDR so the port is freed immediately on stop."""
    allow_reuse_address = True


_cgi_server = None

def start_cgi_server(log):
    global _cgi_server
    try:
        # ReusableHTTPServer ensures port is released as soon as we call shutdown()
        _cgi_server = ReusableHTTPServer(("", CGI_PORT), CGIStyleHandler)
        log(f"Server started  →  http://localhost:{CGI_PORT}/")
        log("Open that URL in your browser to use the HTML form.")
        log("Fill name + email and submit — server validates server-side.")
        log("Press 'Stop Server' when done.\n")
        _cgi_server.serve_forever()   # blocks this thread until shutdown()
    except OSError as e:
        log(f"Server error: {e}  (Try stopping then starting again)")

def stop_cgi_server(log):
    global _cgi_server
    if _cgi_server:
        srv = _cgi_server
        _cgi_server = None
        def _shutdown():
            srv.shutdown()      # stop serve_forever() loop
            srv.server_close()  # release the socket so port is free immediately
        # Must run on a separate thread — shutdown() blocks until serve_forever() exits
        threading.Thread(target=_shutdown, daemon=True).start()
        log("Server stopped. Port is now free.")
    else:
        log("No server is running.")


# =============================================================================
#  ███████╗███████╗ ██████╗████████╗██╗ ██████╗ ███╗   ██╗     ██████╗
#  ██╔════╝██╔════╝██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║    ██╔════╝
#  ███████╗█████╗  ██║        ██║   ██║██║   ██║██╔██╗ ██║    ██║
#  ╚════██║██╔══╝  ██║        ██║   ██║██║   ██║██║╚██╗██║    ██║
#  ███████║███████╗╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║    ╚██████╗
#  ╚══════╝╚══════╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝     ╚═════╝
#  SQLite Database helpers  (Student Management)
# =============================================================================

DB_NAME = "students.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT    NOT NULL,
            age   INTEGER NOT NULL,
            email TEXT    UNIQUE NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def db_insert(name, age, email):
    conn = sqlite3.connect(DB_NAME)
    try:
        conn.execute("INSERT INTO users (name,age,email) VALUES (?,?,?)",
                     (name, int(age), email))
        conn.commit()
        return True, "Record inserted successfully!"
    except sqlite3.IntegrityError:
        conn.rollback()
        return False, "Error: Email already exists!"
    except Exception as e:
        conn.rollback()
        return False, f"Error: {e}"
    finally:
        conn.close()

def db_fetch_all():
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute("SELECT id,name,age,email FROM users").fetchall()
    conn.close()
    return rows

def db_search(keyword):
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute(
        "SELECT id,name,age,email FROM users WHERE name LIKE ? OR email LIKE ?",
        (f"%{keyword}%", f"%{keyword}%")
    ).fetchall()
    conn.close()
    return rows

def db_update(old_email, new_name, new_age, new_email):
    conn = sqlite3.connect(DB_NAME)
    try:
        cur = conn.execute(
            "UPDATE users SET name=?,age=?,email=? WHERE email=?",
            (new_name, int(new_age), new_email, old_email)
        )
        if cur.rowcount == 0:
            conn.rollback()
            return False, "No record found with that email!"
        conn.commit()
        return True, "Record updated successfully!"
    except sqlite3.IntegrityError:
        conn.rollback()
        return False, "Error: New email already exists!"
    except Exception as e:
        conn.rollback()
        return False, f"Error: {e}"
    finally:
        conn.close()

def db_delete(email):
    conn = sqlite3.connect(DB_NAME)
    try:
        cur = conn.execute("DELETE FROM users WHERE email=?", (email,))
        if cur.rowcount == 0:
            conn.rollback()
            return False, "No record found with that email!"
        conn.commit()
        return True, "Record deleted successfully!"
    except Exception as e:
        conn.rollback()
        return False, f"Error: {e}"
    finally:
        conn.close()


# =============================================================================
#  ██████╗ ██╗███╗   ██╗██╗███╗   ██╗ ██████╗
#  ██╔══██╗██║████╗  ██║██║████╗  ██║██╔════╝
#  ██║  ██║██║██╔██╗ ██║██║██╔██╗ ██║██║  ███╗
#  ██║  ██║██║██║╚██╗██║██║██║╚██╗██║██║   ██║
#  ██████╔╝██║██║ ╚████║██║██║ ╚████║╚██████╔╝
#  ╚═════╝ ╚═╝╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝ ╚═════╝
#  Dining Philosophers
# =============================================================================

class DiningPhilosophers:
    """
    5 philosophers, 5 forks (semaphores).
    Deadlock prevention: philosopher 4 picks RIGHT fork first,
    breaking the circular-wait condition.
    Uses acquire(timeout=0.2) so threads can notice stop() quickly
    without blocking forever on a held semaphore.
    """
    NUM = 5

    def __init__(self, log_cb):
        self.log     = log_cb
        self.forks   = [threading.Semaphore(1) for _ in range(self.NUM)]
        self.running = False

    def _philosopher(self, i):
        left  = i
        right = (i + 1) % self.NUM
        while self.running:
            # ── THINKING ─────────────────────────────────────────────────
            self.log(f"Philosopher {i}  — thinking...")
            time.sleep(random.uniform(0.5, 1.5))
            if not self.running:
                break

            # ── PICK UP FORKS (timeout so stop() is never blocked) ────────
            first, second = (right, left) if i == self.NUM - 1 else (left, right)

            # Wait for first fork with short timeout — retry if stopping
            while self.running:
                if self.forks[first].acquire(timeout=0.2):
                    break
            else:
                break   # running turned False while waiting

            self.log(f"Philosopher {i}  — picked fork {first}")

            # Wait for second fork
            while self.running:
                if self.forks[second].acquire(timeout=0.2):
                    break
            else:
                # Could not get second fork — release first and exit
                self.forks[first].release()
                break

            # ── EATING ───────────────────────────────────────────────────
            self.log(f"Philosopher {i}  — picked fork {second}  → EATING!")
            time.sleep(random.uniform(0.5, 1.0))

            # ── PUT DOWN FORKS ────────────────────────────────────────────
            self.forks[first].release()
            self.forks[second].release()
            self.log(f"Philosopher {i}  — done eating, put down forks")

    def start(self):
        self.running = True
        for i in range(self.NUM):
            threading.Thread(target=self._philosopher,
                             args=(i,), daemon=True).start()

    def stop(self):
        self.running = False


# =============================================================================
#   ██████╗ ██╗   ██╗██╗
#  ██╔════╝ ██║   ██║██║
#  ██║  ███╗██║   ██║██║
#  ██║   ██║██║   ██║██║
#  ╚██████╔╝╚██████╔╝██║
#   ╚═════╝  ╚═════╝ ╚═╝
#  Tkinter GUI  — tabbed launcher
# =============================================================================

# ── shared style constants ────────────────────────────────────────────────
BG    = "#1e1e2e"
CARD  = "#2a2a3e"
DARK  = "#13131f"
ACC   = "#7c3aed"
FG    = "#e2e8f0"
MUTED = "#94a3b8"
GREEN = "#86efac"
RED   = "#f87171"
GOLD  = "#fbbf24"
FONT  = ("Consolas", 10)
BOLD  = ("Consolas", 10, "bold")

def styled_btn(parent, text, cmd, color=ACC, width=20):
    return tk.Button(parent, text=text, command=cmd,
                     bg=color, fg="white", font=BOLD,
                     relief="flat", cursor="hand2", width=width,
                     activebackground=color, activeforeground="white")

def log_widget(parent, height=18, width=72):
    """Return a read-only scrolled Text widget."""
    t = scrolledtext.ScrolledText(parent, height=height, width=width,
                                  bg=DARK, fg=GREEN, font=("Consolas", 9),
                                  relief="flat", state="disabled",
                                  insertbackground=GREEN)
    return t

def log_write(widget, msg):
    """Thread-safe append to a log Text widget."""
    def _do():
        widget.config(state="normal")
        widget.insert(tk.END, msg + "\n")
        widget.see(tk.END)
        widget.config(state="disabled")
    widget.after(0, _do)


# ─────────────────────────────────────────────────────────────────────────────
#  TAB A — urllib Demo
# ─────────────────────────────────────────────────────────────────────────────

class UrllibTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self._build()

    def _build(self):
        # ── Header ───────────────────────────────────────────────────────
        tk.Label(self, text="Section A — Client-Side Scripting with urllib",
                 bg=BG, fg="#a78bfa", font=("Consolas", 13, "bold")
                 ).pack(pady=(14, 2))
        tk.Label(self, text="HTTP GET · HTTP POST · URL Parameter Passing · Validation",
                 bg=BG, fg=MUTED, font=("Consolas", 9)).pack(pady=(0, 8))

        content = tk.Frame(self, bg=BG)
        content.pack(fill="both", expand=True, padx=16, pady=4)

        # ── Left: controls ────────────────────────────────────────────────
        left = tk.LabelFrame(content, text=" Controls ", bg=CARD, fg=ACC,
                             font=BOLD, bd=2, relief="groove")
        left.pack(side="left", fill="y", padx=(0, 10))

        # Name / Email inputs (shared by POST + Part 3)
        for row, lbl in enumerate(["Name", "Email"]):
            tk.Label(left, text=lbl+":", bg=CARD, fg=FG,
                     font=FONT).grid(row=row, column=0,
                                     sticky="w", padx=12, pady=8)
            e = tk.Entry(left, width=22, bg=DARK, fg=FG,
                         insertbackground=FG, relief="flat",
                         font=FONT, bd=4)
            e.grid(row=row, column=1, padx=12, pady=8)
            setattr(self, f"e_{lbl.lower()}", e)

        sep = ttk.Separator(left, orient="horizontal")
        sep.grid(row=2, column=0, columnspan=2, sticky="ew",
                 padx=12, pady=6)

        # Buttons
        btn_specs = [
            ("Part 1 — GET Request",       "#0f766e", self._run_get),
            ("Part 2 — POST Request",      ACC,       self._run_post),
            ("Part 3 — GET with Params",   "#0369a1", self._run_params),
            ("Clear Log",                  "#334155", self._clear_log),
        ]
        for r, (txt, col, cmd) in enumerate(btn_specs, start=3):
            styled_btn(left, txt, cmd, color=col, width=22).grid(
                row=r, column=0, columnspan=2,
                pady=5, padx=12, sticky="ew")

        # Validation info box
        info = tk.LabelFrame(left, text=" Validation Rules ",
                             bg=CARD, fg=MUTED,
                             font=("Consolas", 8), bd=1)
        info.grid(row=8, column=0, columnspan=2,
                  sticky="ew", padx=12, pady=(12, 8))
        rules = ("• Name  : required, ≥ 2 chars\n"
                 "• Email : required, valid format\n"
                 "• Checked client-side before send\n"
                 "• Also checked server-side (CGI tab)")
        tk.Label(info, text=rules, bg=CARD, fg=MUTED,
                 font=("Consolas", 8), justify="left",
                 wraplength=200).pack(padx=8, pady=6)

        # ── Right: log ───────────────────────────────────────────────────
        right = tk.LabelFrame(content, text=" Output Log ",
                              bg=CARD, fg=ACC, font=BOLD,
                              bd=2, relief="groove")
        right.pack(side="left", fill="both", expand=True)

        self.log_box = log_widget(right, height=24, width=58)
        self.log_box.pack(fill="both", expand=True, padx=8, pady=8)

        self._log("Ready.  Enter name + email, then click a button.\n")

    # ── Runners ──────────────────────────────────────────────────────────
    def _log(self, msg):
        log_write(self.log_box, msg)

    def _clear_log(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", tk.END)
        self.log_box.config(state="disabled")

    def _run_get(self):
        self._log("Sending GET request (requires internet)...")
        threading.Thread(target=urllib_get_request,
                         args=(self._log,), daemon=True).start()

    def _run_post(self):
        name  = self.e_name.get()
        email = self.e_email.get()
        threading.Thread(target=urllib_post_request,
                         args=(name, email, self._log), daemon=True).start()

    def _run_params(self):
        name  = self.e_name.get()
        email = self.e_email.get()
        threading.Thread(target=urllib_get_with_params,
                         args=(name, email, self._log), daemon=True).start()


# ─────────────────────────────────────────────────────────────────────────────
#  TAB B — CGI Server
# ─────────────────────────────────────────────────────────────────────────────

class CGITab(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self._build()

    def _build(self):
        tk.Label(self, text="Section B — Server-Side Scripting with CGI",
                 bg=BG, fg="#a78bfa", font=("Consolas", 13, "bold")
                 ).pack(pady=(14, 2))
        tk.Label(self,
                 text="Python's built-in HTTP server + CGI · cgi.FieldStorage() · server-side validation",
                 bg=BG, fg=MUTED, font=("Consolas", 9)).pack(pady=(0, 8))

        content = tk.Frame(self, bg=BG)
        content.pack(fill="both", expand=True, padx=16, pady=4)

        # ── Left: controls ────────────────────────────────────────────────
        left = tk.LabelFrame(content, text=" Server Controls ",
                             bg=CARD, fg=ACC, font=BOLD,
                             bd=2, relief="groove")
        left.pack(side="left", fill="y", padx=(0, 10))

        # Status indicator
        self.status_lbl = tk.Label(left, text="● Server: STOPPED",
                                   bg=CARD, fg=RED, font=BOLD)
        self.status_lbl.pack(pady=(16, 4), padx=16)

        tk.Label(left,
                 text=f"Port: {CGI_PORT}\nURL: http://localhost:{CGI_PORT}/",
                 bg=CARD, fg=MUTED, font=("Consolas", 9),
                 justify="center").pack(pady=(0, 12))

        self.start_btn = styled_btn(left, "▶  Start CGI Server",
                                    self._start, color="#0f766e", width=22)
        self.start_btn.pack(pady=5, padx=16, fill="x")

        self.stop_btn = styled_btn(left, "⏹  Stop Server",
                                   self._stop, color="#be123c", width=22)
        self.stop_btn.pack(pady=5, padx=16, fill="x")
        self.stop_btn.config(state="disabled")

        styled_btn(left, "Open in Browser",
                   self._open_browser, color="#334155", width=22
                   ).pack(pady=5, padx=16, fill="x")

        # How-it-works note
        info = tk.LabelFrame(left, text=" How It Works ",
                             bg=CARD, fg=MUTED,
                             font=("Consolas", 8), bd=1)
        info.pack(fill="x", padx=12, pady=(20, 8))
        steps = ("1. Click 'Start CGI Server'\n"
                 "2. Click 'Open in Browser'\n"
                 "3. Fill the HTML form\n"
                 "4. Submit → CGI script runs\n"
                 "5. cgi.FieldStorage() reads fields\n"
                 "6. Server validates name+email\n"
                 "7. Returns Hello [name]... response")
        tk.Label(info, text=steps, bg=CARD, fg=MUTED,
                 font=("Consolas", 8), justify="left",
                 wraplength=200).pack(padx=8, pady=6)

        # ── Right: log ───────────────────────────────────────────────────
        right = tk.LabelFrame(content, text=" Server Log ",
                              bg=CARD, fg=ACC, font=BOLD,
                              bd=2, relief="groove")
        right.pack(side="left", fill="both", expand=True)

        self.log_box = log_widget(right, height=24, width=58)
        self.log_box.pack(fill="both", expand=True, padx=8, pady=8)

        self._log("Click 'Start CGI Server' to begin.\n")
        self._log("Server-side processing runs in-process (Python 3.13+ compatible).\n")
        self._log("HTML form served at:\n"
                  f"  http://localhost:{CGI_PORT}/\n")

    def _log(self, msg):
        log_write(self.log_box, msg)

    def _start(self):
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_lbl.config(text="● Server: RUNNING", fg=GREEN)
        threading.Thread(target=start_cgi_server,
                         args=(self._log,), daemon=True).start()

    def _stop(self):
        stop_cgi_server(self._log)
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_lbl.config(text="● Server: STOPPED", fg=RED)

    def _open_browser(self):
        import webbrowser
        webbrowser.open(f"http://localhost:{CGI_PORT}/")
        self._log(f"Opened browser → http://localhost:{CGI_PORT}/")


# ─────────────────────────────────────────────────────────────────────────────
#  TAB C — Student Management System
# ─────────────────────────────────────────────────────────────────────────────

class StudentTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        init_db()
        self._build()
        self.refresh_list()

    def _build(self):
        tk.Label(self, text="Section C — Student Management System",
                 bg=BG, fg="#a78bfa", font=("Consolas", 13, "bold")
                 ).pack(pady=(14, 2))
        tk.Label(self, text="Tkinter GUI · SQLite CRUD · Transactions · Dining Philosophers",
                 bg=BG, fg=MUTED, font=("Consolas", 9)).pack(pady=(0, 8))

        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=16, pady=4)

        # ── Left: form ────────────────────────────────────────────────────
        form_frame = tk.LabelFrame(main, text=" User Details ",
                                   bg=CARD, fg=ACC, font=BOLD,
                                   bd=2, relief="groove")
        form_frame.pack(side="left", fill="y", padx=(0, 10), pady=4)

        self.entries = {}
        for i, lbl in enumerate(["Name", "Age", "Email"]):
            tk.Label(form_frame, text=lbl+":", bg=CARD, fg=FG,
                     font=FONT).grid(row=i, column=0,
                                     sticky="w", padx=12, pady=8)
            e = tk.Entry(form_frame, width=22, bg=DARK, fg=FG,
                         insertbackground=FG, relief="flat",
                         font=FONT, bd=4)
            e.grid(row=i, column=1, padx=12, pady=8)
            self.entries[lbl.lower()] = e

        self.greet_lbl = tk.Label(form_frame, text="", bg=CARD,
                                  fg=GREEN, font=("Consolas", 9, "italic"),
                                  wraplength=200)
        self.greet_lbl.grid(row=3, column=0, columnspan=2, pady=(0, 4))

        btn_specs = [
            ("➕  Add Record",     "#0f766e", self.add_record),
            ("✏️  Update Record",  ACC,       self.update_record),
            ("🗑️  Delete Record",  "#be123c", self.delete_record),
            ("🔍  Search Record",  "#0369a1", self.search_record),
            ("👋  Greet Selected", "#b45309", self.greet_selected),
            ("🔄  Refresh List",   "#334155", self.refresh_list),
            ("🍝  Dining Philos.", "#4c1d95", self.open_dining),
        ]
        for r, (txt, col, cmd) in enumerate(btn_specs, start=4):
            styled_btn(form_frame, txt, cmd, color=col, width=18).grid(
                row=r, column=0, columnspan=2,
                pady=4, padx=12, sticky="ew")

        # ── Right: listbox ────────────────────────────────────────────────
        list_frame = tk.LabelFrame(main, text=" Records ",
                                   bg=CARD, fg=ACC, font=BOLD,
                                   bd=2, relief="groove")
        list_frame.pack(side="left", fill="both", expand=True, pady=4)

        tk.Label(list_frame, text="ID    Name               Age    Email",
                 bg=CARD, fg=MUTED,
                 font=("Consolas", 9)).pack(anchor="w", padx=10, pady=(6, 2))

        # Pre-loaded example names
        ex_frame = tk.LabelFrame(list_frame, text=" Quick-Select Names ",
                                 bg=CARD, fg=MUTED,
                                 font=("Consolas", 8), bd=1)
        ex_frame.pack(fill="x", padx=10, pady=(0, 4))
        self.name_listbox = tk.Listbox(
            ex_frame, selectmode="single",
            bg=DARK, fg=GOLD, selectbackground=ACC,
            font=("Consolas", 9), relief="flat", bd=0, height=3)
        for n in ["Alice", "Bob", "Charlie", "Diana", "Eve"]:
            self.name_listbox.insert(tk.END, f"  {n}")
        self.name_listbox.pack(fill="x", padx=4, pady=4)
        self.name_listbox.bind("<<ListboxSelect>>", self.on_name_select)

        tk.Label(list_frame, text="Database Records:",
                 bg=CARD, fg=MUTED,
                 font=("Consolas", 9)).pack(anchor="w", padx=10, pady=(2, 0))

        lb_wrap = tk.Frame(list_frame, bg=CARD)
        lb_wrap.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        sb = tk.Scrollbar(lb_wrap, orient="vertical")
        self.listbox = tk.Listbox(
            lb_wrap, selectmode="extended",
            yscrollcommand=sb.set,
            bg=DARK, fg=FG, selectbackground=ACC,
            font=("Consolas", 10), relief="flat", bd=0,
            activestyle="none", height=16)
        sb.config(command=self.listbox.yview)
        sb.pack(side="right", fill="y")
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        self.status = tk.Label(self, text="Ready", bg=DARK, fg=MUTED,
                               font=("Consolas", 9), anchor="w")
        self.status.pack(fill="x", side="bottom", padx=10, pady=4)

    # ── CRUD ─────────────────────────────────────────────────────────────
    def add_record(self):
        name  = self.entries["name"].get().strip()
        age   = self.entries["age"].get().strip()
        email = self.entries["email"].get().strip()
        if not all([name, age, email]):
            messagebox.showwarning("Missing", "Please fill all fields!")
            return
        if not age.isdigit():
            messagebox.showwarning("Invalid", "Age must be a number!")
            return
        ok_e, err_e = validate_email(email)
        if not ok_e:
            messagebox.showwarning("Invalid", err_e)
            return
        ok, msg = db_insert(name, age, email)
        if ok:
            self.clear_entries(); self.refresh_list()
            self.status.config(text=msg, fg=GREEN)
        else:
            messagebox.showerror("Error", msg)

    def update_record(self):
        old_email = self.entries["email"].get().strip()
        if not old_email:
            messagebox.showwarning("Missing",
                                   "Select a record or enter email to update!")
            return
        name      = self.entries["name"].get().strip()
        age       = self.entries["age"].get().strip()
        new_email = simpledialog.askstring(
            "New Email", "Enter new email:",
            initialvalue=old_email, parent=self)
        if new_email is None:
            return
        new_email = new_email.strip() or old_email
        ok_e, err_e = validate_email(new_email)
        if not ok_e:
            messagebox.showwarning("Invalid", err_e)
            return
        ok, msg = db_update(old_email, name, age, new_email)
        if ok:
            self.clear_entries(); self.refresh_list()
            self.status.config(text=msg, fg=GREEN)
        else:
            messagebox.showerror("Error", msg)

    def delete_record(self):
        email = self.entries["email"].get().strip()
        if not email:
            messagebox.showwarning("Missing",
                                   "Enter or select a record to delete!")
            return
        if not messagebox.askyesno("Confirm",
                                   f"Delete record:\n{email}?"):
            return
        ok, msg = db_delete(email)
        if ok:
            self.clear_entries(); self.refresh_list()
            self.status.config(text=msg, fg=RED)
        else:
            messagebox.showerror("Error", msg)

    def search_record(self):
        kw = (self.entries["name"].get().strip() or
              self.entries["email"].get().strip())
        if not kw:
            messagebox.showwarning("Search",
                                   "Enter name or email to search!")
            return
        rows = db_search(kw)
        self.listbox.delete(0, tk.END)
        if rows:
            for r in rows:
                self.listbox.insert(
                    tk.END, f"  {r[0]:<4} {r[1]:<18} {r[2]:<6} {r[3]}")
            self.status.config(
                text=f"Found {len(rows)} result(s) for '{kw}'.", fg=GOLD)
        else:
            self.listbox.insert(tk.END, "  No records found.")
            self.status.config(text=f"No results for '{kw}'.", fg=RED)

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for r in db_fetch_all():
            self.listbox.insert(
                tk.END, f"  {r[0]:<4} {r[1]:<18} {r[2]:<6} {r[3]}")
        self.status.config(
            text=f"{len(db_fetch_all())} record(s) loaded.", fg=MUTED)

    def on_select(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        rows = db_fetch_all()
        idx  = sel[0]
        if idx < len(rows):
            r = rows[idx]
            for key, val in zip(["name","age","email"], [r[1],r[2],r[3]]):
                self.entries[key].delete(0, tk.END)
                self.entries[key].insert(0, val)

    def on_name_select(self, event):
        sel = self.name_listbox.curselection()
        if not sel:
            return
        name = self.name_listbox.get(sel[0]).strip()
        self.entries["name"].delete(0, tk.END)
        self.entries["name"].insert(0, name)
        self.greet_lbl.config(text=f"Hello, {name}! Welcome!")

    def greet_selected(self):
        name = self.entries["name"].get().strip()
        if name:
            self.greet_lbl.config(text=f"Hello, {name}! Welcome!")
            messagebox.showinfo("Greeting",
                                f"Hello, {name}! Welcome to the system.")
        else:
            messagebox.showwarning("Select",
                                   "Enter or select a name first!")

    def clear_entries(self):
        for e in self.entries.values():
            e.delete(0, tk.END)

    # ── Dining Philosophers pop-up ────────────────────────────────────────
    def open_dining(self):
        win = tk.Toplevel(self)
        win.title("Dining Philosophers — Sync Demo")
        win.geometry("540x520")
        win.configure(bg=DARK)
        win.resizable(False, False)

        tk.Label(win, text="Dining Philosophers Problem",
                 bg=DARK, fg="#a78bfa",
                 font=("Consolas", 13, "bold")).pack(pady=10)
        tk.Label(win,
                 text=("5 philosophers · 5 forks (semaphores)\n"
                       "Philosopher 4 picks RIGHT fork first"
                       " → breaks circular wait → no deadlock"),
                 bg=DARK, fg=MUTED, font=("Consolas", 9),
                 justify="center").pack()

        lbox = log_widget(win, height=20, width=64)
        lbox.pack(padx=14, pady=8)

        def log(m):  log_write(lbox, m)

        dp = DiningPhilosophers(log)

        bf = tk.Frame(win, bg=DARK); bf.pack(pady=6)

        def start():
            dp.start()
            s_btn.config(state="disabled")
            x_btn.config(state="normal")
            log("Simulation started — no deadlock will occur!")

        def stop():
            dp.stop()
            s_btn.config(state="normal")
            x_btn.config(state="disabled")
            log("Simulation stopped.")

        s_btn = styled_btn(bf, "Start Simulation", start,
                           color=ACC, width=18)
        s_btn.pack(side="left", padx=8)
        x_btn = styled_btn(bf, "Stop", stop,
                           color="#be123c", width=10)
        x_btn.pack(side="left", padx=8)
        x_btn.config(state="disabled")

        win.protocol("WM_DELETE_WINDOW",
                     lambda: [dp.stop(), win.destroy()])


# ─────────────────────────────────────────────────────────────────────────────
#  Main App Window
# ─────────────────────────────────────────────────────────────────────────────

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python Assignments — urllib · CGI · Student Management")
        self.geometry("980x720")
        self.resizable(True, True)
        self.configure(bg=BG)
        self._build_menu()
        self._build_tabs()

    def _build_menu(self):
        mb = tk.Menu(self)

        fm = tk.Menu(mb, tearoff=0)
        fm.add_command(label="Open File…",
                       command=lambda: filedialog.askopenfilename(
                           title="Open",
                           filetypes=[("All files","*.*"),
                                      ("Text","*.txt"),
                                      ("CSV","*.csv")]))
        fm.add_command(label="Save Export",    command=self._save_export)
        fm.add_separator()
        fm.add_command(label="Exit",           command=self._on_exit)
        mb.add_cascade(label="File", menu=fm)

        hm = tk.Menu(mb, tearoff=0)
        hm.add_command(label="About",
                       command=lambda: messagebox.showinfo(
                           "About",
                           "Combined Python Assignment\n"
                           "urllib · CGI · Tkinter · SQLite\n"
                           "Dining Philosophers"))
        mb.add_cascade(label="Help", menu=hm)

        self.config(menu=mb)

    def _build_tabs(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook",
                        background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=CARD, foreground=FG,
                        font=BOLD, padding=[14, 6])
        style.map("TNotebook.Tab",
                  background=[("selected", ACC)],
                  foreground=[("selected", "white")])

        tab_a = UrllibTab(nb)
        tab_b = CGITab(nb)
        tab_c = StudentTab(nb)

        nb.add(tab_a, text="  Section A — urllib  ")
        nb.add(tab_b, text="  Section B — CGI     ")
        nb.add(tab_c, text="  Section C — Student DB  ")

    def _save_export(self):
        rows = db_fetch_all()
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file","*.txt"),("CSV","*.csv")])
        if path:
            with open(path, "w") as f:
                f.write("ID | Name | Age | Email\n" + "-"*50 + "\n")
                for r in rows:
                    f.write(f"{r[0]} | {r[1]} | {r[2]} | {r[3]}\n")
            messagebox.showinfo("Saved", f"Exported to:\n{path}")

    def _on_exit(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.destroy()


# =============================================================================
if __name__ == "__main__":
    app = MainApp()
    app.protocol("WM_DELETE_WINDOW", app._on_exit)
    app.mainloop()
