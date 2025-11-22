import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from scraper import ScraperEngine
from data import export_to_excel
import os


class ModernButton(tk.Canvas):
    """Custom modern button with hover effects."""
    
    def __init__(self, parent, text, command, bg_color='#3498db', hover_color='#2980b9', 
                 fg_color='white', width=200, height=45):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=parent['bg'])
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color
        self.text = text
        
        self.rect = self.create_rectangle(0, 0, width, height, fill=bg_color, outline='', tags='button')
        self.text_item = self.create_text(width/2, height/2, text=text, fill=fg_color, 
                                         font=('Segoe UI', 11, 'bold'), tags='button')
        
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)
        self.tag_bind('button', '<Enter>', self._on_enter)
        self.tag_bind('button', '<Leave>', self._on_leave)
        self.tag_bind('button', '<Button-1>', self._on_click)
    
    def _on_enter(self, event):
        self.itemconfig(self.rect, fill=self.hover_color)
        self.config(cursor='hand2')
    
    def _on_leave(self, event):
        self.itemconfig(self.rect, fill=self.bg_color)
        self.config(cursor='')
    
    def _on_click(self, event):
        if self.command:
            self.command()


class MarketingScraperGUI:
    """Modern GUI Application for Marketing Scraper."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Marketing Business Scraper Pro")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        self.root.configure(bg='#f5f6fa')
        
        # Variables
        self.keyword_var = tk.StringVar(value="dentist")
        self.location_var = tk.StringVar(value="boston")
        self.max_results_var = tk.IntVar(value=10)
        self.headless_var = tk.BooleanVar(value=True)
        self.output_dir_var = tk.StringVar(value="output")
        self.scroll_count_var = tk.IntVar(value=3)
        
        self.scraper = None
        self.is_running = False
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        
        # ===== HEADER =====
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Title with icon
        title_label = tk.Label(
            header_frame,
            text="🚀 Marketing Business Scraper Pro",
            font=('Segoe UI', 24, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Extract business data from Google Maps with ease",
            font=('Segoe UI', 10),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        subtitle_label.pack(pady=(0, 10))
        
        # ===== MAIN CONTAINER =====
        main_container = tk.Frame(self.root, bg='#f5f6fa')
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # ===== LEFT PANEL (Settings) =====
        left_panel = tk.Frame(main_container, bg='white', relief=tk.FLAT, bd=0)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # Add shadow effect
        left_panel.configure(highlightbackground='#dfe6e9', highlightthickness=1)
        
        # Settings Header
        settings_header = tk.Label(
            left_panel,
            text="⚙️ Search Settings",
            font=('Segoe UI', 14, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        settings_header.pack(pady=(20, 15), padx=20, anchor=tk.W)
        
        # Settings Container
        settings_container = tk.Frame(left_panel, bg='white')
        settings_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Keyword
        self._create_input_field(settings_container, "🔍 Keyword", self.keyword_var, 
                                "e.g., dentist, restaurant, lawyer", row=0)
        
        # Location
        self._create_input_field(settings_container, "📍 Location", self.location_var, 
                                "e.g., Boston, New York, Los Angeles", row=1)
        
        # Max Results
        self._create_spinbox_field(settings_container, "📊 Max Results", self.max_results_var, 
                                  1, 100, row=2)
        
        # Scroll Count
        self._create_spinbox_field(settings_container, "🔄 Scroll Count", self.scroll_count_var, 
                                  1, 10, row=3, tooltip="Number of times to scroll the results list")
        
        # Output Directory
        output_frame = tk.Frame(settings_container, bg='white')
        output_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, pady=15)
        
        tk.Label(
            output_frame,
            text="💾 Output Directory",
            font=('Segoe UI', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        output_entry_frame = tk.Frame(output_frame, bg='white')
        output_entry_frame.pack(fill=tk.X)
        
        output_entry = tk.Entry(
            output_entry_frame,
            textvariable=self.output_dir_var,
            font=('Segoe UI', 10),
            bg='#f8f9fa',
            relief=tk.FLAT,
            bd=0
        )
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, ipadx=10)
        
        browse_btn = tk.Button(
            output_entry_frame,
            text="Browse",
            command=self._browse_directory,
            font=('Segoe UI', 9),
            bg='#95a5a6',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=15
        )
        browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Headless Mode
        headless_frame = tk.Frame(settings_container, bg='white')
        headless_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        headless_check = tk.Checkbutton(
            headless_frame,
            text="🕶️ Headless Mode (Run browser in background)",
            variable=self.headless_var,
            font=('Segoe UI', 10),
            bg='white',
            fg='#2c3e50',
            activebackground='white',
            cursor='hand2'
        )
        headless_check.pack(anchor=tk.W)
        
        # Action Buttons
        button_frame = tk.Frame(left_panel, bg='white')
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.start_button = ModernButton(
            button_frame,
            "▶️  Start Scraping",
            self._start_scraping,
            bg_color='#27ae60',
            hover_color='#229954',
            width=250,
            height=50
        )
        self.start_button.pack(pady=5)
        
        self.stop_button = ModernButton(
            button_frame,
            "⏹️  Stop Scraping",
            self._stop_scraping,
            bg_color='#e74c3c',
            hover_color='#c0392b',
            width=250,
            height=50
        )
        self.stop_button.pack(pady=5)
        
        # ===== RIGHT PANEL (Log & Stats) =====
        right_panel = tk.Frame(main_container, bg='white', relief=tk.FLAT, bd=0)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        right_panel.configure(highlightbackground='#dfe6e9', highlightthickness=1)
        
        # Stats Header
        stats_header = tk.Label(
            right_panel,
            text="📈 Progress & Logs",
            font=('Segoe UI', 14, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        stats_header.pack(pady=(20, 15), padx=20, anchor=tk.W)
        
        # Status Label
        self.status_label = tk.Label(
            right_panel,
            text="Status: Ready to start",
            font=('Segoe UI', 11),
            bg='white',
            fg='#7f8c8d',
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Progress Bar
        progress_frame = tk.Frame(right_panel, bg='white')
        progress_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        self.progress = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            length=300
        )
        self.progress.pack(fill=tk.X)
        
        # Log Area
        log_label = tk.Label(
            right_panel,
            text="📝 Activity Log",
            font=('Segoe UI', 10, 'bold'),
            bg='white',
            fg='#2c3e50',
            anchor=tk.W
        )
        log_label.pack(fill=tk.X, padx=20, pady=(0, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            right_panel,
            height=20,
            font=('Consolas', 9),
            bg='#2c3e50',
            fg='#ecf0f1',
            relief=tk.FLAT,
            bd=0,
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        self.log_text.config(state=tk.DISABLED)
        
        # Footer
        footer = tk.Label(
            self.root,
            text="Made with ❤️ for Marketing Professionals | v2.0",
            font=('Segoe UI', 9),
            bg='#f5f6fa',
            fg='#95a5a6'
        )
        footer.pack(side=tk.BOTTOM, pady=10)
    
    def _create_input_field(self, parent, label, variable, placeholder, row):
        """Create a modern input field."""
        tk.Label(
            parent,
            text=label,
            font=('Segoe UI', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).grid(row=row, column=0, sticky=tk.W, pady=(15, 5))
        
        entry = tk.Entry(
            parent,
            textvariable=variable,
            font=('Segoe UI', 10),
            bg='#f8f9fa',
            relief=tk.FLAT,
            bd=0
        )
        entry.grid(row=row, column=1, sticky=tk.W+tk.E, pady=(15, 5), ipady=8, ipadx=10)
        
        tk.Label(
            parent,
            text=placeholder,
            font=('Segoe UI', 8),
            bg='white',
            fg='#95a5a6'
        ).grid(row=row+1, column=1, sticky=tk.W, pady=(0, 5))
        
        parent.grid_columnconfigure(1, weight=1)
    
    def _create_spinbox_field(self, parent, label, variable, from_, to, row, tooltip=None):
        """Create a modern spinbox field."""
        tk.Label(
            parent,
            text=label,
            font=('Segoe UI', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).grid(row=row, column=0, sticky=tk.W, pady=(15, 5))
        
        spinbox = tk.Spinbox(
            parent,
            from_=from_,
            to=to,
            textvariable=variable,
            font=('Segoe UI', 10),
            bg='#f8f9fa',
            relief=tk.FLAT,
            bd=0,
            width=15
        )
        spinbox.grid(row=row, column=1, sticky=tk.W, pady=(15, 5), ipady=5, ipadx=10)
        
        if tooltip:
            tk.Label(
                parent,
                text=tooltip,
                font=('Segoe UI', 8),
                bg='white',
                fg='#95a5a6'
            ).grid(row=row+1, column=1, sticky=tk.W, pady=(0, 5))
    
    def _browse_directory(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_var.set(directory)
    
    def _log(self, message):
        """Add message to log."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _update_status(self, status):
        """Update status label."""
        self.status_label.config(text=f"Status: {status}")
    
    def _start_scraping(self):
        """Start the scraping process."""
        if self.is_running:
            messagebox.showwarning("Already Running", "Scraping is already in progress!")
            return
        
        keyword = self.keyword_var.get().strip()
        location = self.location_var.get().strip()
        
        if not keyword or not location:
            messagebox.showerror("Input Error", "Please enter both keyword and location!")
            return
        
        self.is_running = True
        self.progress.start()
        self._log("="*50)
        self._log(f"🚀 Starting scraper...")
        self._log(f"🔍 Keyword: {keyword}")
        self._log(f"📍 Location: {location}")
        self._log(f"📊 Max Results: {self.max_results_var.get()}")
        self._log("="*50)
        
        # Start scraping in a separate thread
        thread = threading.Thread(target=self._scrape_worker, daemon=True)
        thread.start()
    
    def _stop_scraping(self):
        """Stop the scraping process."""
        if not self.is_running:
            messagebox.showinfo("Not Running", "No scraping process is currently running!")
            return
        
        self.is_running = False
        self._log("⏹️ Stopping scraper...")
        self._update_status("Stopped by user")
        
        if self.scraper:
            try:
                self.scraper.close()
            except:
                pass
    
    def _scrape_worker(self):
        """Worker thread for scraping."""
        try:
            keyword = self.keyword_var.get().strip()
            location = self.location_var.get().strip()
            max_results = self.max_results_var.get()
            headless = self.headless_var.get()
            scroll_count = self.scroll_count_var.get()
            
            # Initialize scraper
            self._update_status("Initializing browser...")
            self._log("🌐 Initializing browser...")
            self.scraper = ScraperEngine(headless=headless)
            
            # Perform search
            self._update_status("Searching Google Maps...")
            self._log(f"🔎 Searching for '{keyword}' in '{location}'...")
            self.scraper.search(keyword, location)
            
            # Scroll to load more results
            self._update_status("Loading results...")
            self._log(f"📜 Scrolling to load results (x{scroll_count})...")
            self.scraper.scroll_results(scroll_count)
            
            # Get business elements
            self._update_status("Finding businesses...")
            business_elements = self.scraper.get_business_elements()
            total_found = len(business_elements)
            self._log(f"✅ Found {total_found} businesses")
            
            # Limit to max_results
            business_elements = business_elements[:max_results]
            self._log(f"📊 Processing {len(business_elements)} businesses...")
            
            # Extract details
            self._update_status("Extracting business details...")
            businesses = self.scraper.extract_details(
                business_elements,
                keyword,
                location
            )
            
            if not businesses:
                self._log("❌ No data extracted")
                self._finish_scraping(success=False)
                return
            
            self._log(f"✅ Extracted {len(businesses)} businesses")
            
            # Export to Excel
            self._update_status("Exporting to Excel...")
            self._log("💾 Exporting to Excel...")
            output_dir = self.output_dir_var.get()
            filepath = export_to_excel(businesses, keyword, location, output_dir)
            
            if filepath:
                self._log(f"✅ Data exported to: {filepath}")
                self._log(f"📊 Total businesses: {len(businesses)}")
                self._finish_scraping(success=True, filepath=filepath)
            else:
                self._log("❌ Export failed")
                self._finish_scraping(success=False)
                
        except Exception as e:
            self._log(f"❌ Error: {str(e)}")
            self._finish_scraping(success=False)
    
    def _finish_scraping(self, success=True, filepath=None):
        """Finish scraping and cleanup."""
        self.is_running = False
        self.progress.stop()
        
        if self.scraper:
            try:
                self.scraper.close()
            except:
                pass
        
        if success:
            self._update_status("✅ Completed successfully!")
            self._log("="*50)
            self._log("✅ SCRAPING COMPLETED SUCCESSFULLY!")
            self._log("="*50)
            if filepath:
                messagebox.showinfo(
                    "Success!",
                    f"Scraping completed successfully!\n\nData saved to:\n{filepath}"
                )
        else:
            self._update_status("❌ Failed")
            self._log("="*50)
            self._log("❌ SCRAPING FAILED")
            self._log("="*50)
            messagebox.showerror(
                "Error",
                "Scraping failed. Please check the logs for details."
            )


def main():
    """Main entry point."""
    root = tk.Tk()
    app = MarketingScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
