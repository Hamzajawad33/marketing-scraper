from flask import Flask, render_template, jsonify, request, Response, send_file, redirect, url_for, flash, session
import threading
import time
import json
import os
import queue
import logging
from datetime import datetime
from scraper.engine import ScraperEngine
from data.exporter import DataExporter
import auth

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'nebula_crest_secret_key_2024')  # Load from env

# Global state
scraper_thread = None
current_engine = None
stop_event = threading.Event()
log_queue = queue.Queue()

# ... (existing code) ...


current_stats = {
    'total': 0,
    'with_website': 0,
    'no_website': 0,
    'with_phone': 0,
    'no_phone': 0,
    'with_social': 0,
    'with_pixels': 0,
    'with_email': 0,
    'status': 'Idle',
    'progress': 0
}

# Configure logging to queue
class QueueHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        log_queue.put(log_entry)

logger = logging.getLogger('NebulaScraper')
logger.setLevel(logging.INFO)
queue_handler = QueueHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
queue_handler.setFormatter(formatter)
logger.addHandler(queue_handler)

def run_scraper(keyword, location, max_results, headless, no_website=False):
    global current_stats, stop_event, current_engine
    
    try:
        current_stats['status'] = 'Initializing...'
        current_stats['progress'] = 5
        logger.info(f"Starting scrape for '{keyword}' in '{location}'")
        
        # Check if stop was requested
        if stop_event.is_set():
            current_stats['status'] = 'Aborted'
            return

        engine = ScraperEngine(headless=headless)
        current_engine = engine
        
        current_stats['status'] = 'Searching...'
        current_stats['progress'] = 10
        if not engine.search(keyword, location):
            logger.error("Search failed")
            current_stats['status'] = 'Error'
            return

        # Check if stop was requested
        if stop_event.is_set():
            current_stats['status'] = 'Aborted'
            engine.close()
            return

        # Phase 1 & 2: Collect & Extract (Smart Mode or Normal Mode)
        if no_website:
            logger.info(f"Smart Filtering Enabled: Searching for {max_results} businesses without websites...")
            current_stats['status'] = 'Smart Filtering...'
            
            def no_website_filter(data):
                # Return True if NO website
                return not data.get('Website') or data.get('Website').strip() == ''
                
            results = engine.scrape_with_filter(
                keyword, 
                location, 
                max_results, 
                filter_func=no_website_filter,
                should_stop=lambda: stop_event.is_set()
            )
            logger.info(f"Smart Filter Complete: Found {len(results)} businesses")
            
        else:
            current_stats['status'] = 'Collecting URLs...'
            current_stats['progress'] = 20
            logger.info("Scrolling to find businesses...")
            
            # Phase 1: Collect
            elements = engine.scroll_and_collect(max_results, should_stop=lambda: stop_event.is_set())
            logger.info(f"Found {len(elements)} businesses to process")
            
            # Check if stop was requested
            if stop_event.is_set():
                current_stats['status'] = 'Aborted'
                engine.close()
                return
            
            current_stats['status'] = 'Extracting Data...'
            current_stats['progress'] = 30
            
            # Phase 2: Extract
            results = engine.extract_details(elements, keyword, location, should_stop=lambda: stop_event.is_set())
        
        # Update final stats
        current_stats['total'] = len(results)
        current_stats['with_website'] = sum(1 for b in results if b.get('Website'))
        current_stats['no_website'] = len(results) - current_stats['with_website']
        current_stats['with_phone'] = sum(1 for b in results if b.get('Phone'))
        current_stats['no_phone'] = len(results) - current_stats['with_phone']
        
        # New v6.0 Stats
        current_stats['with_social'] = sum(1 for b in results if any(b.get(k) for k in ['Social_Facebook', 'Social_Instagram', 'Social_LinkedIn', 'Social_Twitter']))
        current_stats['with_pixels'] = sum(1 for b in results if b.get('Ad_Pixel_FB') == 'Yes' or b.get('Ad_Pixel_Google') == 'Yes')
        current_stats['with_email'] = sum(1 for b in results if b.get('Email') or b.get('Email_Found'))
        
        # Check if stop was requested
        if stop_event.is_set():
            current_stats['status'] = 'Aborted'
            engine.close()
            return

        # Export
        current_stats['status'] = 'Exporting...'
        current_stats['progress'] = 90
        
        exporter = DataExporter()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filter_suffix = "_no_website" if no_website else ""
        filename = f"{keyword}_{location}{filter_suffix}_{timestamp}"
        
        # Save to 'output' directory
        output_dir = os.path.abspath("output")
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, f"{filename}.xlsx")
        exporter.export_to_excel(results, filepath)
        logger.info(f"Exported to: {filepath}")
        
        current_stats['status'] = 'Completed'
        current_stats['progress'] = 100
        logger.info("Scraping finished successfully")
        
    except Exception as e:
        logger.error(f"Scraping error: {str(e)}")
        current_stats['status'] = 'Error'
    finally:
        if 'engine' in locals():
            engine.close()
        current_engine = None

@app.route('/')
def index():
    # Check if license is activated
    if 'license_key' not in session:
        return redirect(url_for('license_page'))
    return render_template('index.html')

@app.route('/license')
def license_page():
    # If already activated, redirect to home
    if 'license_key' in session:
        return redirect(url_for('index'))
    return render_template('license.html')

@app.route('/activate', methods=['POST'])
def activate_license():
    data = request.json
    license_key = data.get('license_key')
    
    if not license_key:
        return jsonify({'success': False, 'error': 'License key is required'})
    
    result = auth.activate_license(license_key)
    
    if result['success']:
        # Store in session
        session['license_key'] = result['license_key']
        session['license_type'] = result['license_type']
        session['features'] = result['features']
        return jsonify({'success': True, 'redirect': '/'})
    else:
        return jsonify({'success': False, 'error': result['error']})

@app.route('/logout')
def logout():
    session.clear()
    flash('License deactivated. Please activate again to use the tool.', 'info')
    return redirect(url_for('license_page'))

@app.route('/api/start', methods=['POST'])
def start_scraping():
    global scraper_thread, stop_event, current_stats
    
    if scraper_thread and scraper_thread.is_alive():
        return jsonify({'error': 'Scraper is already running'}), 400
        
    data = request.json
    keyword = data.get('keyword')
    location = data.get('location')
    max_results = int(data.get('max_results', 10))
    headless = data.get('headless', True)
    no_website = data.get('no_website', False)
    
    # Validate license-based max_results limit
    if 'features' in session:
        license_max = session['features'].get('max_results', 100)
        if license_max != -1 and max_results > license_max:
            return jsonify({
                'error': f'Maximum results exceeded. Your license allows up to {license_max} results.'
            }), 400
    
    # Reset stats
    current_stats = {k: 0 for k in current_stats if k != 'status'}
    current_stats['status'] = 'Starting...'
    
    stop_event.clear()
    scraper_thread = threading.Thread(
        target=run_scraper,
        args=(keyword, location, max_results, headless, no_website)
    )
    scraper_thread.daemon = True
    scraper_thread.start()
    
    return jsonify({'status': 'started'})

@app.route('/api/stop', methods=['POST'])
def stop_scraping():
    global stop_event, current_engine
    stop_event.set()
    
    # Force kill the engine if it exists
    if current_engine:
        try:
            current_engine.close()
        except:
            pass
            
    return jsonify({'status': 'stopping'})

@app.route('/api/stats')
def get_stats():
    return jsonify(current_stats)

@app.route('/api/logs')
def stream_logs():
    def generate():
        while True:
            try:
                log_entry = log_queue.get(timeout=1)
                yield f"data: {log_entry}\n\n"
            except queue.Empty:
                yield f"data: \n\n"
                time.sleep(0.5)
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    # Open browser automatically to license page
    if os.environ.get('FLASK_DEBUG', 'True').lower() == 'true':
        import webbrowser
        webbrowser.open('http://127.0.0.1:5000/license')
    
    app.run(
        debug=os.environ.get('FLASK_DEBUG', 'True').lower() == 'true',
        host='0.0.0.0', 
        port=int(os.environ.get('PORT', 5000)),
        use_reloader=False
    )
