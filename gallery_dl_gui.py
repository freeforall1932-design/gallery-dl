#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gallery-dl GUI - Phase 3: Authentication & Input Methods
A graphical user interface for gallery-dl image downloader
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import subprocess
import sys
import os
import json

class GalleryDLGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("gallery-dl GUI")
        self.root.geometry("1000x750")
        self.root.minsize(850, 650)
        
        # Queue for thread-safe logging
        self.log_queue = queue.Queue()
        
        # Download state
        self.is_downloading = False
        self.process = None
        
        # Setup UI
        self.setup_styles()
        self.create_menu()
        self.create_main_layout()
        self.create_status_bar()
        
        # Start log update loop
        self.update_log()
        
    def setup_styles(self):
        """Configure ttk styles for better appearance"""
        style = ttk.Style()
        
        # Try to use a modern theme
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'vista' in available_themes:
            style.theme_use('vista')
        
        # Configure colors
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Section.TLabel', font=('Helvetica', 11, 'bold'))
        style.configure('Action.TButton', padding=(10, 5))
        
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load URLs from file...", command=self.load_urls_from_file)
        file_menu.add_command(label="Save URLs to file...", command=self.save_urls_to_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Extractor Info", command=self.show_extractor_info)
        tools_menu.add_command(label="List Keywords", command=self.list_keywords)
        tools_menu.add_separator()
        tools_menu.add_command(label="Configuration...", command=self.open_config)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="gallery-dl Documentation", command=self.open_docs)
        
    def create_main_layout(self):
        """Create the main layout with all sections"""
        # Main container with scrollbar
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create canvas with scrollbar for scrollable content
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ===== Notebook for Tabs =====
        notebook = ttk.Notebook(scrollable_frame)
        notebook.pack(fill=tk.X, padx=10, pady=5)
        
        # Create tabs
        self.urls_tab = ttk.Frame(notebook, padding=10)
        self.auth_tab = ttk.Frame(notebook, padding=10)
        self.input_tab = ttk.Frame(notebook, padding=10)
        self.advanced_tab = ttk.Frame(notebook, padding=10)  # Phase 2
        
        notebook.add(self.urls_tab, text="URLs")
        notebook.add(self.auth_tab, text="Authentication")
        notebook.add(self.input_tab, text="Input Methods")
        notebook.add(self.advanced_tab, text="Advanced")  # Phase 2
        
        # ===== URL Input Section (in URLs tab) =====
        url_frame = ttk.LabelFrame(self.urls_tab, text="URLs to Download", padding=10)
        url_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(url_frame, text="Enter one or more URLs (one per line):", 
                 style='Section.TLabel').pack(anchor=tk.W)
        
        self.url_text = tk.Text(url_frame, height=6, wrap=tk.WORD)
        self.url_text.pack(fill=tk.X, pady=5)
        
        # URL buttons frame
        url_btn_frame = ttk.Frame(url_frame)
        url_btn_frame.pack(fill=tk.X)
        
        ttk.Button(url_btn_frame, text="Load from File...", 
                  command=self.load_urls_from_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(url_btn_frame, text="Clear", 
                  command=lambda: self.url_text.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=2)
        ttk.Button(url_btn_frame, text="Paste from Clipboard", 
                  command=self.paste_urls).pack(side=tk.LEFT, padx=2)
        
        # ===== Authentication Section (in Auth tab) =====
        self.create_auth_section()
        
        # ===== Input Methods Section (in Input tab) =====
        self.create_input_methods_section()
        
        # ===== Advanced Section (in Advanced tab) - Phase 2 =====
        self.create_advanced_section()
        
        # Close notebook to allow other sections
        # ===== Destination Section =====
        dest_frame = ttk.LabelFrame(scrollable_frame, text="Download Destination", padding=10)
        dest_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(dest_frame, text="Destination Directory:").pack(anchor=tk.W)
        
        dest_input_frame = ttk.Frame(dest_frame)
        dest_input_frame.pack(fill=tk.X, pady=5)
        
        self.dest_var = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.dest_entry = ttk.Entry(dest_input_frame, textvariable=self.dest_var)
        self.dest_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(dest_input_frame, text="Browse...", 
                  command=self.browse_destination).pack(side=tk.LEFT)
        
        # ===== Basic Options Section =====
        options_frame = ttk.LabelFrame(scrollable_frame, text="Basic Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # First row of options
        opt_row1 = ttk.Frame(options_frame)
        opt_row1.pack(fill=tk.X, pady=2)
        
        self.simulate_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt_row1, text="Simulate (no download)", 
                       variable=self.simulate_var).pack(side=tk.LEFT, padx=10)
        
        self.quiet_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt_row1, text="Quiet mode", 
                       variable=self.quiet_var).pack(side=tk.LEFT, padx=10)
        
        self.verbose_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt_row1, text="Verbose", 
                       variable=self.verbose_var).pack(side=tk.LEFT, padx=10)
        
        # Second row of options
        opt_row2 = ttk.Frame(options_frame)
        opt_row2.pack(fill=tk.X, pady=2)
        
        self.get_urls_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt_row2, text="Get URLs only", 
                       variable=self.get_urls_var).pack(side=tk.LEFT, padx=10)
        
        self.dump_json_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt_row2, text="Dump JSON", 
                       variable=self.dump_json_var).pack(side=tk.LEFT, padx=10)
        
        # Filename format
        filename_frame = ttk.Frame(options_frame)
        filename_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filename_frame, text="Filename Format:").pack(side=tk.LEFT)
        self.filename_var = tk.StringVar(value="{category}_{id}.{extension}")
        filename_entry = ttk.Entry(filename_frame, textvariable=self.filename_var)
        filename_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        ttk.Button(filename_frame, text="Reset", 
                  command=lambda: self.filename_var.set("{category}_{id}.{extension}")).pack(side=tk.LEFT)
        
        # ===== Action Buttons Section =====
        action_frame = ttk.Frame(scrollable_frame)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_btn = ttk.Button(action_frame, text="▶ Start Download", 
                                    style='Action.TButton',
                                    command=self.start_download)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(action_frame, text="⏹ Stop", 
                                   style='Action.TButton',
                                   command=self.stop_download,
                                   state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_log_btn = ttk.Button(action_frame, text="Clear Log", 
                                        command=self.clear_log)
        self.clear_log_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress indicator
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(action_frame, variable=self.progress_var, 
                                            maximum=100, mode='indeterminate')
        self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=10)
        
        # ===== Output Log Section =====
        log_frame = ttk.LabelFrame(scrollable_frame, text="Output Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, 
                                      command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure text tags for coloring
        self.log_text.tag_configure('info', foreground='black')
        self.log_text.tag_configure('success', foreground='green')
        self.log_text.tag_configure('warning', foreground='orange')
        self.log_text.tag_configure('error', foreground='red')
        self.log_text.tag_configure('debug', foreground='gray')
        
    def create_advanced_section(self):
        """Create advanced options section in Advanced tab - Phase 2"""
        # Network Settings
        net_frame = ttk.LabelFrame(self.advanced_tab, text="Network Settings", padding=10)
        net_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Proxy
        proxy_frame = ttk.Frame(net_frame)
        proxy_frame.pack(fill=tk.X, pady=3)
        ttk.Label(proxy_frame, text="Proxy:", width=15).pack(side=tk.LEFT)
        self.proxy_var = tk.StringVar()
        proxy_entry = ttk.Entry(proxy_frame, textvariable=self.proxy_var, width=40)
        proxy_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(proxy_frame, text="(e.g., http://host:port)", foreground="gray").pack(side=tk.LEFT)
        
        # User-Agent
        ua_frame = ttk.Frame(net_frame)
        ua_frame.pack(fill=tk.X, pady=3)
        ttk.Label(ua_frame, text="User-Agent:", width=15).pack(side=tk.LEFT)
        self.ua_var = tk.StringVar()
        ua_entry = ttk.Entry(ua_frame, textvariable=self.ua_var, width=40)
        ua_entry.pack(side=tk.LEFT, padx=5)
        
        # Retries and Timeout
        retry_frame = ttk.Frame(net_frame)
        retry_frame.pack(fill=tk.X, pady=3)
        ttk.Label(retry_frame, text="Retries:", width=15).pack(side=tk.LEFT)
        self.retries_var = tk.StringVar(value="4")
        retries_spin = ttk.Spinbox(retry_frame, from_=0, to=20, textvariable=self.retries_var, width=5)
        retries_spin.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(retry_frame, text="Timeout (s):", width=12).pack(side=tk.LEFT, padx=(20,0))
        self.timeout_var = tk.StringVar(value="30")
        timeout_spin = ttk.Spinbox(retry_frame, from_=1, to=300, textvariable=self.timeout_var, width=5)
        timeout_spin.pack(side=tk.LEFT, padx=5)
        
        # Connection options
        conn_frame = ttk.Frame(net_frame)
        conn_frame.pack(fill=tk.X, pady=3)
        self.ipv4_var = tk.BooleanVar()
        ttk.Checkbutton(conn_frame, text="Force IPv4", variable=self.ipv4_var).pack(side=tk.LEFT, padx=10)
        self.ipv6_var = tk.BooleanVar()
        ttk.Checkbutton(conn_frame, text="Force IPv6", variable=self.ipv6_var).pack(side=tk.LEFT, padx=10)
        self.no_check_cert_var = tk.BooleanVar()
        ttk.Checkbutton(conn_frame, text="Skip SSL Verification", variable=self.no_check_cert_var).pack(side=tk.LEFT, padx=10)
        
        # Rate Limiting & Sleep
        rate_frame = ttk.LabelFrame(self.advanced_tab, text="Rate Limiting & Sleep", padding=10)
        rate_frame.pack(fill=tk.X, padx=5, pady=5)
        
        sleep_frame = ttk.Frame(rate_frame)
        sleep_frame.pack(fill=tk.X, pady=3)
        ttk.Label(sleep_frame, text="Sleep (sec):", width=15).pack(side=tk.LEFT)
        self.sleep_var = tk.StringVar()
        sleep_entry = ttk.Entry(sleep_frame, textvariable=self.sleep_var, width=10)
        sleep_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(sleep_frame, text="Wait between downloads", foreground="gray").pack(side=tk.LEFT)
        
        ratelimit_frame = ttk.Frame(rate_frame)
        ratelimit_frame.pack(fill=tk.X, pady=3)
        ttk.Label(ratelimit_frame, text="Rate Limit:", width=15).pack(side=tk.LEFT)
        self.rate_limit_var = tk.StringVar()
        ratelimit_entry = ttk.Entry(ratelimit_frame, textvariable=self.rate_limit_var, width=10)
        ratelimit_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(ratelimit_frame, text="KB/s (0 = unlimited)", foreground="gray").pack(side=tk.LEFT)
        
        # File Handling
        file_frame = ttk.LabelFrame(self.advanced_tab, text="File Handling", padding=10)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        chunk_frame = ttk.Frame(file_frame)
        chunk_frame.pack(fill=tk.X, pady=3)
        ttk.Label(chunk_frame, text="Chunk Size (KB):", width=15).pack(side=tk.LEFT)
        self.chunk_size_var = tk.StringVar(value="256")
        chunk_spin = ttk.Spinbox(chunk_frame, from_=64, to=4096, textvariable=self.chunk_size_var, width=5)
        chunk_spin.pack(side=tk.LEFT, padx=5)
        
        part_frame = ttk.Frame(file_frame)
        part_frame.pack(fill=tk.X, pady=3)
        self.part_files_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(part_frame, text="Use .part files during download", variable=self.part_files_var).pack(side=tk.LEFT, padx=10)
        
        self.skip_download_var = tk.BooleanVar()
        ttk.Checkbutton(part_frame, text="Skip download (metadata only)", variable=self.skip_download_var).pack(side=tk.LEFT, padx=10)
        
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_auth_section(self):
        """Create authentication section in Auth tab"""
        # Cookies section
        cookies_frame = ttk.LabelFrame(self.auth_tab, text="Authentication Methods", padding=10)
        cookies_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Cookie file option
        cookie_file_frame = ttk.Frame(cookies_frame)
        cookie_file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(cookie_file_frame, text="Cookie File (Netscape format):").pack(anchor=tk.W)
        
        self.cookie_file_var = tk.StringVar()
        cookie_input_frame = ttk.Frame(cookie_file_frame)
        cookie_input_frame.pack(fill=tk.X, pady=2)
        
        self.cookie_file_entry = ttk.Entry(cookie_input_frame, textvariable=self.cookie_file_var)
        self.cookie_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(cookie_input_frame, text="Browse...", 
                  command=self.browse_cookie_file).pack(side=tk.LEFT)
        
        # Username/Password option
        creds_frame = ttk.Frame(cookies_frame)
        creds_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(creds_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(creds_frame, textvariable=self.username_var, width=30)
        username_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(creds_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(creds_frame, textvariable=self.password_var, show="*", width=30)
        password_entry.grid(row=1, column=1, padx=5, pady=2)
        
        # Show/hide password toggle
        self.show_password_var = tk.BooleanVar(value=False)
        show_pass_cb = ttk.Checkbutton(creds_frame, text="Show password", 
                                       variable=self.show_password_var,
                                       command=self.toggle_password_visibility)
        show_pass_cb.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # OAuth/Refresh token option
        oauth_frame = ttk.LabelFrame(cookies_frame, text="OAuth / Token Authentication", padding=5)
        oauth_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(oauth_frame, text="API Key / Token:").pack(anchor=tk.W)
        self.api_key_var = tk.StringVar()
        api_key_entry = ttk.Entry(oauth_frame, textvariable=self.api_key_var, width=50)
        api_key_entry.pack(fill=tk.X, pady=2)
        
        ttk.Label(oauth_frame, text="OAuth Refresh Token:").pack(anchor=tk.W)
        self.oauth_token_var = tk.StringVar()
        oauth_token_entry = ttk.Entry(oauth_frame, textvariable=self.oauth_token_var, width=50)
        oauth_token_entry.pack(fill=tk.X, pady=2)
        
        # Netrc option
        netrc_frame = ttk.Frame(cookies_frame)
        netrc_frame.pack(fill=tk.X, pady=5)
        
        self.use_netrc_var = tk.BooleanVar(value=False)
        netrc_cb = ttk.Checkbutton(netrc_frame, text="Use .netrc file for authentication", 
                                   variable=self.use_netrc_var)
        netrc_cb.pack(side=tk.LEFT)
        
        ttk.Button(netrc_frame, text="Edit .netrc", 
                  command=self.edit_netrc).pack(side=tk.LEFT, padx=10)
        
        # Browser cookies extraction
        browser_frame = ttk.LabelFrame(cookies_frame, text="Extract Cookies from Browser", padding=5)
        browser_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(browser_frame, text="Select browser to extract cookies:").pack(anchor=tk.W)
        
        browser_select_frame = ttk.Frame(browser_frame)
        browser_select_frame.pack(fill=tk.X, pady=2)
        
        self.browser_var = tk.StringVar(value="chrome")
        browsers = [("Chrome", "chrome"), ("Firefox", "firefox"), ("Edge", "edge"), 
                   ("Opera", "opera"), ("Safari", "safari")]
        
        for text, value in browsers:
            ttk.Radiobutton(browser_select_frame, text=text, value=value, 
                           variable=self.browser_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(browser_frame, text="Extract Cookies", 
                  command=self.extract_browser_cookies).pack(pady=5)
        
    def create_input_methods_section(self):
        """Create input methods section in Input tab"""
        input_frame = ttk.LabelFrame(self.input_tab, text="Alternative Input Methods", padding=10)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Gallery URL list file
        file_input_frame = ttk.LabelFrame(input_frame, text="File-based Input", padding=10)
        file_input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_input_frame, text="URL List File:").pack(anchor=tk.W)
        self.url_list_file_var = tk.StringVar()
        url_list_frame = ttk.Frame(file_input_frame)
        url_list_frame.pack(fill=tk.X, pady=2)
        
        self.url_list_entry = ttk.Entry(url_list_frame, textvariable=self.url_list_file_var)
        self.url_list_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(url_list_frame, text="Browse...", 
                  command=self.browse_url_list).pack(side=tk.LEFT)
        
        # Search query input
        search_frame = ttk.LabelFrame(input_frame, text="Search Query Input", padding=10)
        search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(search_frame, text="Search Keywords:").pack(anchor=tk.W)
        self.search_query_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_query_var, width=60)
        search_entry.pack(fill=tk.X, pady=2)
        
        ttk.Label(search_frame, text="Supported sites: Danbooru, Gelbooru, Safebooru, etc.").pack(anchor=tk.W)
        
        # User/Gallery ID input
        id_frame = ttk.LabelFrame(input_frame, text="User/Gallery ID Input", padding=10)
        id_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(id_frame, text="User ID / Username:").pack(anchor=tk.W)
        self.user_id_var = tk.StringVar()
        user_id_entry = ttk.Entry(id_frame, textvariable=self.user_id_var, width=60)
        user_id_entry.pack(fill=tk.X, pady=2)
        
        ttk.Label(id_frame, text="Gallery/Album ID:").pack(anchor=tk.W)
        self.gallery_id_var = tk.StringVar()
        gallery_id_entry = ttk.Entry(id_frame, textvariable=self.gallery_id_var, width=60)
        gallery_id_entry.pack(fill=tk.X, pady=2)
        
        # Helper buttons
        helper_frame = ttk.Frame(input_frame)
        helper_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(helper_frame, text="Get User ID from URL", 
                  command=self.get_user_id_from_url).pack(side=tk.LEFT, padx=5)
        ttk.Button(helper_frame, text="Validate IDs", 
                  command=self.validate_ids).pack(side=tk.LEFT, padx=5)
        
    def browse_cookie_file(self):
        """Browse for cookie file"""
        file_path = filedialog.askopenfilename(
            title="Select Cookie File",
            filetypes=[("All files", "*.*"), ("Text files", "*.txt")]
        )
        if file_path:
            self.cookie_file_var.set(file_path)
            
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        for widget in self.auth_tab.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, ttk.Entry) and grandchild.cget('show') == '*':
                                grandchild.config(show='')
                            elif isinstance(grandchild, ttk.Entry) and grandchild.cget('show') == '':
                                grandchild.config(show='*')
                                
    def edit_netrc(self):
        """Edit .netrc file"""
        import os
        netrc_path = os.path.expanduser("~/.netrc")
        
        if not os.path.exists(netrc_path):
            # Create default .netrc
            with open(netrc_path, 'w') as f:
                f.write("# .netrc file for gallery-dl authentication\n")
                f.write("# machine example.com\n")
                f.write("# login username\n")
                f.write("# password password\n")
        
        # Try to open with default editor
        try:
            if sys.platform == 'win32':
                os.startfile(netrc_path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', netrc_path])
            else:
                subprocess.run(['xdg-open', netrc_path])
        except Exception as e:
            messagebox.showinfo("Info", f".netrc file location: {netrc_path}\n\nEdit this file manually to add credentials.")
            
    def extract_browser_cookies(self):
        """Extract cookies from selected browser"""
        browser = self.browser_var.get()
        self.log_message(f"Extracting cookies from {browser}...", 'info')
        
        cmd = [sys.executable, "-m", "gallery_dl", "--cookies-from-browser", browser]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.log_message(f"Cookies extracted successfully from {browser}", 'success')
            else:
                self.log_message(f"Cookie extraction failed: {result.stderr}", 'error')
        except subprocess.TimeoutExpired:
            self.log_message("Cookie extraction timed out", 'error')
        except Exception as e:
            self.log_message(f"Error extracting cookies: {str(e)}", 'error')
            
    def browse_url_list(self):
        """Browse for URL list file"""
        file_path = filedialog.askopenfilename(
            title="Select URL List File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.url_list_file_var.set(file_path)
            
    def get_user_id_from_url(self):
        """Extract user ID from a URL"""
        # Simple implementation - in real app would parse various site formats
        urls = self.url_text.get(1.0, tk.END).strip().split('\n')
        urls = [u.strip() for u in urls if u.strip()]
        
        if not urls:
            messagebox.showwarning("Warning", "Please enter a URL first")
            return
            
        # Just show the first URL's potential user ID
        url = urls[0]
        self.log_message(f"Analyzing URL: {url}", 'debug')
        messagebox.showinfo("Info", "User ID extraction is site-specific.\n\nThis feature will be enhanced in future phases to support automatic extraction for all supported sites.")
        
    def validate_ids(self):
        """Validate entered IDs"""
        user_id = self.user_id_var.get().strip()
        gallery_id = self.gallery_id_var.get().strip()
        
        if not user_id and not gallery_id:
            messagebox.showwarning("Warning", "Please enter at least one ID to validate")
            return
            
        self.log_message("Validating IDs...", 'info')
        # Placeholder - actual validation would check against specific sites
        messagebox.showinfo("Validation", "ID validation is site-specific.\n\nThis feature will check if the IDs exist and are accessible in future phases.")

    def browse_destination(self):
        """Open directory browser"""
        directory = filedialog.askdirectory(initialdir=self.dest_var.get())
        if directory:
            self.dest_var.set(directory)
            
    def paste_urls(self):
        """Paste URLs from clipboard"""
        try:
            clipboard = self.root.clipboard_get()
            self.url_text.insert(tk.END, clipboard + "\n")
        except tk.TclError:
            messagebox.showwarning("Warning", "Clipboard is empty or not accessible")
            
    def load_urls_from_file(self):
        """Load URLs from a text file"""
        file_path = filedialog.askopenfilename(
            title="Load URLs from file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    urls = f.read()
                self.url_text.insert(tk.END, urls + "\n")
                self.log_message(f"Loaded URLs from {file_path}", 'info')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
                
    def save_urls_to_file(self):
        """Save current URLs to a file"""
        urls = self.url_text.get(1.0, tk.END).strip()
        if not urls:
            messagebox.showwarning("Warning", "No URLs to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save URLs to file",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(urls)
                self.log_message(f"Saved URLs to {file_path}", 'success')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
                
    def build_command(self):
        """Build gallery-dl command from current settings"""
        cmd = [sys.executable, "-m", "gallery_dl"]
        
        # Get URLs - check both main URL text and input methods
        urls = self.url_text.get(1.0, tk.END).strip().split('\n')
        urls = [u.strip() for u in urls if u.strip()]
        
        # Add URLs from file-based input if specified
        url_list_file = self.url_list_file_var.get().strip()
        if url_list_file and os.path.exists(url_list_file):
            with open(url_list_file, 'r', encoding='utf-8') as f:
                file_urls = [line.strip() for line in f if line.strip()]
                urls.extend(file_urls)
        
        # Add search query if specified
        search_query = self.search_query_var.get().strip()
        if search_query:
            # Convert search query to URL format for supported sites
            # This is a simplified version - real implementation would handle multiple sites
            urls.append(f"https://danbooru.donmai.us/posts?tags={search_query.replace(' ', '+')}")
        
        # Add user ID if specified
        user_id = self.user_id_var.get().strip()
        if user_id:
            # Placeholder - would convert to appropriate site URL
            self.log_message(f"User ID input: {user_id} (site-specific URL generation needed)", 'debug')
        
        # Add gallery ID if specified  
        gallery_id = self.gallery_id_var.get().strip()
        if gallery_id:
            # Placeholder - would convert to appropriate site URL
            self.log_message(f"Gallery ID input: {gallery_id} (site-specific URL generation needed)", 'debug')
        
        if not urls:
            messagebox.showwarning("Warning", "Please enter at least one URL or use input methods")
            return None
            
        # Authentication options
        # Cookie file
        cookie_file = self.cookie_file_var.get().strip()
        if cookie_file:
            cmd.extend(["--cookies", cookie_file])
        
        # Username/Password
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if username and password:
            cmd.extend(["-u", username, "-p", password])
        
        # API Key / Token
        api_key = self.api_key_var.get().strip()
        if api_key:
            # Gallery-dl uses --header for custom headers
            cmd.extend(["--header", f"Authorization: Bearer {api_key}"])
        
        # OAuth token
        oauth_token = self.oauth_token_var.get().strip()
        if oauth_token:
            # Store in environment or use as header depending on site
            cmd.extend(["--header", f"Authorization: Bearer {oauth_token}"])
        
        # Use .netrc
        if self.use_netrc_var.get():
            cmd.append("--netrc")
        
        # Destination
        dest = self.dest_var.get().strip()
        if dest:
            cmd.extend(["-d", dest])
            
        # Filename format
        filename = self.filename_var.get().strip()
        if filename:
            cmd.extend(["-f", filename])
            
        # Boolean options
        if self.simulate_var.get():
            cmd.append("-s")
        if self.quiet_var.get():
            cmd.append("-q")
        if self.verbose_var.get():
            cmd.append("-v")
        if self.get_urls_var.get():
            cmd.append("-g")
        if self.dump_json_var.get():
            cmd.append("-j")
        
        # Advanced options - Phase 2
        # Proxy
        proxy = self.proxy_var.get().strip()
        if proxy:
            cmd.extend(["--proxy", proxy])
        
        # User-Agent
        ua = self.ua_var.get().strip()
        if ua:
            cmd.extend(["--user-agent", ua])
        
        # Retries
        retries = self.retries_var.get().strip()
        if retries and retries != "4":
            cmd.extend(["--retries", retries])
        
        # Timeout
        timeout = self.timeout_var.get().strip()
        if timeout and timeout != "30":
            cmd.extend(["--timeout", timeout])
        
        # IPv4/IPv6
        if self.ipv4_var.get():
            cmd.append("--ipv4")
        if self.ipv6_var.get():
            cmd.append("--ipv6")
        
        # Skip SSL verification
        if self.no_check_cert_var.get():
            cmd.append("--no-check-certificate")
        
        # Sleep
        sleep = self.sleep_var.get().strip()
        if sleep:
            cmd.extend(["--sleep", sleep])
        
        # Rate limit
        rate_limit = self.rate_limit_var.get().strip()
        if rate_limit and rate_limit != "0":
            cmd.extend(["--rate-limit", rate_limit])
        
        # Chunk size
        chunk_size = self.chunk_size_var.get().strip()
        if chunk_size and chunk_size != "256":
            cmd.extend(["--chunk-size", chunk_size])
        
        # Part files
        if not self.part_files_var.get():
            cmd.append("--no-part-files")
        
        # Skip download
        if self.skip_download_var.get():
            cmd.append("--skip-download")
            
        # Add URLs
        cmd.extend(urls)
        
        return cmd
        
    def start_download(self):
        """Start the download process"""
        if self.is_downloading:
            return
            
        cmd = self.build_command()
        if not cmd:
            return
            
        self.is_downloading = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_bar.start()
        self.status_var.set("Downloading...")
        
        # Start download in separate thread
        thread = threading.Thread(target=self.run_download, args=(cmd,), daemon=True)
        thread.start()
        
    def run_download(self, cmd):
        """Run gallery-dl command in subprocess"""
        try:
            self.log_message(f"Running: {' '.join(cmd)}", 'debug')
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            for line in self.process.stdout:
                if line.strip():
                    self.log_queue.put(line)
                    
            self.process.wait()
            
            if self.process.returncode == 0:
                self.log_queue.put(("DONE", "Download completed successfully", 'success'))
            else:
                self.log_queue.put(("DONE", f"Download finished with code {self.process.returncode}", 'warning'))
                
        except Exception as e:
            self.log_queue.put(("DONE", f"Error: {str(e)}", 'error'))
        finally:
            self.log_queue.put(("DONE", None, None))
            
    def stop_download(self):
        """Stop the current download"""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.log_message("Download stopped by user", 'warning')
            
    def update_log(self):
        """Update log display from queue"""
        try:
            while True:
                item = self.log_queue.get_nowait()
                
                if len(item) == 3 and item[0] == "DONE":
                    # Download finished
                    self.is_downloading = False
                    self.start_btn.config(state=tk.NORMAL)
                    self.stop_btn.config(state=tk.DISABLED)
                    self.progress_bar.stop()
                    self.status_var.set("Ready")
                    
                    if item[1]:
                        self.log_message(item[1], item[2])
                else:
                    # Regular log message
                    msg = item if isinstance(item, str) else item[1]
                    tag = 'info' if isinstance(item, str) else item[2]
                    self.log_message(msg, tag)
                    
        except queue.Empty:
            pass
            
        # Schedule next update
        self.root.after(100, self.update_log)
        
    def log_message(self, message, tag='info'):
        """Add message to log display"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def clear_log(self):
        """Clear the log display"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def show_extractor_info(self):
        """Show extractor information"""
        cmd = [sys.executable, "-m", "gallery_dl", "-E"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            # Show in new window
            info_window = tk.Toplevel(self.root)
            info_window.title("Extractor Info")
            info_window.geometry("600x400")
            
            text = tk.Text(info_window, wrap=tk.WORD)
            text.pack(fill=tk.BOTH, expand=True)
            text.insert(tk.END, result.stdout)
            text.config(state=tk.DISABLED)
            
            ttk.Button(info_window, text="Close", 
                      command=info_window.destroy).pack(pady=5)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get extractor info: {str(e)}")
            
    def list_keywords(self):
        """List keywords for URLs"""
        urls = self.url_text.get(1.0, tk.END).strip().split('\n')
        urls = [u.strip() for u in urls if u.strip()]
        
        if not urls:
            messagebox.showwarning("Warning", "Please enter at least one URL")
            return
            
        cmd = [sys.executable, "-m", "gallery_dl", "-K"] + urls
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            # Show in new window
            info_window = tk.Toplevel(self.root)
            info_window.title("Available Keywords")
            info_window.geometry("700x500")
            
            text = tk.Text(info_window, wrap=tk.WORD)
            text.pack(fill=tk.BOTH, expand=True)
            text.insert(tk.END, result.stdout)
            if result.stderr:
                text.insert(tk.END, "\n" + result.stderr)
            text.config(state=tk.DISABLED)
            
            ttk.Button(info_window, text="Close", 
                      command=info_window.destroy).pack(pady=5)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list keywords: {str(e)}")
            
    def open_config(self):
        """Open configuration file"""
        messagebox.showinfo("Info", "Configuration management will be added in Phase 8")
        
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About gallery-dl GUI",
            "gallery-dl GUI\n\n"
            "A graphical interface for gallery-dl\n"
            "Version 1.0 (Phase 3)\n\n"
            "gallery-dl version: 1.32.6\n\n"
            "This is a multi-phase project.\n"
            "Current phase: Authentication & Input Methods\n\n"
            "Features in this phase:\n"
            "- Cookie file authentication\n"
            "- Username/Password login\n"
            "- OAuth/Token authentication\n"
            "- .netrc support\n"
            "- Browser cookie extraction\n"
            "- File-based URL input\n"
            "- Search query input\n"
            "- User/Gallery ID input"
        )
        
    def open_docs(self):
        """Open documentation in browser"""
        import webbrowser
        webbrowser.open("https://gdl-org.github.io/docs/")
        
    def on_close(self):
        """Handle window close event"""
        if self.is_downloading:
            if messagebox.askyesno("Confirm", "Download in progress. Stop and exit?"):
                self.stop_download()
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    root = tk.Tk()
    app = GalleryDLGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
