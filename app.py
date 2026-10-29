from datetime import date, time

import streamlit as st

from pawpal_system import FREQUENCIES, PRIORITIES, Owner, Pet, Scheduler, Task, to_hhmm

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")


def md(text: str) -> str:
    """Escape user-typed text so Markdown/LaTeX characters (e.g. "$5", "*") display literally."""
    return "".join("\\" + ch if ch in "\\`*_{}[]()#+-.!|~$<>" else ch for ch in text)


def get_owner() -> Owner:
    """Return the Owner kept in session state, creating one on first run."""
    if "owner" not in st.session_state:
        st.session_state.owner = Owner("Jordan")
    return st.session_state.owner


owner = get_owner()
scheduler = Scheduler(owner)

st.title("🐾 PawPal+")
st.caption("Plan your pets' walks, meals, meds, and appointments — sorted and conflict-checked.")

# --- Sidebar: owner and pets ---------------------------------------------------

with st.sidebar:
    st.header("Owner")
    name = st.text_input("Your name", value=owner.name)
    minutes = st.number_input(
        "Minutes available for pet care per day", min_value=5, max_value=1440, value=owner.available_minutes, step=5
    )
    owner.name, owner.available_minutes = name, int(minutes)

    st.header("Pets")
    for pet in owner.pets:
        st.markdown(f"- **{md(pet.name)}** — {pet.species}, {pet.age} yr · {len(pet.tasks)} task{'' if len(pet.tasks) == 1 else 's'}")
    with st.form("add_pet", clear_on_submit=True):
        pet_name = st.text_input("Pet name")
        species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
        age = st.number_input("Age (years)", min_value=0, max_value=40, value=1)
        if st.form_submit_button("Add pet"):
            if not pet_name.strip():
                st.error("Give your pet a name.")
            else:
                try:
                    owner.add_pet(Pet(pet_name.strip(), species, int(age)))
                    st.rerun()
                except ValueError as err:
                    st.error(str(err))

if not owner.pets:
    st.info("Start by adding a pet in the sidebar.")
    st.stop()

day = st.date_input("Day", value=date.today())

# --- Add a task ------------------------------------------------------------------

with st.expander("➕ Add a task", expanded=not owner.get_all_tasks()):
    with st.form("add_task", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            task_pet = st.selectbox("Pet", [p.name for p in owner.pets])
            description = st.text_input("Task", placeholder="Morning walk")
            task_time = st.time_input("Time", value=time(8, 0), step=300)
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=480, value=20)
            priority = st.selectbox("Priority", PRIORITIES, index=1)
            frequency = st.selectbox("Repeats", FREQUENCIES)
            due = st.date_input("Due date", value=day)
        if st.form_submit_button("Add task"):
            if not description.strip():
                st.error("Describe the task.")
            else:
                owner.get_pet(task_pet).add_task(
                    Task(description.strip(), task_time.strftime("%H:%M"), int(duration), priority, frequency, due)
                )
                st.rerun()

# --- Schedule ------------------------------------------------------------------------

schedule_tab, plan_tab = st.tabs(["📅 Schedule", "🧠 Smart plan"])

with schedule_tab:
    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox("Pet", ["All pets"] + [p.name for p in owner.pets])
    with col2:
        status_filter = st.selectbox("Status", ["All", "To do", "Done"])

    tasks = scheduler.filter_tasks(
        scheduler.tasks_for_day(day),
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"All": None, "To do": False, "Done": True}[status_filter],
    )
    tasks = scheduler.sort_by_time(tasks)

    for warning in scheduler.detect_conflicts(day):
        st.warning(md(warning))

    if not tasks:
        st.info("No tasks match for this day.")
    for task in tasks:
        c_done, c_info, c_delete = st.columns([1, 8, 1])
        with c_done:
            if task.completed:
                st.markdown("✅")
            elif st.button("✔", key=f"done-{task.id}", help="Mark done"):
                upcoming = scheduler.mark_task_complete(task.id)
                if upcoming:
                    st.toast(f"Done! Next '{md(upcoming.description)}' added for {upcoming.due_date:%a %b %d}.")
                st.rerun()
        with c_info:
            text = (
                f"**{task.time}–{to_hhmm(task.end_minutes)}** · {md(task.description)} · "
                f"*{md(task.pet_name)}* · {task.priority} priority"
                + (f" · repeats {task.frequency}" if task.frequency != "once" else "")
            )
            st.markdown(f"~~{text}~~" if task.completed else text)
        with c_delete:
            if st.button("🗑", key=f"del-{task.id}", help="Delete task"):
                owner.get_pet(task.pet_name).remove_task(task.id)
                st.rerun()

with plan_tab:
    plan = scheduler.generate_plan(day)
    st.markdown(
        f"Fits **{len(plan.scheduled)}** of **{len(plan.scheduled) + len(plan.skipped)}** remaining tasks "
        f"into your **{plan.budget_minutes} minutes** ({plan.minutes_used} min used). "
        "Highest priority goes first; ties go to the earlier task."
    )
    st.progress(min(plan.minutes_used / plan.budget_minutes, 1.0))
    if plan.scheduled:
        st.table(
            [
                {
                    "Time": e.task.time,
                    "Pet": e.task.pet_name,
                    "Task": e.task.description,
                    "Min": e.task.duration_minutes,
                    "Why": e.reason,
                }
                for e in plan.scheduled
            ]
        )
    else:
        st.success("Nothing left to do on this day. 🎉")
    for entry in plan.skipped:
        st.info(f"Skipped **{md(entry.task.description)}** ({md(entry.task.pet_name)}): {entry.reason}")
    for warning in plan.conflicts:
        st.warning(md(warning))
