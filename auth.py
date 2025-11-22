"""
License Key Authentication Module for Nebula Scraper v6.0
Handles license key validation and session management
"""

import sqlite3
import secrets
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for, flash

# Database configuration
DATABASE = 'nebula_users.db'

# Valid License Keys
# 1 Developer Key - Full access, unlimited usage
DEV_LICENSE_KEY = "DEV1-2024-NBLC-FULL-A7X9"

# 10 Client Keys - Standard access
CLIENT_LICENSE_KEYS = [
    "CLT1-2024-NBLC-STD1-K4M2",
    "CLT2-2024-NBLC-STD2-P9W5",
    "CLT3-2024-NBLC-STD3-R3Y8",
    "CLT4-2024-NBLC-STD4-T6L1",
    "CLT5-2024-NBLC-STD5-V2N7",
    "CLT6-2024-NBLC-STD6-X8Q4",
    "CLT7-2024-NBLC-STD7-Z1H9",
    "CLT8-2024-NBLC-STD8-B5J3",
    "CLT9-2024-NBLC-STD9-D9F6",
    "CL10-2024-NBLC-ST10-G3K8"
]

ALL_VALID_KEYS = [DEV_LICENSE_KEY] + CLIENT_LICENSE_KEYS

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with license_activations table"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS license_activations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_key TEXT NOT NULL,
            license_type TEXT NOT NULL,
            activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def validate_license_key(license_key):
    """
    Validate a license key and return license info
    Returns: dict with success, license_type, and message
    """
    # Remove spaces and convert to uppercase
    license_key = license_key.replace(' ', '').replace('-', '').upper()
    
    # Re-format with dashes
    formatted_key = '-'.join([license_key[i:i+4] for i in range(0, len(license_key), 4)])
    
    if formatted_key == DEV_LICENSE_KEY:
        return {
            'success': True,
            'license_type': 'developer',
            'license_key': formatted_key,
            'features': {
                'max_results': -1,  # Unlimited
                'advanced_features': True,
                'priority_support': True
            }
        }
    elif formatted_key in CLIENT_LICENSE_KEYS:
        return {
            'success': True,
            'license_type': 'client',
            'license_key': formatted_key,
            'features': {
                'max_results': 1000,  # Standard limit
                'advanced_features': True,
                'priority_support': False
            }
        }
    else:
        return {
            'success': False,
            'error': 'Invalid license key. Please check and try again.'
        }

def activate_license(license_key):
    """
    Activate a license key and create session
    """
    result = validate_license_key(license_key)
    
    if not result['success']:
        return result
    
    try:
        conn = get_db_connection()
        
        # Check if already activated
        existing = conn.execute(
            'SELECT * FROM license_activations WHERE license_key = ?',
            (result['license_key'],)
        ).fetchone()
        
        if existing:
            # Update last_used timestamp
            conn.execute(
                'UPDATE license_activations SET last_used = CURRENT_TIMESTAMP WHERE license_key = ?',
                (result['license_key'],)
            )
        else:
            # Insert new activation
            conn.execute(
                'INSERT INTO license_activations (license_key, license_type) VALUES (?, ?)',
                (result['license_key'], result['license_type'])
            )
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'license_key': result['license_key'],
            'license_type': result['license_type'],
            'features': result['features']
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Activation error: {str(e)}'
        }

def get_license_info(license_key):
    """Get license information from database"""
    try:
        conn = get_db_connection()
        license_data = conn.execute(
            'SELECT * FROM license_activations WHERE license_key = ?',
            (license_key,)
        ).fetchone()
        conn.close()
        
        if license_data:
            result = validate_license_key(license_key)
            return {
                'license_key': license_data['license_key'],
                'license_type': license_data['license_type'],
                'activated_at': license_data['activated_at'],
                'last_used': license_data['last_used'],
                'features': result.get('features', {})
            }
        return None
    except Exception as e:
        return None

def license_required(f):
    """Decorator to protect routes that require license activation"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'license_key' not in session:
            flash('Please activate your license to access this page', 'warning')
            return redirect(url_for('license_page'))
        return f(*args, **kwargs)
    return decorated_function

# Initialize database on module import
init_db()
