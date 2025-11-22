import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from scraper import ScraperEngine
from data import export_to_excel
import os
from datetime import datetime


class NebulaScraper:
    """Nebula Scraper - Premium Google Maps Business Data Extractor"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Nebula Scraper v3.0")
        self.root.geometry("1100x800")
        self.root.resizable(True, True)
        
        # Nebula color scheme
        self.colors = {
            'bg_dark': '#0a0e27',
            'bg_medium': '#1a1f3a',
            'bg_light': '#2a2f4a',
            'accent_purple': '#8b5cf6',
            'accent_blue': '#3b82f6',
            'accent_pink': '#ec4899',
            'text_primary': '#ffffff',
            'text_secondary': '#a0aec0',
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444'
        }
        
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Variables
        self.keyword_var = tk.StringVar(value="dentist")
        self.location_var = tk.StringVar(value="boston")
        self.max_results_var = tk.IntVar(value=10)
        self.headless_var = tk.BooleanVar(value=True)
        self.output_dir_var = tk.StringVar(value="output")
        self.scroll_count_var = tk.IntVar(value=3)
        self.stealth_mode_var = tk.BooleanVar(value=True)
        
        self.scraper = None
        self.is_running = False
        
        self._create_widgets()
    
    def _create_gradient_canvas(self, parent, width, height):
        """Create a nebula gradient background"""
        canvas = tk.Canvas(parent, width=width, height=height, 
                          highlightthickness=0, bg=self.colors['bg_dark'])
        
        # Create gradient effect
        for i in range(height):
            ratio = i / height
            # Interpolate between purple and blue
            r = int(138 * (1 - ratio) + 59 * ratio)
            g = int(92 * (1 - ratio) + 130 * ratio)
            b = int(246 * (1 - ratio) + 246 * ratio)
            color = f'#{r:02x}{g:02x}{b:02x}'
            canvas.create_line(0, i, width, i, fill=color, width=1)
        
        return canvas
    
    def _create_widgets(self):
        """Create all GUI widgets"""
        
        # ===== HEADER WITH GRADIENT =====
        header_frame = tk.Frame(self.root, bg=self.colors['bg_dark'], height=120)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Gradient background
        gradient = self._create_gradient_canvas(header_frame, 1100, 120)
        gradient.place(x=0, y=0)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="🌌 NEBULA SCRAPER",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['accent_purple'],
            fg=self.colors['text_primary']
        )
        gradient.create_window(550, 40, window=title_label)
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Premium Google Maps Business Intelligence Tool v3.0",
            font=('Segoe UI', 11),
            bg=self.colors['accent_purple'],
            fg=self.colors['text_secondary']
        )
        gradient.create_window(550, 75, window=subtitle_label)
        
        # ===== MAIN CONTAINER =====
        main_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # ===== LEFT PANEL =====
        left_panel = tk.Frame(main_container, bg=self.colors['bg_medium'], 
                             relief=tk.FLAT, bd=0)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Settings Header
        settings_header = tk.Label(
            left_panel,
            text="⚙️ CONFIGURATION",
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent_purple']
        )
        settings_header.pack(pady=(20, 15), padx=20, anchor=tk.W)
        
        # Settings Container
        settings_container = tk.Frame(left_panel, bg=self.colors['bg_medium'])
        settings_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Input Fields
        self._create_nebula_input(settings_container, "🔍 SEARCH KEYWORD", 
                                 self.keyword_var, "e.g., dentist, restaurant, lawyer", row=0)
        
        self._create_nebula_input(settings_container, "📍 TARGET LOCATION", 
                                 self.location_var, "e.g., Boston, New York, Los Angeles", row=1)
        
        self._create_nebula_spinbox(settings_container, "📊 MAX RESULTS", 
                                   self.max_results_var, 1, 100, row=2)
        
        self._create_nebula_spinbox(settings_container, "🔄 SCROLL ITERATIONS", 
                                   self.scroll_count_var, 1, 10, row=3)
        
        # Output Directory
        output_frame = tk.Frame(settings_container, bg=self.colors['bg_medium'])
        output_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, pady=15)
        
        tk.Label(
            output_frame,
            text="💾 OUTPUT DIRECTORY",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent_blue']
        ).pack(anchor=tk.W, pady=(0, 5))
        
        output_entry_frame = tk.Frame(output_frame, bg=self.colors['bg_light'])
        output_entry_frame.pack(fill=tk.X)
        
        output_entry = tk.Entry(
            output_entry_frame,
            textvariable=self.output_dir_var,
            font=('Segoe UI', 10),
            bg=self.colors['bg_light'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            bd=0,
            insertbackground=self.colors['accent_purple']
        )
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, ipadx=10)
        
        browse_btn = tk.Button(
            output_entry_frame,
            text="📁 BROWSE",
            command=self._browse_directory,
            font=('Segoe UI', 9, 'bold'),
            bg=self.colors['accent_purple'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        )
        browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Advanced Options
        advanced_frame = tk.Frame(settings_container, bg=self.colors['bg_medium'])
        advanced_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=15)
        
        tk.Label(
            advanced_frame,
            text="🔧 ADVANCED OPTIONS",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent_pink']
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Checkboxes
        headless_check = tk.Checkbutton(
            advanced_frame,
            text="🕶️ Headless Mode (Background)",
            variable=self.headless_var,
            font=('Segoe UI', 9),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_secondary'],
            selectcolor=self.colors['bg_light'],
            activebackground=self.colors['bg_medium'],
            activeforeground=self.colors['text_primary'],
            cursor='hand2'
        )
        headless_check.pack(anchor=tk.W, pady=2)
        
        stealth_check = tk.Checkbutton(
            advanced_frame,
            text="🥷 Stealth Mode (Anti-Detection)",
            variable=self.stealth_mode_var,
            font=('Segoe UI', 9),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_secondary'],
            selectcolor=self.colors['bg_light'],
            activebackground=self.colors['bg_medium'],
            activeforeground=self.colors['text_primary'],
            cursor='hand2'
        )
        stealth_check.pack(anchor=tk.W, pady=2)
        
        # Action Buttons
        button_frame = tk.Frame(left_panel, bg=self.colors['bg_medium'])
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.start_button = tk.Button(
            button_frame,
            text="▶️  START EXTRACTION",
            command=self._start_scraping,
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['success'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=15
        )
        self.start_button.pack(fill=tk.X, pady=5)
        
        self.stop_button = tk.Button(
            button_frame,
            text="⏹️  STOP EXTRACTION",
            command=self._stop_scraping,
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['error'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=15
        )
        self.stop_button.pack(fill=tk.X, pady=5)
        
        # ===== RIGHT PANEL =====
        right_panel = tk.Frame(main_container, bg=self.colors['bg_medium'], 
                              relief=tk.FLAT, bd=0)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Stats Header
        stats_header = tk.Label(
            right_panel,
            text="📊 LIVE MONITORING",
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent_blue']
        )
        stats_header.pack(pady=(20, 15), padx=20, anchor=tk.W)
        
        # Status
        self.status_label = tk.Label(
            right_panel,
            text="Status: ⚡ Ready to extract data",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['success'],
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Progress Bar
        progress_frame = tk.Frame(right_panel, bg=self.colors['bg_medium'])
        progress_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Nebula.Horizontal.TProgressbar",
                       troughcolor=self.colors['bg_light'],
                       background=self.colors['accent_purple'],
                       bordercolor=self.colors['bg_light'],
                       lightcolor=self.colors['accent_purple'],
                       darkcolor=self.colors['accent_purple'])
        
        self.progress = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            style="Nebula.Horizontal.TProgressbar"
        )
        self.progress.pack(fill=tk.X)
        
        # Log Area
        log_label = tk.Label(
            right_panel,
            text="📝 ACTIVITY LOG",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent_pink'],
            anchor=tk.W
        )
        log_label.pack(fill=tk.X, padx=20, pady=(0, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            right_panel,
            height=25,
            font=('Consolas', 9),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            bd=0,
            wrap=tk.WORD,
            insertbackground=self.colors['accent_purple']
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        self.log_text.config(state=tk.DISABLED)
        
        # Footer
        footer = tk.Label(
            self.root,
            text="🌌 Nebula Scraper v3.0 | Powered by Advanced AI Technology | © 2025",
            font=('Segoe UI', 9),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_secondary']
        )
        footer.pack(side=tk.BOTTOM, pady=10)
    
    def _create_nebula_input(self, parent, label, variable, placeholder, row):
        """Create a nebula-styled input field"""
        tk.Label(
            parent,
            text=label,
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent_blue']
        ).grid(row=row*2, column=0, sticky=tk.W, pady=(15, 5))
        
        entry = tk.Entry(
            parent,
            textvariable=variable,
            font=('Segoe UI', 10),
            bg=self.colors['bg_light'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            bd=0,
            insertbackground=self.colors['accent_purple']
        )
        entry.grid(row=row*2, column=1, sticky=tk.W+tk.E, pady=(15, 5), ipady=10, ipadx=10)
        
        tk.Label(
            parent,
            text=placeholder,
            font=('Segoe UI', 8),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_secondary']
        ).grid(row=row*2+1, column=1, sticky=tk.W, pady=(0, 5))
        
        parent.grid_columnconfigure(1, weight=1)
    
    def _create_nebula_spinbox(self, parent, label, variable, from_, to, row):
        """Create a nebula-styled spinbox"""
        tk.Label(
            parent,
            text=label,
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent_blue']
        ).grid(row=row*2, column=0, sticky=tk.W, pady=(15, 5))
        
        spinbox = tk.Spinbox(
            parent,
            from_=from_,
            to=to,
            textvariable=variable,
            font=('Segoe UI', 10),
            bg=self.colors['bg_light'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            bd=0,
            buttonbackground=self.colors['accent_purple'],
            width=15
        )
        spinbox.grid(row=row*2, column=1, sticky=tk.W, pady=(15, 5), ipady=8, ipadx=10)
    
    def _browse_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_var.set(directory)
    
    def _log(self, message, level='info'):
        """Add message to log with color coding"""
        self.log_text.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if level == 'success':
            prefix = "✅"
            color = self.colors['success']
        elif level == 'error':
            prefix = "❌"
            color = self.colors['error']
        elif level == 'warning':
            prefix = "⚠️"
            color = self.colors['warning']
        else:
            prefix = "ℹ️"
            color = self.colors['text_primary']
        
        self.log_text.insert(tk.END, f"[{timestamp}] {prefix} {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _update_status(self, status, level='info'):
        """Update status label"""
        if level == 'success':
            emoji = "✅"
            color = self.colors['success']
        elif level == 'error':
            emoji = "❌"
            color = self.colors['error']
        elif level == 'running':
            emoji = "⚡"
            color = self.colors['accent_purple']
        else:
            emoji = "ℹ️"
            color = self.colors['text_secondary']
        
        self.status_label.config(text=f"Status: {emoji} {status}", fg=color)
    
    def _start_scraping(self):
        """Start the scraping process"""
        if self.is_running:
            messagebox.showwarning("Already Running", "Extraction is already in progress!")
            return
        
        keyword = self.keyword_var.get().strip()
        location = self.location_var.get().strip()
        
        if not keyword or not location:
            messagebox.showerror("Input Error", "Please enter both keyword and location!")
            return
        
        self.is_running = True
        self.progress.start()
        self._log("="*60)
        self._log(f"🚀 Initializing Nebula Scraper...", 'info')
        self._log(f"🔍 Keyword: {keyword}", 'info')
        self._log(f"📍 Location: {location}", 'info')
        self._log(f"📊 Max Results: {self.max_results_var.get()}", 'info')
        self._log(f"🥷 Stealth Mode: {'Enabled' if self.stealth_mode_var.get() else 'Disabled'}", 'info')
        self._log("="*60)
        
        self._update_status("Extracting data...", 'running')
        
        # Start scraping in a separate thread
        thread = threading.Thread(target=self._scrape_worker, daemon=True)
        thread.start()
    
    def _stop_scraping(self):
        """Stop the scraping process"""
        if not self.is_running:
            messagebox.showinfo("Not Running", "No extraction process is currently running!")
            return
        
        self.is_running = False
        self._log("⏹️ Stopping scraper...", 'warning')
        self._update_status("Stopped by user", 'warning')
        
        if self.scraper:
            try:
                self.scraper.close()
            except:
                pass
    
    def _scrape_worker(self):
        """Worker thread for scraping"""
        try:
            keyword = self.keyword_var.get().strip()
            location = self.location_var.get().strip()
            max_results = self.max_results_var.get()
            headless = self.headless_var.get()
            scroll_count = self.scroll_count_var.get()
            
            # Initialize scraper
            self._update_status("Initializing browser...", 'running')
            self._log("🌐 Launching browser engine...", 'info')
            self.scraper = ScraperEngine(headless=headless)
            
            # Perform search
            self._update_status("Searching Google Maps...", 'running')
            self._log(f"🔎 Searching for '{keyword}' in '{location}'...", 'info')
            self.scraper.search(keyword, location)
            
            # Scroll to load more results
            self._update_status("Loading results...", 'running')
            self._log(f"📜 Scrolling to load results (x{scroll_count})...", 'info')
            self.scraper.scroll_results(scroll_count)
            
            # Get business elements
            self._update_status("Finding businesses...", 'running')
            business_elements = self.scraper.get_business_elements()
            total_found = len(business_elements)
            self._log(f"✅ Found {total_found} businesses", 'success')
            
            # Limit to max_results
            business_elements = business_elements[:max_results]
            self._log(f"📊 Processing {len(business_elements)} businesses...", 'info')
            
            # Extract details
            self._update_status("Extracting business details...", 'running')
            businesses = self.scraper.extract_details(
                business_elements,
                keyword,
                location
            )
            
            if not businesses:
                self._log("❌ No data extracted", 'error')
                self._finish_scraping(success=False)
                return
            
            self._log(f"✅ Extracted {len(businesses)} businesses", 'success')
            
            # Export to Excel
            self._update_status("Exporting to Excel...", 'running')
            self._log("💾 Generating Excel report...", 'info')
            output_dir = self.output_dir_var.get()
            filepath = export_to_excel(businesses, keyword, location, output_dir)
            
            if filepath:
                self._log(f"✅ Data exported to: {filepath}", 'success')
                self._log(f"📊 Total businesses: {len(businesses)}", 'success')
                self._finish_scraping(success=True, filepath=filepath)
            else:
                self._log("❌ Export failed", 'error')
                self._finish_scraping(success=False)
                
        except Exception as e:
            self._log(f"❌ Error: {str(e)}", 'error')
            self._finish_scraping(success=False)
    
    def _finish_scraping(self, success=True, filepath=None):
        """Finish scraping and cleanup"""
        self.is_running = False
        self.progress.stop()
        
        if self.scraper:
            try:
                self.scraper.close()
            except:
                pass
        
        if success:
            self._update_status("✅ Completed successfully!", 'success')
            self._log("="*60, 'success')
            self._log("✅ EXTRACTION COMPLETED SUCCESSFULLY!", 'success')
            self._log("="*60, 'success')
            if filepath:
                messagebox.showinfo(
                    "Success!",
                    f"🌌 Nebula Scraper completed successfully!\n\n📊 Data saved to:\n{filepath}\n\n✨ Ready for your next extraction!"
                )
        else:
            self._update_status("❌ Failed", 'error')
            self._log("="*60, 'error')
            self._log("❌ EXTRACTION FAILED", 'error')
            self._log("="*60, 'error')
            messagebox.showerror(
                "Error",
                "Extraction failed. Please check the logs for details."
            )


def main():
    """Main entry point"""
    root = tk.Tk()
    app = NebulaScraper(root)
    root.mainloop()


if __name__ == "__main__":
    main()
