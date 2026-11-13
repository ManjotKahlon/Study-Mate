
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import date

import database as db


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="StudyMate - Productivity Manager",
    page_icon="📚",
    layout="wide"
)

# Initialize database
db.init_db()


# --------------------------------------------------
# 2. CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.main {
    background-color: #f5f7fb;
}

.stMetric {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
}

h1 {
    color: #243b55;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 3. SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.title("📚 StudyMate")
st.sidebar.caption("Smart Student Productivity Manager")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Task Management",
        "Study Planner",
        "Study Tracker",
        "Progress Analytics"
    ]
)


# --------------------------------------------------
# 4. FETCH DATABASE INFORMATION
# --------------------------------------------------

tasks = db.get_tasks()
sessions = db.get_study_sessions()

total_tasks = len(tasks)

completed_tasks = sum(
    1 for task in tasks if task["status"] == "Completed"
)

pending_tasks = total_tasks - completed_tasks

total_study_time = db.get_total_study_time()

completion_rate = (
    (completed_tasks / total_tasks) * 100
    if total_tasks > 0 else 0
)


# --------------------------------------------------
# 5. DASHBOARD
# --------------------------------------------------

if menu == "Dashboard":

    st.title("📊 StudyMate Dashboard")

    st.write(
        "Welcome to StudyMate! Manage your studies "
        "and monitor your productivity."
    )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Tasks", total_tasks)
    col2.metric("Completed Tasks", completed_tasks)
    col3.metric("Pending Tasks", pending_tasks)

    col4.metric(
        "Study Hours",
        f"{total_study_time / 60:.1f}"
    )

    
    # Deadline Tracking

    st.subheader("📅 Deadline Overview")

    today = date.today()

    overdue_tasks = [
        task for task in tasks
        if task["status"] == "Pending"
        and task["due_date"]
        and date.fromisoformat(task["due_date"]) < today
    ]

    upcoming_tasks = [
        task for task in tasks
        if task["status"] == "Pending"
        and task["due_date"]
        and date.fromisoformat(task["due_date"]) >= today
    ]

    col1, col2 = st.columns(2)

    col1.metric("Overdue Tasks", len(overdue_tasks))
    col2.metric("Upcoming Tasks", len(upcoming_tasks))

    if overdue_tasks:

        st.warning("You have overdue study tasks!")

        for task in overdue_tasks:
            st.write(
                f"🔴 {task['title']} - "
                f"{task['subject']} "
                f"(Due: {task['due_date']})"
            )

    st.divider()


    st.subheader("Overall Task Progress")

    st.progress(int(completion_rate))

    st.write(f"Completion Rate: {completion_rate:.1f}%")

    st.divider()

    st.subheader("Recent Study Tasks")

    if tasks:

        df = pd.DataFrame(tasks)

        st.dataframe(
            df[
                [
                    "subject",
                    "title",
                    "priority",
                    "due_date",
                    "status"
                ]
            ].head(5),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No tasks available. Add your first study task!")

    st.subheader("Recent Study Sessions")

    if sessions:

        st.dataframe(
            pd.DataFrame(sessions).head(5),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No study sessions recorded yet.")



# --------------------------------------------------
# 6. TASK MANAGEMENT
# --------------------------------------------------

elif menu == "Task Management":

    st.title("📝 Task Management")

    # Add New Task
    st.subheader("Add New Study Task")

    with st.form("task_form"):

        subject = st.text_input("Subject")

        title = st.text_input("Task Title")

        description = st.text_area("Description")

        priority = st.selectbox(
            "Priority",
            ["Low", "Medium", "High"]
        )

        due_date = st.date_input(
            "Due Date",
            min_value=date.today()
        )

        submitted = st.form_submit_button("Add Task")

        if submitted:

            if subject.strip() and title.strip():

                db.add_task(
                    subject.strip(),
                    title.strip(),
                    description,
                    priority,
                    str(due_date)
                )

                st.success("Task added successfully!")
                st.rerun()

            else:

                st.error("Please enter both subject and task title.")

    st.divider()

    # Display Existing Tasks
    st.subheader("All Study Tasks")

    tasks = db.get_tasks()

    

    if tasks:
                # Export Tasks to CSV

        task_df = pd.DataFrame(tasks)

        csv_data = task_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download Tasks CSV",
            data=csv_data,
            file_name="studymate_tasks.csv",
            mime="text/csv"
        )

        for task in tasks:

            with st.expander(
                f"{task['title']} - {task['subject']}"
            ):

                st.write("Description:", task["description"])
                st.write("Priority:", task["priority"])
                st.write("Due Date:", task["due_date"])
                st.write("Status:", task["status"])

                col1, col2, col3 = st.columns(3)

                # Complete / Pending
                with col1:

                    if task["status"] == "Pending":

                        if st.button(
                            "Mark Completed",
                            key=f"complete_{task['id']}"
                        ):

                            db.update_task_status(
                                task["id"],
                                "Completed"
                            )

                            st.rerun()

                    else:

                        if st.button(
                            "Mark Pending",
                            key=f"pending_{task['id']}"
                        ):

                            db.update_task_status(
                                task["id"],
                                "Pending"
                            )

                            st.rerun()

                # Edit Task
                with col2:

                    if st.button(
                        "Edit Task",
                        key=f"edit_{task['id']}"
                    ):

                        st.session_state["editing_task"] = task["id"]

                # Delete Task
                with col3:

                    if st.button(
                        "Delete Task",
                        key=f"delete_{task['id']}"
                    ):

                        db.delete_task(task["id"])

                        if st.session_state.get("editing_task") == task["id"]:
                            del st.session_state["editing_task"]

                        st.rerun()

                # Edit Form
                if st.session_state.get("editing_task") == task["id"]:

                    st.divider()
                    st.subheader("Edit Study Task")

                    with st.form(f"edit_form_{task['id']}"):

                        new_subject = st.text_input(
                            "Subject",
                            value=task["subject"],
                            key=f"subject_{task['id']}"
                        )

                        new_title = st.text_input(
                            "Task Title",
                            value=task["title"],
                            key=f"title_{task['id']}"
                        )

                        new_description = st.text_area(
                            "Description",
                            value=task["description"] or "",
                            key=f"description_{task['id']}"
                        )

                        new_priority = st.selectbox(
                            "Priority",
                            ["Low", "Medium", "High"],
                            index=["Low", "Medium", "High"].index(
                                task["priority"]
                            ),
                            key=f"priority_{task['id']}"
                        )

                        new_due_date = st.date_input(
                            "Due Date",
                            value=date.fromisoformat(task["due_date"]),
                            key=f"date_{task['id']}"
                        )

                        save = st.form_submit_button("Save Changes")

                        cancel = st.form_submit_button("Cancel")

                        if save:

                            if new_subject.strip() and new_title.strip():

                                db.edit_task(
                                    task["id"],
                                    new_subject.strip(),
                                    new_title.strip(),
                                    new_description,
                                    new_priority,
                                    str(new_due_date)
                                )

                                del st.session_state["editing_task"]

                                st.success("Task updated successfully!")
                                st.rerun()

                            else:

                                st.error("Subject and title are required.")

                        if cancel:

                            del st.session_state["editing_task"]
                            st.rerun()

    else:

        st.info("No tasks added yet.")



# --------------------------------------------------
# 7. STUDY PLANNER
# --------------------------------------------------

elif menu == "Study Planner":

    st.title("📅 Study Planner")

    tasks = db.get_tasks()

    if tasks:

        df = pd.DataFrame(tasks)

        selected_date = st.date_input(
            "Select Study Date",
            value=date.today()
        )

        selected_tasks = df[
            df["due_date"] == str(selected_date)
        ]

        st.subheader(
            f"Tasks scheduled for {selected_date}"
        )

        if not selected_tasks.empty:

            for _, task in selected_tasks.iterrows():

                st.write(
                    f"**{task['title']}** - "
                    f"{task['subject']} "
                    f"({task['priority']})"
                )

                st.caption(
                    f"Status: {task['status']}"
                )

        else:

            st.info("No tasks scheduled for this date.")

    else:

        st.info("Add tasks first to view your study planner.")



# --------------------------------------------------
# 8. STUDY TIME TRACKER
# --------------------------------------------------

elif menu == "Study Tracker":

    st.title("⏱️ Study Time Tracker")

    st.write("Track your study hours and monitor your daily effort.")

    # Create session state variables
    if "timer_start" not in st.session_state:
        st.session_state.timer_start = None

    if "timer_subject" not in st.session_state:
        st.session_state.timer_subject = ""

    # Two tabs
    tab1, tab2 = st.tabs([
        "Live Study Timer",
        "Manual Entry"
    ])

    # --------------------------------------------------
    # LIVE STUDY TIMER
    # --------------------------------------------------

    with tab1:

        st.subheader("Start Your Study Session")

        subject = st.text_input(
            "Select Subject",
            key="timer_subject_input",
            placeholder="Example: Python"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "▶ Start Studying",
                disabled=st.session_state.timer_start is not None,
                use_container_width=True
            ):

                if subject.strip():

                    st.session_state.timer_subject = subject.strip()
                    st.session_state.timer_start = time.time()

                    st.rerun()

                else:

                    st.warning("Please enter a subject first.")

        with col2:

            if st.button(
                "⏹ Stop & Save",
                disabled=st.session_state.timer_start is None,
                use_container_width=True
            ):

                elapsed = int(
                    time.time() - st.session_state.timer_start
                )

                # Convert seconds into minutes
                duration = max(1, (elapsed + 59) // 60)

                db.add_study_session(
                    st.session_state.timer_subject,
                    duration,
                    str(date.today()),
                    "Recorded using Live Study Timer"
                )

                st.session_state.timer_start = None
                st.session_state.timer_subject = ""

                st.success("Study session saved successfully!")

                st.rerun()

        st.divider()

        # Automatically refresh timer every second
        @st.fragment(run_every="1s")
        def display_timer():

            if st.session_state.timer_start is not None:

                elapsed = int(
                    time.time() - st.session_state.timer_start
                )

                hours = elapsed // 3600
                minutes = (elapsed % 3600) // 60
                seconds = elapsed % 60

                st.subheader(
                    f"📖 Studying: {st.session_state.timer_subject}"
                )

                st.metric(
                    "Time Elapsed",
                    f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                )

                st.info("Your study session is currently running.")

            else:

                st.metric("Time Elapsed", "00:00:00")

                st.info("Start a study session when you are ready.")

        display_timer()

    # --------------------------------------------------
    # MANUAL STUDY ENTRY
    # --------------------------------------------------

    with tab2:

        st.subheader("Record Study Time Manually")

        with st.form("study_form"):

            manual_subject = st.text_input("Subject Name")

            duration = st.number_input(
                "Study Duration (Minutes)",
                min_value=1,
                max_value=1440,
                value=60
            )

            session_date = st.date_input(
                "Study Date",
                value=date.today()
            )

            notes = st.text_area("Study Notes")

            submitted = st.form_submit_button(
                "Save Study Session"
            )

            if submitted:

                if manual_subject.strip():

                    db.add_study_session(
                        manual_subject.strip(),
                        int(duration),
                        str(session_date),
                        notes
                    )

                    st.success("Study session recorded!")

                    st.rerun()

                else:

                    st.error("Please enter a subject name.")

    # --------------------------------------------------
    # STUDY SESSION HISTORY
    # --------------------------------------------------

    st.divider()

    
    st.subheader("📚 Study Session History")

    sessions = db.get_study_sessions()

    if sessions:

        session_df = pd.DataFrame(sessions)

        st.dataframe(
            session_df,
            use_container_width=True,
            hide_index=True
        )

        total_minutes = db.get_total_study_time()

        st.metric(
            "Total Study Time",
            f"{total_minutes // 60}h {total_minutes % 60}m"
        )

        # Export Study Sessions
        csv_data = session_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download Study Sessions CSV",
            data=csv_data,
            file_name="studymate_sessions.csv",
            mime="text/csv"
        )

        # Delete Individual Session
        st.divider()

        st.subheader("Manage Study Sessions")

        for session in sessions:

            with st.expander(
                f"{session['subject']} - "
                f"{session['session_date']} "
                f"({session['duration']} minutes)"
            ):

                st.write("Notes:", session["notes"] or "No notes")

                if st.button(
                    "Delete Session",
                    key=f"delete_session_{session['id']}"
                ):

                    db.delete_study_session(session["id"])

                    st.success("Study session deleted!")

                    st.rerun()

    else:

        st.info("No study sessions recorded yet.")




# --------------------------------------------------
# 9. PROGRESS ANALYTICS
# --------------------------------------------------

elif menu == "Progress Analytics":

    st.title("📈 Progress Analytics")

    st.write(
        "Analyze your study habits, task completion "
        "and overall productivity."
    )

    tasks = db.get_tasks()
    sessions = db.get_study_sessions()

    # --------------------------------------------------
    # PRODUCTIVITY SUMMARY
    # --------------------------------------------------

    st.subheader("Productivity Summary")

    total_tasks = len(tasks)

    completed_tasks = sum(
        1 for task in tasks
        if task["status"] == "Completed"
    )

    pending_tasks = total_tasks - completed_tasks

    total_minutes = db.get_total_study_time()

    total_sessions = len(sessions)

    average_session = (
        total_minutes / total_sessions
        if total_sessions > 0 else 0
    )

    completion_rate = (
        completed_tasks / total_tasks * 100
        if total_tasks > 0 else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Completion Rate", f"{completion_rate:.1f}%")

    col2.metric("Total Study Hours", f"{total_minutes / 60:.1f}")

    col3.metric("Study Sessions", total_sessions)

    col4.metric("Average Session", f"{average_session:.0f} min")

    st.divider()

    # --------------------------------------------------
    # TASK COMPLETION ANALYSIS
    # --------------------------------------------------

    st.subheader("Task Completion Analysis")

    if tasks:

        task_df = pd.DataFrame(tasks)

        status_counts = (
            task_df["status"]
            .value_counts()
            .reindex(["Completed", "Pending"], fill_value=0)
        )

        fig, ax = plt.subplots()

        status_counts.plot(
            kind="pie",
            autopct="%1.1f%%",
            startangle=90,
            ax=ax
        )

        ax.set_ylabel("")
        ax.set_title("Completed vs Pending Tasks")

        st.pyplot(fig)
        plt.close(fig)

        st.subheader("Subject-wise Task Distribution")

        subject_counts = task_df["subject"].value_counts()

        fig, ax = plt.subplots()

        subject_counts.plot(
            kind="bar",
            ax=ax
        )

        ax.set_xlabel("Subject")
        ax.set_ylabel("Number of Tasks")
        ax.set_title("Tasks per Subject")

        plt.xticks(rotation=30, ha="right")
        fig.tight_layout()

        st.pyplot(fig)
        plt.close(fig)

    else:

        st.info("Add study tasks to view task analytics.")

    st.divider()

    # --------------------------------------------------
    # DAILY STUDY TIME ANALYSIS
    # --------------------------------------------------

    st.subheader("Daily Study Activity")

    if sessions:

        session_df = pd.DataFrame(sessions)

        session_df["session_date"] = pd.to_datetime(
            session_df["session_date"]
        )

        daily_data = (
            session_df.groupby("session_date")["duration"]
            .sum()
        )

        last_seven_days = pd.date_range(
            end=pd.Timestamp.today().normalize(),
            periods=7
        )

        daily_data = daily_data.reindex(
            last_seven_days,
            fill_value=0
        )

        fig, ax = plt.subplots()

        daily_data.plot(
            kind="bar",
            ax=ax
        )

        ax.set_xlabel("Date")
        ax.set_ylabel("Study Time (Minutes)")
        ax.set_title("Last 7 Days Study Activity")

        plt.xticks(rotation=30, ha="right")
        fig.tight_layout()

        st.pyplot(fig)
        plt.close(fig)

    else:

        st.info("Record study sessions to view daily activity.")

    st.divider()

    # --------------------------------------------------
    # SUBJECT-WISE STUDY TIME
    # --------------------------------------------------

    st.subheader("Subject-wise Study Time")

    if sessions:

        subject_time = (
            session_df.groupby("subject")["duration"]
            .sum()
            .sort_values(ascending=False)
        )

        fig, ax = plt.subplots()

        subject_time.plot(
            kind="bar",
            ax=ax
        )

        ax.set_xlabel("Subject")
        ax.set_ylabel("Study Time (Minutes)")
        ax.set_title("Total Study Time per Subject")

        plt.xticks(rotation=30, ha="right")
        fig.tight_layout()

        st.pyplot(fig)
        plt.close(fig)

        # Most studied subject
        best_subject = subject_time.idxmax()

        st.success(
            f"Your most studied subject is: {best_subject}"
        )

    else:

        st.info("Record study sessions to view subject-wise analysis.")

    st.divider()

    # --------------------------------------------------
    # STUDY PERFORMANCE REPORT
    # --------------------------------------------------

    st.subheader("Study Performance Report")

    col1, col2 = st.columns(2)

    with col1:

        st.write("**Task Statistics**")

        st.write(f"Total Tasks: {total_tasks}")

        st.write(f"Completed Tasks: {completed_tasks}")

        st.write(f"Pending Tasks: {pending_tasks}")

        st.write(f"Completion Rate: {completion_rate:.1f}%")

    with col2:

        st.write("**Study Statistics**")

        st.write(f"Total Sessions: {total_sessions}")

        st.write(f"Total Study Minutes: {total_minutes}")

        st.write(f"Total Study Hours: {total_minutes / 60:.2f}")

        st.write(f"Average Session: {average_session:.1f} minutes")



# --------------------------------------------------
# 10. FOOTER
# --------------------------------------------------

st.sidebar.divider()

st.sidebar.caption(
    "StudyMate | Python Productivity Manager"
)

st.sidebar.caption(
    "Built using Python, SQLite, Pandas, "
    "Matplotlib and Streamlit"
)
