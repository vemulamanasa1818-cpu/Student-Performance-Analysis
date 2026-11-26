import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from database import init_db, add_student, get_students, update_student, delete_student, save_marks, get_marks, get_all_results, get_student_report

st.set_page_config(page_title="Student Performance Analysis", page_icon="🎓", layout="wide")
init_db()

st.title("🎓 Student Performance Analysis System")
st.caption("A simple web application to manage student records and analyse academic performance.")

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Choose a page", [
        "Dashboard", "Student Management", "Marks Management",
        "Performance Analysis", "Graphs", "Student Reports"
    ])
    st.divider()
    st.caption("Python • Streamlit • SQLite")

def grade_for(percentage):
    if percentage >= 90:
        return "A+"
    if percentage >= 80:
        return "A"
    if percentage >= 70:
        return "B"
    if percentage >= 60:
        return "C"
    if percentage >= 50:
        return "D"
    return "F"

students = get_students()

if page == "Dashboard":
    st.subheader("Dashboard")
    results = get_all_results()
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Students", len(students))
    c2.metric("Students with Marks", len(results))
    avg = round(sum(r["percentage"] for r in results) / len(results), 2) if results else 0
    c3.metric("Class Average", f"{avg}%")
    st.markdown("### Recent student records")
    if students:
        st.dataframe(pd.DataFrame(students), use_container_width=True, hide_index=True)
    else:
        st.info("No students added yet. Open Student Management to add your first student.")
    st.markdown("### Quick guide")
    st.write("1. Add student details.  2. Enter subject-wise marks.  3. View analysis, graphs and reports.")

elif page == "Student Management":
    st.subheader("Student Management")
    with st.form("add_student_form", clear_on_submit=True):
        st.markdown("#### Add a student")
        col1, col2 = st.columns(2)
        name = col1.text_input("Student name")
        roll = col2.text_input("Roll number")
        dept = col1.text_input("Department", value="CSE")
        year = col2.selectbox("Year", ["1st Year", "2nd Year", "3rd Year", "4th Year"])
        submitted = st.form_submit_button("Add Student")
        if submitted:
            if not name.strip() or not roll.strip():
                st.error("Please enter both student name and roll number.")
            else:
                try:
                    add_student(name.strip(), roll.strip(), dept.strip(), year)
                    st.success("Student added successfully.")
                    st.rerun()
                except Exception:
                    st.error("That roll number already exists. Please use a unique roll number.")

    st.markdown("#### Existing students")
    students = get_students()
    if students:
        st.dataframe(pd.DataFrame(students), use_container_width=True, hide_index=True)
        choices = {f'{s["roll_number"]} - {s["name"]}': s for s in students}
        selected_label = st.selectbox("Select a student to update or delete", list(choices))
        selected = choices[selected_label]
        with st.expander("Update student details"):
            with st.form("update_student_form"):
                new_name = st.text_input("Name", selected["name"])
                new_dept = st.text_input("Department", selected["department"])
                new_year = st.selectbox("Year", ["1st Year", "2nd Year", "3rd Year", "4th Year"],
                                         index=["1st Year", "2nd Year", "3rd Year", "4th Year"].index(selected["year"]))
                if st.form_submit_button("Save Changes"):
                    update_student(selected["id"], new_name.strip(), new_dept.strip(), new_year)
                    st.success("Student details updated.")
                    st.rerun()
        if st.button("Delete selected student", type="secondary"):
            delete_student(selected["id"])
            st.success("Student and their marks deleted.")
            st.rerun()
    else:
        st.info("No student records available.")

elif page == "Marks Management":
    st.subheader("Marks Management")
    if not students:
        st.info("Add a student first in Student Management.")
    else:
        student_map = {f'{s["roll_number"]} - {s["name"]}': s["id"] for s in students}
        chosen = st.selectbox("Choose student", list(student_map))
        student_id = student_map[chosen]
        st.write("Enter marks out of 100 for each subject.")
        subjects = ["Python", "DBMS", "Mathematics", "Java", "English"]
        existing = {m["subject"]: m["marks"] for m in get_marks(student_id)}
        with st.form("marks_form"):
            values = {}
            cols = st.columns(2)
            for i, subject in enumerate(subjects):
                values[subject] = cols[i % 2].number_input(
                    subject, min_value=0, max_value=100,
                    value=int(existing.get(subject, 0)), step=1
                )
            if st.form_submit_button("Save Marks"):
                save_marks(student_id, values)
                st.success("Marks saved successfully.")
                st.rerun()
        saved = get_marks(student_id)
        if saved:
            st.markdown("#### Saved marks")
            st.dataframe(pd.DataFrame(saved), use_container_width=True, hide_index=True)

elif page == "Performance Analysis":
    st.subheader("Performance Analysis")
    results = get_all_results()
    if results:
        df = pd.DataFrame(results)
        st.dataframe(df[["roll_number", "name", "total", "out_of", "percentage", "grade"]],
                     use_container_width=True, hide_index=True)
        st.download_button("Download analysis as CSV", df.to_csv(index=False).encode("utf-8"),
                           file_name="student_performance.csv", mime="text/csv")
    else:
        st.info("Enter marks for at least one student to see performance analysis.")

elif page == "Graphs":
    st.subheader("Performance Graphs")
    results = get_all_results()
    if results:
        df = pd.DataFrame(results)
        fig, ax = plt.subplots()
        ax.bar(df["name"], df["percentage"])
        ax.set_title("Student-wise Percentage")
        ax.set_ylabel("Percentage")
        ax.set_ylim(0, 100)
        ax.tick_params(axis="x", rotation=35)
        st.pyplot(fig)
        plt.close(fig)

        all_marks = []
        for student in students:
            for mark in get_marks(student["id"]):
                all_marks.append(mark)
        if all_marks:
            mdf = pd.DataFrame(all_marks)
            subject_avg = mdf.groupby("subject")["marks"].mean().sort_values(ascending=False)
            fig2, ax2 = plt.subplots()
            ax2.bar(subject_avg.index, subject_avg.values)
            ax2.set_title("Average Marks by Subject")
            ax2.set_ylabel("Average marks out of 100")
            ax2.set_ylim(0, 100)
            ax2.tick_params(axis="x", rotation=25)
            st.pyplot(fig2)
            plt.close(fig2)
    else:
        st.info("Add students and marks to display graphs.")

elif page == "Student Reports":
    st.subheader("Student Reports")
    if students:
        student_map = {f'{s["roll_number"]} - {s["name"]}': s["id"] for s in students}
        chosen = st.selectbox("Choose a student", list(student_map))
        report = get_student_report(student_map[chosen])
        if report and report["marks"]:
            st.markdown(f'### {report["student"]["name"]}')
            st.write(f'**Roll number:** {report["student"]["roll_number"]}  |  **Department:** {report["student"]["department"]}  |  **Year:** {report["student"]["year"]}')
            marks_df = pd.DataFrame(report["marks"])
            total = int(marks_df["marks"].sum())
            out_of = len(marks_df) * 100
            percentage = round(total / out_of * 100, 2) if out_of else 0
            grade = grade_for(percentage)
            a, b, c = st.columns(3)
            a.metric("Total", f"{total}/{out_of}")
            b.metric("Percentage", f"{percentage}%")
            c.metric("Grade", grade)
            st.dataframe(marks_df, use_container_width=True, hide_index=True)
            st.download_button("Download this report as CSV", marks_df.to_csv(index=False).encode("utf-8"),
                               file_name=f'{report["student"]["roll_number"]}_report.csv', mime="text/csv")
        else:
            st.info("No marks saved for this student yet.")
    else:
        st.info("Add a student first.")
