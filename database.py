import mysql.connector
from datetime import datetime
import streamlit as st
import smtplib
import email.mime.text
import email.mime.multipart
import threading
import time
import os  # New import to access environment variables

class MySQLDatabaseManager:
    def __init__(self, host="localhost", user="root", password="", database="todo_db", sender_email=None, sender_password=None):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

        # Allow sender credentials to be provided directly or via environment variables
        self.sender_email = sender_email or os.getenv("SENDER_EMAIL")
        self.sender_password = sender_password or os.getenv("SENDER_PASSWORD")

        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connect to MySQL database"""
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.conn.cursor()
            return True
            
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
    
    def get_all_todos(self):
        """Get all todos"""
        try:
            self.cursor.execute("SELECT * FROM todos ORDER BY id DESC")
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error getting data: {e}")
            return []
    
    def add_todo(self, title, description="", deadline=None, email=None):
        """Add new todo with deadline and email"""
        try:
            insert_query = "INSERT INTO todos (title, description, deadline, email) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(insert_query, (title, description, deadline, email))
            self.conn.commit()
            return self.cursor.lastrowid
        except mysql.connector.Error as e:
            print(f"Error adding todo: {e}")
            return None
    
    def update_todo_status(self, todo_id, completed):
        """Update todo status"""
        try:
            if completed:
                update_query = "UPDATE todos SET completed = 1, completed_at = CURRENT_TIMESTAMP WHERE id = %s"
            else:
                update_query = "UPDATE todos SET completed = 0, completed_at = NULL WHERE id = %s"
            
            self.cursor.execute(update_query, (todo_id,))
            self.conn.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error updating todo: {e}")
            return False
    
    def delete_todo(self, todo_id):
        """Delete todo"""
        try:
            delete_query = "DELETE FROM todos WHERE id = %s"
            self.cursor.execute(delete_query, (todo_id,))
            self.conn.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error deleting todo: {e}")
            return False
    
    def update_todo(self, todo_id, new_title, new_description, new_deadline, new_email=None):
        """Update title, description, deadline and email of a todo"""
        try:
            update_query = "UPDATE todos SET title = %s, description = %s, deadline = %s, email = %s WHERE id = %s"
            self.cursor.execute(update_query, (new_title, new_description, new_deadline, new_email, todo_id))
            self.conn.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error updating todo: {e}")
            return False
    
    def get_todos_due_soon(self):
        """Get todos that have reached their deadline and haven't been notified"""
        try:
            query = """
            SELECT id, title, description, deadline, email 
            FROM todos 
            WHERE deadline IS NOT NULL 
            AND email IS NOT NULL 
            AND deadline <= NOW()
            AND (email_sent IS NULL OR email_sent = 0)
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error getting due todos: {e}")
            return []
    
    def mark_email_sent(self, todo_id):
        """Mark that email notification has been sent for this todo"""
        try:
            update_query = "UPDATE todos SET email_sent = 1 WHERE id = %s"
            self.cursor.execute(update_query, (todo_id,))
            self.conn.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error marking email sent: {e}")
            return False

    def send_email_notification(self, to_email, title, description, deadline):
        """Send email notification for due todo"""
        if not self.sender_email or not self.sender_password:
            print("Warning: Email sending is not configured. Missing SENDER_EMAIL or SENDER_PASSWORD.")
            return False
        try:
            # Email configuration - Thay đổi theo SMTP server của bạn
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            
            # Tạo email
            msg = email.mime.multipart.MimeMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = f"⏰ Todo Reminder: {title}"
            
            body = f"""
            <html>
            <body>
                <h2>🔔 Todo Reminder</h2>
                <p><strong>Title:</strong> {title}</p>
                <p><strong>Description:</strong> {description or 'No description'}</p>
                <p><strong>Deadline:</strong> {deadline.strftime('%Y-%m-%d %H:%M')}</p>
                <p>Don't forget to complete your task!</p>
                <hr>
                <p><em>This is an automated reminder from your Todo App.</em></p>
            </body>
            </html>
            """
            
            msg.attach(email.mime.text.MimeText(body, 'html'))
            
            # Gửi email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, to_email, text)
            server.quit()
            
            print(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def check_and_send_notifications(self):
        """Check for due todos and send email notifications"""
        due_todos = self.get_todos_due_soon()
        
        for todo in due_todos:
            todo_id, title, description, deadline, email = todo
            
            if self.send_email_notification(email, title, description, deadline):
                self.mark_email_sent(todo_id)
                print(f"Notification sent for todo: {title}")

    def close(self):
        """Close connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
