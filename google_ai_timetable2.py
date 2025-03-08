import streamlit as st
import google.generativeai as genai
from datetime import datetime

# Streamlit UI for API key input
st.sidebar.header("API Key Configuration")
google_api_key = st.sidebar.text_input("Enter your Google API Key", type="password")

if not google_api_key:
    st.error("Please enter your Google API key to proceed.")
    st.stop()

# Configure the Google Generative AI with the provided API key
try:
    genai.configure(api_key=google_api_key)
except Exception as e:
    st.error(f"Error configuring API key: {str(e)}")
    st.stop()

# Function to list available models
def list_available_models():
    try:
        models = genai.list_models()
        st.write("Available Models:")
        for model in models:
            st.write(f"- {model.name}: {model.description}")
    except Exception as e:
        st.error(f"Error listing models: {str(e)}")

# Call the function to list models
list_available_models()

# Initialize the Google Generative AI model
try:
    model = genai.GenerativeModel('gemini-1.5-flash-latest')  # Use a valid model name
except Exception as e:
    st.error(f"Error initializing model: {str(e)}")
    st.warning("Falling back to a default model.")
    try:
        model = genai.GenerativeModel('gemini-1.0-pro')  # Fallback to another valid model
    except Exception as e:
        st.error(f"Failed to initialize fallback model: {str(e)}")
        st.stop()

# Function to generate a timetable using Google's Generative AI
def generate_timetable_with_google_ai(tasks, available_time, start_time, breaks, syllabus_info, exam_name):
    prompt = f"""
    You are an expert time management assistant helping a student prepare for the {exam_name}. 
    Create a detailed timetable based on the following details:
    - Tasks and Priorities: {tasks}
    - Total available time: {available_time} hours
    - Start time: {start_time}
    - Break duration: {breaks} minutes
    - Syllabus Information: {syllabus_info}

    Ensure the timetable includes proper breaks, prioritizes high-priority tasks, and allocates sufficient time for each subject/task.
    The timetable should be realistic, structured, and account for study time and task completions.
    Return the timetable in a clear, readable format.
    """
    
    try:
        response = model.generate_content(prompt)
        st.write("Debug - API Response:", response)  # Debug: Print API response
        return response.text
    except Exception as e:
        st.error(f"Error generating timetable: {str(e)}")
        return None

# Function to generate a test based on the subjects and tasks relevant to the exam
def generate_test(exam_name, subjects, tasks):
    prompt = f"""
    You are a teacher preparing a test for a student who is preparing for the {exam_name}. Based on the following subjects and tasks:
    - Subjects: {subjects}
    - Tasks: {tasks}

    Please create a set of 5 multiple-choice questions (with options) and 3 fill-in-the-blank questions.
    Ensure the questions are relevant to the subjects and tasks the student is studying. The test should cover a variety of difficulty levels.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating test: {str(e)}")
        return None

# Streamlit UI for user input and AI interaction
st.title("🚀 AI-Powered Exam Preparation and Timetable Scheduler with Google Generative AI")

# Input fields
st.sidebar.header("Input Your Details")
name = st.sidebar.text_input("Your Name")
available_time = st.sidebar.number_input("Total Available Time (in hours)", min_value=1, max_value=24, value=8)
start_time = st.sidebar.time_input("Start Time", datetime.strptime("09:00", "%H:%M"))
breaks = st.sidebar.number_input("Break Duration (in minutes)", min_value=5, max_value=60, value=10)

# Ask for exam details
exam_name = st.sidebar.text_input("Which exam are you preparing for? (e.g., 'Math Exam', 'Physics Exam', etc.)")

# Store exam name in session state
if 'exam_name' not in st.session_state:
    st.session_state.exam_name = exam_name
else:
    st.session_state.exam_name = exam_name

# Task input with priority and description
st.header("📝 Enter Your Tasks")
task_name = st.text_input("Task Name")
task_duration = st.number_input("Task Duration (in hours)", min_value=0.5, max_value=float(available_time), value=1.0, step=0.5)
task_priority = st.selectbox("Task Priority", options=["High", "Medium", "Low"])
task_description = st.text_area("Task Description", placeholder="Provide a brief description of the task...")

# Dictionary to hold the tasks
if 'task_list' not in st.session_state:
    st.session_state.task_list = []

# Allow users to add multiple tasks to the list
if st.button("Add Task"):
    if task_name and task_duration and task_priority:
        st.session_state.task_list.append({
            "name": task_name,
            "duration": task_duration,
            "priority": task_priority,
            "description": task_description
        })
        st.success(f"Task '{task_name}' added!")
    else:
        st.error("Please fill in all the fields.")

# Display tasks
st.header("📋 Your Tasks")
if st.session_state.task_list:
    for task in st.session_state.task_list:
        st.write(f"- {task['name']}: {task['duration']} hours, Priority: {task['priority']}")
        st.write(f"    - Description: {task['description']}")
else:
    st.write("No tasks added yet.")

# Syllabus input for study subjects (Multiple Subjects)
st.header("📚 Syllabus Information")

# Ask user how many subjects they want to enter
num_subjects = st.number_input("How many subjects would you like to enter?", min_value=1, max_value=10, value=1)

# Dictionary to hold subjects
if 'subjects' not in st.session_state:
    st.session_state.subjects = {}

# Add subjects to session state
for i in range(num_subjects):
    subject_name = st.text_input(f"Subject Name {i+1}")
    subject_time = st.number_input(f"Time to Allocate for Subject {i+1} (in hours)", min_value=0.5, max_value=float(available_time), value=1.0, step=0.5)

    if st.button(f"Add Subject {i+1}"):
        if subject_name and subject_time:
            st.session_state.subjects[subject_name] = subject_time
            st.success(f"Subject '{subject_name}' added!")
        else:
            st.error("Please fill in both subject name and time.")

# Display syllabus
st.header("📋 Your Syllabus")
if st.session_state.subjects:
    for subject, time in st.session_state.subjects.items():
        st.write(f"- {subject}: {time} hours")
else:
    st.write("No subjects added yet.")

# Generate timetable
if st.button("Generate Timetable with AI"):
    if st.session_state.task_list and st.session_state.exam_name:
        total_task_time = sum([task['duration'] for task in st.session_state.task_list])
        if total_task_time <= available_time:
            syllabus_info = "\n".join([f"{subject}: {time} hours" for subject, time in st.session_state.subjects.items()])
            
            # Debug: Print inputs
            st.write("Debug - Tasks:", st.session_state.task_list)
            st.write("Debug - Available Time:", available_time)
            st.write("Debug - Start Time:", start_time.strftime("%H:%M"))
            st.write("Debug - Breaks:", breaks)
            st.write("Debug - Syllabus Info:", syllabus_info)
            st.write("Debug - Exam Name:", st.session_state.exam_name)

            st.header("⏰ Your AI-Generated Timetable")
            with st.spinner("Generating your perfect timetable..."):
                timetable = generate_timetable_with_google_ai(st.session_state.task_list, available_time, start_time.strftime("%H:%M"), breaks, syllabus_info, st.session_state.exam_name)
                if timetable:
                    st.write(timetable)
                else:
                    st.error("Failed to generate timetable. Please check the inputs and try again.")
        else:
            st.error("Total task duration exceeds available time. Please adjust your tasks.")
    else:
        st.error("No tasks added or exam name missing. Please add tasks and specify the exam.")

# Use a container for Q&A and Test sections
with st.container():
    # Generate Test for the Student
    st.header("📝 Generate Test for the Student")
    if st.button("Generate Test"):
        st.write("Debug - Generating Test...")  # Debug: Check if the button is clicked
        st.write("Debug - Subjects:", st.session_state.subjects)  # Debug: Check subjects
        st.write("Debug - Exam Name:", st.session_state.exam_name)  # Debug: Check exam name

        if st.session_state.subjects and st.session_state.exam_name:
            with st.spinner("Generating your test..."):
                test = generate_test(st.session_state.exam_name, st.session_state.subjects, st.session_state.task_list)
                if test:
                    st.write(test)
                else:
                    st.error("Failed to generate test. Please check the inputs and try again.")
        else:
            st.error("No subjects added or exam name missing. Please add subjects and specify the exam.")

    # Q&A Section for Assistance
    st.header("❓ Ask AI for Help")
    question = st.text_input("Ask a question or request help with an assignment:")

    if question:
        st.write("Debug - Generating Q&A Response...")  # Debug: Check if the question is processed
        context = f"Tasks: {st.session_state.task_list}, Syllabus: {st.session_state.subjects}, Available Time: {available_time} hours, Exam: {st.session_state.exam_name}"
        with st.spinner("AI is thinking..."):
            try:
                response = model.generate_content(f"You are a helpful assistant. The user is preparing for the {st.session_state.exam_name}. {context} The user has asked the following question: \"{question}\"")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")

# Run the app
if __name__ == "__main__":
    st.write("To run this app, use the following command in your terminal:")
    st.code("streamlit run google_ai_timetable.py")