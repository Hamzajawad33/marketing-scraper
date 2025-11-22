import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from scraper import ScraperEngine
from data import export_to_excel
import os
import json
import csv
from datetime import datetime
import pandas as pd


class ModernCard(tk.Canvas):
    """Modern card widget with rounded corners and shadow"""
    
    def __init__(self, parent, width, height, corner_radius=15, **kwargs):
        tk.Canvas.__init__(self, parent, width=width, height=height, 
                          highlightthickness=0, **kwargs)
        self.corner_radius = corner_radius
        
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """Create a rounded rectangle"""
        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)


class ModernButton(tk.Canvas):
    """Modern button with hover effects and rounded corners"""
    
    def __init__(self, parent, text, command, bg_color='#8b5cf6', hover_color='#7c3aed',
                 fg_color='white', width=200, height=50, corner_radius=12):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, bg=parent['bg'])
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color
        self.corner_radius = corner_radius
        self.is_hovered = False
        
        # Create rounded rectangle background
        self.bg_rect = self._create_rounded_rect(
            2, 2, width-2, height-2, corner_radius, fill=bg_color, outline=''
        )
        
        # Create text
        self.text_item = self.create_text(
            width/2, height/2, text=text, fill=fg_color,
            font=('Segoe UI', 11, 'bold')
        )
        
        # Bind events
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)
        self.tag_bind(self.bg_rect, '<Enter>', self._on_enter)
        self.tag_bind(self.bg_rect, '<Leave>', self._on_leave)
        self.tag_bind(self.bg_rect, '<Button-1>', self._on_click)
        self.tag_bind(self.text_item, '<Enter>', self._on_enter)
        self.tag_bind(self.text_item, '<Leave>', self._on_leave)
        self.tag_bind(self.text_item, '<Button-1>', self._on_click)
    
    def _create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_enter(self, event):
        self.itemconfig(self.bg_rect, fill=self.hover_color)
        self.config(cursor='hand2')
        self.is_hovered = True
    
    def _on_leave(self, event):
        self.itemconfig(self.bg_rect, fill=self.bg_color)
        self.config(cursor='')
        self.is_hovered = False
    
    def _on_click(self, event):
        if self.command:
            self.command()


class NebulaScraperPro:
    """Nebula Scraper Pro v4.0 - Premium Marketing Intelligence Tool"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Nebula Scraper Pro v4.0")
        self.root.geometry("1400x950")
        self.root.resizable(True, True)
        self.root.minsize(1200, 800)
        
        # Modern color scheme - Dark Nebula
        self.colors = {
            'bg_primary': '#0f0f23',
            'bg_secondary': '#1a1a2e',
            'bg_tertiary': '#16213e',
            'card_bg': '#1e1e3f',
            'accent_purple': '#8b5cf6',
            'accent_blue': '#3b82f6',
            'accent_pink': '#ec4899',
            'accent_green': '#10b981',
            'accent_yellow': '#f59e0b',
            'accent_red': '#ef4444',
            'text_primary': '#ffffff',
            'text_secondary': '#94a3b8',
            'text_muted': '#64748b',
            'border': '#2d3748',
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444'
        }
        
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Variables
        self.keyword_var = tk.StringVar(value="dentist")
        self.location_var = tk.StringVar(value="boston")
        self.max_results_var = tk.IntVar(value=20)
        self.headless_var = tk.BooleanVar(value=True)
        self.output_dir_var = tk.StringVar(value="output")
        self.scroll_count_var = tk.IntVar(value=3)
        
        # Advanced Marketing Filters
        self.filter_no_website_var = tk.BooleanVar(value=False)
        self.filter_no_phone_var = tk.BooleanVar(value=False)
        self.filter_high_rating_var = tk.BooleanVar(value=False)
        self.min_rating_var = tk.DoubleVar(value=4.0)
        self.export_format_var = tk.StringVar(value="Excel")
        
        # Statistics
        self.stats = {
            'total': 0,
            'with_website': 0,
            'without_website': 0,
            'with_phone': 0,
            'without_phone': 0,
            'high_rated': 0
        }
        
        self.scraper = None
        self.is_running = False
        self.extracted_data = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create modern UI"""
        
        # ===== TOP BAR =====
        top_bar = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=80)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)
        
        # Logo and Title
        title_frame = tk.Frame(top_bar, bg=self.colors['bg_secondary'])
        title_frame.pack(side=tk.LEFT, padx=30, pady=20)
        
        tk.Label(
            title_frame,
            text="🌌 NEBULA SCRAPER PRO",
            font=('Segoe UI', 24, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['accent_purple']
        ).pack(side=tk.LEFT)
        
        tk.Label(
            title_frame,
            text="v4.0",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_muted']
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Status indicator
        status_frame = tk.Frame(top_bar, bg=self.colors['bg_secondary'])
        status_frame.pack(side=tk.RIGHT, padx=30)
        
        self.status_indicator = tk.Canvas(
            status_frame, width=12, height=12,
            bg=self.colors['bg_secondary'], highlightthickness=0
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 8))
        self.status_indicator.create_oval(2, 2, 10, 10, fill=self.colors['success'], outline='')
        
        self.status_text = tk.Label(
            status_frame,
            text="Ready",
            font=('Segoe UI', 11),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary']
        )
        self.status_text.pack(side=tk.LEFT)
        
        # ===== MAIN CONTAINER =====
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # ===== LEFT SIDEBAR =====
        left_sidebar = tk.Frame(main_container, bg=self.colors['bg_secondary'], width=360)
        left_sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        left_sidebar.pack_propagate(False)
        
        # Direct frame - NO SCROLLBAR
        sidebar_content = tk.Frame(left_sidebar, bg=self.colors['bg_secondary'])
        sidebar_content.pack(fill=tk.BOTH, expand=True)
        
        # === SEARCH CONFIGURATION ===
        self._create_section_header(sidebar_content, "🔍 Search")
        
        search_card = tk.Frame(sidebar_content, bg=self.colors['card_bg'])
        search_card.pack(fill=tk.X, padx=12, pady=(0, 8))
        
        self._create_modern_input(search_card, "Keyword", self.keyword_var, 
                                 "e.g., dentist", row=0)
        self._create_modern_input(search_card, "Location", self.location_var,
                                 "e.g., Boston", row=1)
        self._create_modern_spinbox(search_card, "Max Results", self.max_results_var,
                                   1, 100, row=2)
        self._create_modern_spinbox(search_card, "Scroll Count", self.scroll_count_var,
                                   1, 10, row=3)
        
        # === MARKETING FILTERS ===
        self._create_section_header(sidebar_content, "🎯 Filters")
        
        filters_card = tk.Frame(sidebar_content, bg=self.colors['card_bg'])
        filters_card.pack(fill=tk.X, padx=12, pady=(0, 8))
        
        self._create_modern_checkbox(filters_card, "🌐 No Website",
                                     self.filter_no_website_var)
        self._create_modern_checkbox(filters_card, "📞 No Phone",
                                     self.filter_no_phone_var)
        self._create_modern_checkbox(filters_card, "⭐ High Rating",
                                     self.filter_high_rating_var)
        
        # Min rating slider
        rating_frame = tk.Frame(filters_card, bg=self.colors['card_bg'])
        rating_frame.pack(fill=tk.X, padx=12, pady=(2, 8))
        
        tk.Label(
            rating_frame,
            text=f"Min Rating: {self.min_rating_var.get()}",
            font=('Segoe UI', 8),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W)
        
        rating_slider = tk.Scale(
            rating_frame,
            from_=1.0,
            to=5.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.min_rating_var,
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary'],
            highlightthickness=0,
            troughcolor=self.colors['bg_tertiary'],
            activebackground=self.colors['accent_purple'],
            showvalue=0
        )
        rating_slider.pack(fill=tk.X, pady=(2, 0))
        
        # === EXPORT OPTIONS ===
        self._create_section_header(sidebar_content, "💾 Export")
        
        export_card = tk.Frame(sidebar_content, bg=self.colors['card_bg'])
        export_card.pack(fill=tk.X, padx=12, pady=(0, 8))
        
        tk.Label(
            export_card,
            text="Format:",
            font=('Segoe UI', 9, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        ).pack(anchor=tk.W, padx=12, pady=(8, 3))
        
        format_frame = tk.Frame(export_card, bg=self.colors['card_bg'])
        format_frame.pack(fill=tk.X, padx=12, pady=(0, 6))
        
        for fmt in ["Excel", "CSV", "JSON"]:
            tk.Radiobutton(
                format_frame,
                text=fmt,
                variable=self.export_format_var,
                value=fmt,
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary'],
                selectcolor=self.colors['bg_tertiary'],
                activebackground=self.colors['card_bg'],
                activeforeground=self.colors['text_primary'],
                font=('Segoe UI', 8)
            ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Output directory
        tk.Label(
            export_card,
            text="Directory:",
            font=('Segoe UI', 9, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        ).pack(anchor=tk.W, padx=12, pady=(6, 3))
        
        dir_frame = tk.Frame(export_card, bg=self.colors['bg_tertiary'])
        dir_frame.pack(fill=tk.X, padx=12, pady=(0, 8))
        
        tk.Entry(
            dir_frame,
            textvariable=self.output_dir_var,
            font=('Segoe UI', 8),
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            bd=0,
            insertbackground=self.colors['accent_purple']
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=6)
        
        tk.Button(
            dir_frame,
            text="📁",
            command=self._browse_directory,
            bg=self.colors['accent_purple'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            cursor='hand2',
            font=('Segoe UI', 9),
            padx=8
        ).pack(side=tk.RIGHT, padx=(3, 3), pady=3)
        
        # === ADVANCED OPTIONS ===
        self._create_section_header(sidebar_content, "⚙️ Options")
        
        advanced_card = tk.Frame(sidebar_content, bg=self.colors['card_bg'])
        advanced_card.pack(fill=tk.X, padx=12, pady=(0, 8))
        
        self._create_modern_checkbox(advanced_card, "🕶️ Headless", self.headless_var)
        
        # === ACTION BUTTONS ===
        button_frame = tk.Frame(sidebar_content, bg=self.colors['bg_secondary'])
        button_frame.pack(fill=tk.X, padx=12, pady=(8, 12))
        
        self.start_btn = ModernButton(
            button_frame,
            "▶️  START",
            self._start_scraping,
            bg_color=self.colors['success'],
            hover_color='#059669',
            width=336,
            height=50
        )
        self.start_btn.pack(pady=(0, 6))
        
        self.stop_btn = ModernButton(
            button_frame,
            "⏹️  STOP",
            self._stop_scraping,
            bg_color=self.colors['error'],
            hover_color='#dc2626',
            width=336,
            height=40
        )
        self.stop_btn.pack()
        
        # ===== RIGHT PANEL =====
        right_panel = tk.Frame(main_container, bg=self.colors['bg_primary'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # === STATISTICS DASHBOARD ===
        stats_container = tk.Frame(right_panel, bg=self.colors['bg_primary'])
        stats_container.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            stats_container,
            text="📊 Live Statistics",
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary']
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Stats cards
        stats_grid = tk.Frame(stats_container, bg=self.colors['bg_primary'])
        stats_grid.pack(fill=tk.X)
        
        self.stat_cards = {}
        stats_config = [
            ("Total", "total", self.colors['accent_blue']),
            ("With Website", "with_website", self.colors['success']),
            ("No Website", "without_website", self.colors['warning']),
            ("No Phone", "without_phone", self.colors['accent_pink']),
        ]
        
        for i, (label, key, color) in enumerate(stats_config):
            card = self._create_stat_card(stats_grid, label, "0", color)
            card.grid(row=0, column=i, padx=(0, 10) if i < 3 else 0, sticky="ew")
            self.stat_cards[key] = card
            stats_grid.grid_columnconfigure(i, weight=1)
        
        # === PROGRESS ===
        progress_frame = tk.Frame(right_panel, bg=self.colors['bg_secondary'])
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            progress_frame,
            text="⚡ Progress",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary']
        ).pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Nebula.Horizontal.TProgressbar",
                       troughcolor=self.colors['bg_tertiary'],
                       background=self.colors['accent_purple'],
                       bordercolor=self.colors['bg_tertiary'],
                       lightcolor=self.colors['accent_purple'],
                       darkcolor=self.colors['accent_purple'],
                       thickness=8)
        
        self.progress = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            style="Nebula.Horizontal.TProgressbar"
        )
        self.progress.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # === ACTIVITY LOG ===
        log_frame = tk.Frame(right_panel, bg=self.colors['bg_secondary'])
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            log_frame,
            text="📝 Activity Log",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary']
        ).pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=('Consolas', 9),
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            bd=0,
            wrap=tk.WORD,
            insertbackground=self.colors['accent_purple']
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        self.log_text.config(state=tk.DISABLED)
    
    def _create_section_header(self, parent, text):
        """Create a section header"""
        tk.Label(
            parent,
            text=text,
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary']
        ).pack(anchor=tk.W, padx=12, pady=(8, 5))
    
    def _create_modern_input(self, parent, label, variable, placeholder, row):
        """Create modern input field"""
        container = tk.Frame(parent, bg=self.colors['card_bg'])
        container.pack(fill=tk.X, padx=12, pady=4)
        
        tk.Label(
            container,
            text=label,
            font=('Segoe UI', 8, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W, pady=(0, 2))
        
        entry_bg = tk.Frame(container, bg=self.colors['bg_tertiary'])
        entry_bg.pack(fill=tk.X)
        
        tk.Entry(
            entry_bg,
            textvariable=variable,
            font=('Segoe UI', 9),
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            bd=0,
            insertbackground=self.colors['accent_purple']
        ).pack(fill=tk.X, padx=8, pady=6)
        
        tk.Label(
            container,
            text=placeholder,
            font=('Segoe UI', 7),
            bg=self.colors['card_bg'],
            fg=self.colors['text_muted']
        ).pack(anchor=tk.W, pady=(1, 0))
    
    def _create_modern_spinbox(self, parent, label, variable, from_, to, row):
        """Create modern spinbox"""
        container = tk.Frame(parent, bg=self.colors['card_bg'])
        container.pack(fill=tk.X, padx=12, pady=4)
        
        tk.Label(
            container,
            text=label,
            font=('Segoe UI', 8, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W, pady=(0, 2))
        
        tk.Spinbox(
            container,
            from_=from_,
            to=to,
            textvariable=variable,
            font=('Segoe UI', 9),
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            bd=0,
            buttonbackground=self.colors['accent_purple'],
            width=15
        ).pack(anchor=tk.W, pady=(0, 2))
    
    def _create_modern_checkbox(self, parent, text, variable):
        """Create modern checkbox"""
        tk.Checkbutton(
            parent,
            text=text,
            variable=variable,
            font=('Segoe UI', 8),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            selectcolor=self.colors['bg_tertiary'],
            activebackground=self.colors['card_bg'],
            activeforeground=self.colors['text_primary'],
            cursor='hand2',
            wraplength=300
        ).pack(anchor=tk.W, padx=12, pady=3)
    
    def _create_stat_card(self, parent, label, value, color):
        """Create a statistics card"""
        card = tk.Frame(parent, bg=self.colors['card_bg'], height=80)
        card.pack_propagate(False)
        
        # Color accent bar
        tk.Frame(card, bg=color, height=4).pack(fill=tk.X)
        
        # Content
        content = tk.Frame(card, bg=self.colors['card_bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        value_label = tk.Label(
            content,
            text=value,
            font=('Segoe UI', 24, 'bold'),
            bg=self.colors['card_bg'],
            fg=color
        )
        value_label.pack()
        
        tk.Label(
            content,
            text=label,
            font=('Segoe UI', 9),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        ).pack()
        
        # Store reference to value label for updates
        card.value_label = value_label
        return card
    
    def _update_stats(self):
        """Update statistics cards"""
        for key, card in self.stat_cards.items():
            card.value_label.config(text=str(self.stats[key]))
    
    def _browse_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_var.set(directory)
    
    def _log(self, message, level='info'):
        """Add message to log"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        prefix_map = {
            'success': '[SUCCESS]',
            'error': '[ERROR]',
            'warning': '[WARNING]',
            'info': '[INFO]'
        }
        
        prefix = prefix_map.get(level, '[INFO]')
        self.log_text.insert(tk.END, f"[{timestamp}] {prefix} {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _update_status(self, status, color=None):
        """Update status indicator"""
        self.status_text.config(text=status)
        if color:
            self.status_indicator.itemconfig(1, fill=color)
    
    def _apply_filters(self, businesses):
        """Apply marketing filters to extracted data"""
        filtered = []
        
        for business in businesses:
            # Apply filters
            if self.filter_no_website_var.get() and business.get('Website'):
                continue
            
            if self.filter_no_phone_var.get() and business.get('Phone'):
                continue
            
            if self.filter_high_rating_var.get():
                try:
                    rating = float(business.get('Rating', 0))
                    if rating < self.min_rating_var.get():
                        continue
                except:
                    continue
            
            filtered.append(business)
        
        return filtered
    
    def _calculate_stats(self, businesses):
        """Calculate statistics"""
        self.stats['total'] = len(businesses)
        self.stats['with_website'] = sum(1 for b in businesses if b.get('Website'))
        self.stats['without_website'] = self.stats['total'] - self.stats['with_website']
        self.stats['with_phone'] = sum(1 for b in businesses if b.get('Phone'))
        self.stats['without_phone'] = self.stats['total'] - self.stats['with_phone']
        
        try:
            self.stats['high_rated'] = sum(
                1 for b in businesses 
                if b.get('Rating') and float(b.get('Rating', 0)) >= self.min_rating_var.get()
            )
        except:
            self.stats['high_rated'] = 0
        
        self._update_stats()
    
    def _export_data(self, businesses, keyword, location):
        """Export data in selected format"""
        try:
            # Get absolute path for output directory
            raw_output_dir = self.output_dir_var.get().strip()
            if not raw_output_dir:
                raw_output_dir = "output"
                
            output_dir = os.path.abspath(raw_output_dir)
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            self._log(f"Error creating directory '{output_dir}': {e}", 'error')
            # Fallback to user's home directory
            output_dir = os.path.join(os.path.expanduser("~"), "Nebula_Output")
            self._log(f"Falling back to: {output_dir}", 'warning')
            os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Sanitize filename
        safe_keyword = "".join([c for c in keyword if c.isalnum() or c in (' ', '-', '_')]).strip()
        safe_location = "".join([c for c in location if c.isalnum() or c in (' ', '-', '_')]).strip()
        base_filename = f"{safe_keyword}_{safe_location}_{timestamp}"
        
        format_type = self.export_format_var.get()
        
        if format_type == "Excel":
            filepath = os.path.join(output_dir, f"{base_filename}.xlsx")
            df = pd.DataFrame(businesses)
            df.to_excel(filepath, index=False, engine='openpyxl')
            return filepath
        
        elif format_type == "CSV":
            filepath = os.path.join(output_dir, f"{base_filename}.csv")
            df = pd.DataFrame(businesses)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            return filepath
        
        elif format_type == "JSON":
            filepath = os.path.join(output_dir, f"{base_filename}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(businesses, f, indent=2, ensure_ascii=False)
            return filepath
        
        return None
    
    def _start_scraping(self):
        """Start scraping"""
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
        self._update_status("Extracting...", self.colors['warning'])
        
        # Reset stats
        for key in self.stats:
            self.stats[key] = 0
        self._update_stats()
        
        self._log("="*60)
        self._log(f"Starting Nebula Scraper Pro v4.0", 'info')
        self._log(f"Keyword: {keyword}", 'info')
        self._log(f"Location: {location}", 'info')
        self._log(f"Max Results: {self.max_results_var.get()}", 'info')
        
        # Log active filters
        if self.filter_no_website_var.get():
            self._log("Filter: No Website ENABLED", 'warning')
        if self.filter_no_phone_var.get():
            self._log("Filter: No Phone ENABLED", 'warning')
        if self.filter_high_rating_var.get():
            self._log(f"Filter: High Rating (>={self.min_rating_var.get()}) ENABLED", 'warning')
        
        self._log("="*60)
        
        thread = threading.Thread(target=self._scrape_worker, daemon=True)
        thread.start()
    
    def _stop_scraping(self):
        """Stop scraping"""
        if not self.is_running:
            messagebox.showinfo("Not Running", "No extraction is currently running!")
            return
        
        self.is_running = False
        self._log("Stopping scraper...", 'warning')
        self._update_status("Stopped", self.colors['error'])
        
        if self.scraper:
            try:
                self.scraper.close()
            except:
                pass
    
    def _scrape_worker(self):
        """Worker thread"""
        try:
            keyword = self.keyword_var.get().strip()
            location = self.location_var.get().strip()
            max_results = self.max_results_var.get()
            headless = self.headless_var.get()
            scroll_count = self.scroll_count_var.get()
            
            # Initialize
            self._log("Initializing browser...", 'info')
            self.scraper = ScraperEngine(headless=headless)
            
            # Search
            self._log(f"Searching Google Maps...", 'info')
            self.scraper.search(keyword, location)
            
            # Scroll
            self._log(f"Loading results...", 'info')
            self.scraper.scroll_results(scroll_count)
            
            # Get elements
            business_elements = self.scraper.get_business_elements()
            self._log(f"Found {len(business_elements)} businesses", 'success')
            
            # Extract
            business_elements = business_elements[:max_results]
            self._log(f"Extracting details from {len(business_elements)} businesses...", 'info')
            
            businesses = self.scraper.extract_details(business_elements, keyword, location)
            
            if not businesses:
                self._log("No data extracted", 'error')
                self._finish_scraping(success=False)
                return
            
            # Calculate stats before filtering
            self._calculate_stats(businesses)
            self._log(f"Extracted {len(businesses)} businesses", 'success')
            
            # Apply filters
            filtered_businesses = self._apply_filters(businesses)
            self._log(f"After filters: {len(filtered_businesses)} businesses", 'info')
            
            # Export
            self._log(f"Exporting to {self.export_format_var.get()}...", 'info')
            filepath = self._export_data(filtered_businesses, keyword, location)
            
            if filepath:
                self._log(f"Data exported to: {filepath}", 'success')
                self._finish_scraping(success=True, filepath=filepath, count=len(filtered_businesses))
            else:
                self._log("Export failed", 'error')
                self._finish_scraping(success=False)
        
        except Exception as e:
            self._log(f"Error: {str(e)}", 'error')
            self._finish_scraping(success=False)
    
    def _finish_scraping(self, success=True, filepath=None, count=0):
        """Finish scraping"""
        self.is_running = False
        self.progress.stop()
        
        if self.scraper:
            try:
                self.scraper.close()
            except:
                pass
        
        if success:
            self._update_status("Completed", self.colors['success'])
            self._log("="*60, 'success')
            self._log("EXTRACTION COMPLETED SUCCESSFULLY!", 'success')
            self._log("="*60, 'success')
            
            messagebox.showinfo(
                "Success!",
                f"Nebula Scraper Pro completed!\n\n"
                f"Businesses extracted: {count}\n"
                f"File: {filepath}\n\n"
                f"Ready for your next extraction!"
            )
        else:
            self._update_status("Failed", self.colors['error'])
            self._log("="*60, 'error')
            self._log("EXTRACTION FAILED", 'error')
            self._log("="*60, 'error')
            messagebox.showerror("Error", "Extraction failed. Check logs for details.")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = NebulaScraperPro(root)
    root.mainloop()


if __name__ == "__main__":
    main()
