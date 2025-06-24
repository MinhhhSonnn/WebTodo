#!/usr/bin/env python3
"""
Script test chức năng gửi email
"""

import sys
import os
sys.path.append('.')

from database import MySQLDatabaseManager
import datetime

def test_email_functionality():
    print("=== TEST EMAIL FUNCTIONALITY ===")
    
    # 1. Test database connection
    print("1. Testing database connection...")
    try:
        db = MySQLDatabaseManager(
            host="localhost",
            user="root",
            password="",
            database="todo_db",
            sender_email=os.getenv("SENDER_EMAIL"),
            sender_password=os.getenv("SENDER_PASSWORD")
        )
        if db.connect():
            print("   ✅ Database connection successful")
        else:
            print("   ❌ Database connection failed")
            return
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return
    
    # 2. Test database structure
    print("2. Checking database structure...")
    try:
        # Check if email columns exist
        db.cursor.execute("SHOW COLUMNS FROM todos")
        columns = [row[0] for row in db.cursor.fetchall()]
        print(f"   Available columns: {columns}")
        
        if 'email' in columns:
            print("   ✅ Email column exists")
        else:
            print("   ❌ Email column missing - run update_database.sql")
            
        if 'email_sent' in columns:
            print("   ✅ Email_sent column exists")
        else:
            print("   ❌ Email_sent column missing - run update_database.sql")
            
    except Exception as e:
        print(f"   ❌ Database structure error: {e}")
    
    # 3. Check todos with email and deadline
    print("3. Checking todos with email and deadline...")
    try:
        query = """
        SELECT id, title, deadline, email, email_sent 
        FROM todos 
        WHERE email IS NOT NULL 
        AND deadline IS NOT NULL
        """
        db.cursor.execute(query)
        todos_with_email = db.cursor.fetchall()
        
        if todos_with_email:
            print(f"   Found {len(todos_with_email)} todos with email:")
            for todo in todos_with_email:
                todo_id, title, deadline, email, email_sent = todo
                print(f"   - ID: {todo_id}, Title: {title}")
                print(f"     Deadline: {deadline}")
                print(f"     Email: {email}")
                print(f"     Email sent: {email_sent}")
                
                # Check if deadline is within 30 minutes
                now = datetime.datetime.now()
                if deadline:
                    time_diff = (deadline - now).total_seconds()
                    if 0 < time_diff <= 1800:  # 30 minutes = 1800 seconds
                        print(f"     🔔 Due within 30 minutes! ({time_diff/60:.1f} minutes left)")
                    elif time_diff <= 0:
                        print(f"     ⏰ Overdue by {abs(time_diff)/60:.1f} minutes")
                    else:
                        print(f"     📅 Due in {time_diff/60:.1f} minutes")
        else:
            print("   ❌ No todos found with both email and deadline")
            
    except Exception as e:
        print(f"   ❌ Query error: {e}")
    
    # 4. Test email sending function
    print("4. Testing email sending...")
    try:
        test_email = "sonhoctap59@gmail.com"  # Your email
        test_title = "Test Email"
        test_description = "This is a test email"
        test_deadline = datetime.datetime.now() + datetime.timedelta(minutes=15)
        
        print(f"   Attempting to send test email to: {test_email}")
        result = db.send_email_notification(test_email, test_title, test_description, test_deadline)
        
        if result:
            print("   ✅ Email sent successfully!")
        else:
            print("   ❌ Email sending failed - check email configuration")
            
    except Exception as e:
        print(f"   ❌ Email sending error: {e}")
    
    # 5. Test notification checker
    print("5. Testing notification checker...")
    try:
        db.check_and_send_notifications()
        print("   ✅ Notification checker ran successfully")
    except Exception as e:
        print(f"   ❌ Notification checker error: {e}")
    
    db.close()
    print("\n=== TEST COMPLETED ===")

if __name__ == "__main__":
    test_email_functionality() 