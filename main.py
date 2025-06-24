import streamlit as st
from database import MySQLDatabaseManager
import datetime
import os

os.environ['STREAMLIT_LOGGER_LEVEL'] = 'ERROR'

st.set_page_config(
    page_title="Todo App",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def init_database():
    db = MySQLDatabaseManager(
        host="localhost",
        user="root",
        password="",
        database="todo_db"
    )
    if db.connect():
        return db
    else:
        return None
    

db = init_database()

st.title("Todo App")
st.write("This is a simple todo app")

st.header("Add a new todo")
with st.form("add_todo_form", clear_on_submit=True):
    title = st.text_input("Title", placeholder="Enter a title")
    description = st.text_area("Description", placeholder="Enter a description")
    date = st.date_input("Deadline date", value=None)
    time = st.time_input("Deadline time", value=None)
    deadline = None
    if date and time:
        
        deadline = datetime.datetime.combine(date, time)
    submitted = st.form_submit_button("Add", use_container_width=True)

    if submitted:
        if title.strip():
            todo_id = db.add_todo(title.strip(), description.strip(), deadline)
            if todo_id:
                st.success("Todo added successfully!")
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
                    new_deadline = None
                    if date:
                        new_deadline = datetime.datetime.combine(date, time)
                    col_save, col_cancel = st.columns(2)
                    save = col_save.form_submit_button("Save")
                    cancel = col_cancel.form_submit_button("Cancel")
                    if save:
                        if new_title.strip():
                            if db.update_todo(todo_id, new_title.strip(), new_description.strip(), new_deadline):
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
                
                if checkbox_state:
                    st.markdown(f"~~**{title}**~~")
                    if description:
                        st.caption(f"~~{description}~~")
                    if deadline:
                        st.caption(f"⏰ Deadline: {deadline.strftime('%Y-%m-%d %H:%M')}")
                else:
                    st.markdown(f"**{title}**")
                    if description:
                        st.caption(description)
                    if deadline:
                        st.caption(f"⏰ Deadline: {deadline.strftime('%Y-%m-%d %H:%M')}")

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