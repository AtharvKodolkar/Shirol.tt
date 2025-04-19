import streamlit as st
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Teacher Substitution", layout="centered")
st.title("📚 Teacher Substitution Planner")

# --- Day Selection ---
days = ["mon", "tue", "wed", "thu", "fri", "sat"]
day_map = {d: d.capitalize() for d in days}
selected_day = st.selectbox("Select Day", days, format_func=lambda d: day_map[d])

# --- Load CSV File ---
try:
    df = pd.read_csv(f"{selected_day}.csv")
    # Ensure data is clean
    df = df.fillna("")
    teachers = df.to_dict(orient="records")
except FileNotFoundError:
    st.error(f"CSV file for {selected_day.capitalize()} not found.")
    st.stop()
except Exception as e:
    st.error(f"Error loading CSV file: {str(e)}")
    st.stop()

# --- Select Absent Teachers ---
all_teacher_names = [str(t.get("Teacher_Name", "")).strip() for t in teachers]
absent_teacher_names = st.multiselect("Select Absent Teachers", [name for name in all_teacher_names if name])

if st.button("Generate Reassignment Plan") and absent_teacher_names:
    # Filter absent teachers
    absent_teachers = [t for t in teachers if str(t.get("Teacher_Name", "")).strip() in absent_teacher_names]

    # Skip first 3 teachers (seniors)
    excluded_seniors = [str(t.get("Teacher_Name", "")).strip() for t in teachers[:3]]
    available_teachers = [
        t for t in teachers
        if str(t.get("Teacher_Name", "")).strip() not in absent_teacher_names
        and str(t.get("Teacher_Name", "")).strip() not in excluded_seniors
    ]

    # Setup for reassignment
    reassignment_plan = {}
    busy_teachers = {str(t.get("Teacher_Name", "")): set() for t in teachers}
    workload = {str(t.get("Teacher_Name", "")): 0 for t in available_teachers}

    # Reassign subjects
    for absent_teacher in absent_teachers:
        for period in [col for col in df.columns if col.startswith("Period")]:
            subject = str(absent_teacher.get(period, "")).strip()
            if subject:  # Only reassign if there is a subject
                sorted_teachers = sorted(
                    available_teachers,
                    key=lambda t: workload[str(t.get("Teacher_Name", ""))]
                )
                for current_teacher in sorted_teachers:
                    name = str(current_teacher.get("Teacher_Name", ""))
                    current_teacher_period = str(current_teacher.get(period, ""))
                    if not current_teacher_period and period not in busy_teachers[name]:
                        current_teacher[period] = subject
                        busy_teachers[name].add(period)
                        workload[name] += 1
                        reassignment_plan[f"{absent_teacher.get('Teacher_Name', '')} - {period}"] = {
                            "subject": subject,
                            "reassigned_to": name
                        }
                        break

    # --- Output ---
    st.subheader("✅ Reassignment Plan")
    if reassignment_plan:
        for k, v in reassignment_plan.items():
            st.write(f"**{k}**: '{v['subject']}' ➜ {v['reassigned_to']}")
    else:
        st.info("No periods could be reassigned.")

elif absent_teacher_names:
    st.warning("Click the button to generate the plan.")
