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
except FileNotFoundError:
    st.error(f"CSV file for {selected_day.capitalize()} not found.")
    st.stop()

teachers = df.to_dict(orient="records")

# --- Select Absent Teachers ---
all_teacher_names = [t["Teacher_Name"].strip() for t in teachers]
absent_teacher_names = st.multiselect("Select Absent Teachers", all_teacher_names)

if st.button("Generate Reassignment Plan") and absent_teacher_names:
    # Filter absent teachers
    absent_teachers = [t for t in teachers if t["Teacher_Name"].strip() in absent_teacher_names]

    # Skip first 3 teachers (seniors)
    excluded_seniors = [t["Teacher_Name"].strip() for t in teachers[:3]]
    available_teachers = [
        t for t in teachers
        if t["Teacher_Name"].strip() not in absent_teacher_names
        and t["Teacher_Name"].strip() not in excluded_seniors
    ]

    # Setup for reassignment
    reassignment_plan = {}
    busy_teachers = {t["Teacher_Name"]: set() for t in teachers}
    workload = {t["Teacher_Name"]: 0 for t in available_teachers}

   # Reassign subjects
for absent_teacher in absent_teachers:
    for period in [col for col in df.columns if col.startswith("Period")]:
        subject = absent_teacher.get(period, "").strip()  # Safely access and strip empty values
        if subject:  # Only reassign if there is a subject
            sorted_teachers = sorted(
                available_teachers,
                key=lambda t: workload[t["Teacher_Name"]]
            )
            for current_teacher in sorted_teachers:
                name = current_teacher["Teacher_Name"]

                # Safely check if the period is empty and if the teacher is not busy
                current_teacher_period = current_teacher.get(period, "")
                if not current_teacher_period and period not in busy_teachers[name]:
                    current_teacher[period] = subject
                    busy_teachers[name].add(period)
                    workload[name] += 1
                    reassignment_plan[f"{absent_teacher['Teacher_Name']} - {period}"] = {
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
