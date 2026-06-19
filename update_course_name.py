#!/usr/bin/env python
# update_course_name.py

import sys
import os

# Add the current directory to the path (optional)
sys.path.insert(0, os.getcwd())

# Import your app and models
# Adjust the import based on your actual app structure
try:
    # If you have a factory function (e.g., create_app)
    from app import create_app
    app = create_app()
except ImportError:
    # If you have a global app instance
    from app import app

from app import db
from app.models.certificate_setting import CertificateSetting


def update_course_name():
    print("🚀 Starting certificate course name update...")
    with app.app_context():
        print("🔍 Checking for certificate settings with course_name='Default'...")
        
        # Find the default row
        settings = CertificateSetting.query.filter_by(course_name='Default').first()
        
        if settings:
            print(f"✅ Found: ID={settings.id}, current course_name='{settings.course_name}'")
            print("🔄 Updating to 'ISO 9001:2015 (Quality Management Systems)'...")
            
            # Perform the update
            settings.course_name = 'ISO 9001:2015 (Quality Management Systems)'
            db.session.commit()
            
            print("✅ Update successful!")
            print(f"   New course_name='{settings.course_name}'")
        else:
            print("❌ No row with course_name='Default' found.")
            print("📋 Listing all existing rows in certificate_settings:")
            all_settings = CertificateSetting.query.all()
            if all_settings:
                for s in all_settings:
                    print(f"   ID={s.id}, course_name='{s.course_name}'")
            else:
                print("   ⚠️ No rows at all in certificate_settings table.")

        print("✅ Done.\n")


if __name__ == "__main__":
    update_course_name()