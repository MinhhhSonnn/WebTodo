#!/usr/bin/env python3
"""
Script để thêm cột email_sent vào database
"""

import mysql.connector

def add_email_sent_column():
    try:
        # Kết nối database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="todo_db"
        )
        cursor = conn.cursor()
        
        print("Connecting to database...")
        
        # Kiểm tra xem cột email_sent đã tồn tại chưa
        cursor.execute("SHOW COLUMNS FROM todos LIKE 'email_sent'")
        result = cursor.fetchone()
        
        if result:
            print("✅ Column 'email_sent' already exists")
        else:
            print("Adding 'email_sent' column...")
            # Thêm cột email_sent
            cursor.execute("ALTER TABLE todos ADD COLUMN email_sent BOOLEAN DEFAULT FALSE")
            conn.commit()
            print("✅ Column 'email_sent' added successfully")
        
        # Hiển thị cấu trúc bảng
        print("\nCurrent table structure:")
        cursor.execute("DESCRIBE todos")
        columns = cursor.fetchall()
        for column in columns:
            print(f"  {column[0]} - {column[1]}")
        
        cursor.close()
        conn.close()
        print("\n✅ Database update completed!")
        
    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_email_sent_column() 