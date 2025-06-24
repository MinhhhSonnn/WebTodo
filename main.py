import streamlit as st
from database import MySQLDatabaseManager
import datetime
import threading
import time as time_module


st.set_page_config(
    page_title="Todo App",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def init_database():
    try:
        db = MySQLDatabaseManager(
            host=st.secrets.get("DB_HOST", "localhost"),
            user=st.secrets.get("DB_USER", "root"),
            password=st.secrets.get("DB_PASSWORD", ""),
            database=st.secrets.get("DB_NAME", "todo_db"),
            sender_email=st.secrets.get("SENDER_EMAIL"),
            sender_password=st.secrets.get("SENDER_PASSWORD")
        )
        if db.connect():
            return db
        else:
            st.error("Failed to connect to the database. Please check your configuration.")
            return None
    except Exception as e:
        st.error(f"An error occurred during database initialization: {e}")
        return None

def notification_worker():
    """Background worker to check and send email notifications"""
    while True:
        try:
            db_worker = MySQLDatabaseManager(
                host=st.secrets.get("DB_HOST", "localhost"),
                user=st.secrets.get("DB_USER", "root"),
                password=st.secrets.get("DB_PASSWORD", ""),
                database=st.secrets.get("DB_NAME", "todo_db"),
                sender_email=st.secrets.get("SENDER_EMAIL"),
                sender_password=st.secrets.get("SENDER_PASSWORD")
            )
            if db_worker.connect():
                db_worker.check_and_send_notifications()
                db_worker.close()
        except Exception as e:
            print(f"Error in notification worker: {e}")
        
        # Check every 5 minutes
        time_module.sleep(300)

# Start background notification worker
@st.cache_resource
def start_notification_worker():
    worker_thread = threading.Thread(target=notification_worker, daemon=True)
    worker_thread.start()
    return worker_thread
    
    
db = init_database()

# Start email notification worker
if db:
    start_notification_worker()

st.markdown("<h1 style='text-align: center;'>Todo App</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>This is a simple todo app</p>", unsafe_allow_html=True)

st.header("Add a new todo")
with st.form("add_todo_form", clear_on_submit=True):
    title = st.text_input("Title", placeholder="Enter a title")
    description = st.text_area("Description", placeholder="Enter a description")
    date = st.date_input("Deadline date", value=None)
    time = st.time_input("Deadline time", value=None)
    email = st.text_input("Email for notification (optional)", placeholder="your-email@example.com")
    deadline = None
    if date and time:
        
        deadline = datetime.datetime.combine(date, time)
    submitted = st.form_submit_button("Add", use_container_width=True)

    if submitted:
        if title.strip():
            # Validate email if provided
            email_to_use = email.strip() if email.strip() else None
            if email_to_use and "@" not in email_to_use:
                st.error("Please enter a valid email address!")
            else:
                todo_id = db.add_todo(title.strip(), description.strip(), deadline, email_to_use)
                if todo_id:
                    st.success("Todo added successfully!")
                    if email_to_use and deadline:
                        st.info("📧 You will receive an email notification exactly at the deadline!")
                    st.rerun()
                else:
                    st.error("Failed to add todo!")
        else:
            st.error("Please enter a title!")

st.header("Your Todos")
todos = db.get_all_todos()

if not todos:
    st.info("No todos found. Add a new todo to get started!")
else:
    for todo in todos:
        todo_id = todo[0]
        title = todo[1]
        description = todo[2]
        status = todo[3]
        deadline = todo[4]
        email = todo[5] if len(todo) > 5 else None

        col1, col2, col3 = st.columns([0.1, 0.7, 0.2])

        with col1:
            checkbox_state = st.checkbox(
                "",
                value= status == "Completed",
                key=f"checkbox_{todo_id}",
            )
        
        with col2:
            if st.session_state.get(f"editing_{todo_id}", False):
                with st.form(f"edit_form_{todo_id}", clear_on_submit=True):
                    new_title = st.text_input("Edit title", value=title, key=f"edit_title_{todo_id}")
                    new_description = st.text_area("Edit description", value=description, key=f"edit_desc_{todo_id}")
                    date = st.date_input("Edit deadline date", value=deadline.date() if deadline else None, key=f"edit_date_{todo_id}")
                    time = st.time_input("Edit deadline time", value=deadline.time() if deadline else datetime.time(23, 59), key=f"edit_time_{todo_id}")
                    new_email = st.text_input("Edit email", value=email or "", key=f"edit_email_{todo_id}")
                    new_deadline = None
                    if date:
                        new_deadline = datetime.datetime.combine(date, time)
                    col_save, col_cancel = st.columns(2)
                    save = col_save.form_submit_button("Save")
                    cancel = col_cancel.form_submit_button("Cancel")
                    if save:
                        if new_title.strip():
                            email_to_use = new_email.strip() if new_email.strip() else None
                            if email_to_use and "@" not in email_to_use:
                                st.error("Please enter a valid email address!")
                            else:
                                if db.update_todo(todo_id, new_title.strip(), new_description.strip(), new_deadline, email_to_use):
                                    st.success("Update successfully!")
                                    st.session_state[f"editing_{todo_id}"] = False
                                    st.rerun()
                                else:
                                    st.error("Update failed! Check terminal for details.")
                        else:
                            st.error("Title cannot be empty!")
                    if cancel:
                        st.session_state[f"editing_{todo_id}"] = False
                        st.rerun()
            else:
                # Hiển thị thông tin bình thường
                if checkbox_state:
                    st.markdown(f"~~**{title}**~~")
                    if description:
                        st.caption(f"~~{description}~~")
                    if deadline:
                        st.caption(f"⏰ Deadline: {deadline.strftime('%Y-%m-%d %H:%M')}")
                    if email:
                        st.caption(f"📧 Email: {email}")
                else:
                    st.markdown(f"**{title}**")
                    if description:
                        st.caption(description)
                    if deadline:
                        st.caption(f"⏰ Deadline: {deadline.strftime('%Y-%m-%d %H:%M')}")
                    if email:
                        st.caption(f"📧 Email: {email}")

        with col3:
            if not st.session_state.get(f"editing_{todo_id}", False):
                if st.button("✏️ Edit", key=f"edit_{todo_id}"):
                    st.session_state[f"editing_{todo_id}"] = True
                    st.rerun()

        if checkbox_state != (status == "Completed"):
            if checkbox_state:  # Nếu checkbox được tích (hoàn thành)
                st.warning("⚠️ You sure you want to complete this task?")
                if st.button("✅ Confirm", key=f"confirm_{todo_id}"):
                    if db.delete_todo(todo_id):
                        st.success(f"Todo '{title}' completed and removed!")
                        st.rerun()
                    else:
                        st.error("Failed to remove todo!")
                
        
        st.divider()