import streamlit as st
from database import MySQLDatabaseManager

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
    submitted = st.form_submit_button("Add", use_container_width=True)

    if submitted:
        if title.strip():
            todo_id = db.add_todo(title.strip(), description.strip())
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

        col1, col2 = st.columns([0.1, 0.9])

        with col1:
            checkbox_state = st.checkbox(
                "",
                value= status == "Completed",
                key=f"checkbox_{todo_id}",
            )
        
        with col2:
            if checkbox_state:  # Nếu checkbox được tích
                st.markdown(f"~~**{title}**~~")
                if description:
                    st.caption(f"~~{description}~~")
            else:
                st.markdown(f"**{title}**")
                if description:
                    st.caption(description)

        if checkbox_state != (status == "Completed"):
            if checkbox_state:  # Nếu checkbox được tích (hoàn thành)
                # Hiển thị hộp thoại xác nhận
                st.warning("⚠️ You sure you want to complete this task?")
                
                if st.button("✅ Confirm", key=f"confirm_{todo_id}"):
                    # Xóa todo khỏi database
                    if db.delete_todo(todo_id):
                        st.success(f"Todo '{title}' completed and removed!")
                        st.rerun()
                    else:
                        st.error("Failed to remove todo!")
                
        
        st.divider()