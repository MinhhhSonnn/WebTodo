import mysql.connector
from datetime import datetime

class MySQLDatabaseManager:
    def __init__(self, host="localhost", user="root", password="", database="todo_db"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
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
            self.cursor.execute("SELECT * FROM todos ORDER BY created_at DESC")
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error getting data: {e}")
            return []
    
    def add_todo(self, title, description=""):
        """Add new todo"""
        try:
            insert_query = "INSERT INTO todos (title, description) VALUES (%s, %s)"
            self.cursor.execute(insert_query, (title, description))
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
    
    def close(self):
        """Close connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
