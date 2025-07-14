#!/usr/bin/env python3
"""
Setup script for Google Sheets integration and company activation
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data.db')

def activate_all_companies():
    """Activate all companies that are currently 'On hold'"""
    
    print("🚀 Activating All Companies...")
    print("=" * 50)
    
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        
        # Update all companies to Active status
        c.execute('UPDATE company SET status = "Active" WHERE status = "On hold"')
        updated_count = c.rowcount
        
        conn.commit()
    
    print(f"✅ Activated {updated_count} companies from 'On hold' to 'Active'")
    print("💡 All companies are now active and visible!")

def check_sheets_integration():
    """Check if Google Sheets integration is properly set up"""
    
    print("\n🔧 Checking Google Sheets Integration...")
    print("=" * 50)
    
    # Check if credentials file exists
    credentials_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
    if os.path.exists(credentials_path):
        print("✅ credentials.json found")
    else:
        print("❌ credentials.json not found")
        print("📝 To set up Google Sheets integration:")
        print("   1. Create a Google Cloud Project")
        print("   2. Enable Google Sheets API")
        print("   3. Create a service account")
        print("   4. Download credentials.json")
        print("   5. Place it in the moslaa_pioneer folder")
    
    # Check if required packages are installed
    try:
        import gspread
        print("✅ gspread package installed")
    except ImportError:
        print("❌ gspread package not installed")
        print("📦 Install with: pip install gspread google-auth")
    
    try:
        from google.oauth2.service_account import Credentials
        print("✅ google-auth package installed")
    except ImportError:
        print("❌ google-auth package not installed")
        print("📦 Install with: pip install google-auth")

def setup_database():
    """Ensure database has all required columns"""
    
    print("\n🗄️  Setting up Database...")
    print("=" * 50)
    
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        
        # Check if required columns exist
        c.execute("PRAGMA table_info(company)")
        columns = [column[1] for column in c.fetchall()]
        
        # Add missing columns if needed
        if 'details' not in columns:
            c.execute('ALTER TABLE company ADD COLUMN details TEXT')
            print("✅ Added 'details' column")
        
        if 'salary' not in columns:
            c.execute('ALTER TABLE company ADD COLUMN salary TEXT')
            print("✅ Added 'salary' column")
        
        if 'location' not in columns:
            c.execute('ALTER TABLE company ADD COLUMN location TEXT')
            print("✅ Added 'location' column")
        
        conn.commit()
    
    print("✅ Database setup complete!")

def main():
    """Main setup function"""
    
    print("🚀 Moslaa Pioneer Setup")
    print("=" * 50)
    
    # Setup database
    setup_database()
    
    # Activate all companies
    activate_all_companies()
    
    # Check sheets integration
    check_sheets_integration()
    
    print("\n🎉 Setup Complete!")
    print("📱 Your app is ready to use!")
    print("🌐 Start with: python app.py")
    print("📊 Visit: http://localhost:5000/companies")

if __name__ == "__main__":
    main() 