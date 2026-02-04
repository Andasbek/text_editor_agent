import streamlit as st
import sys
import os

# Ensure app can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.service import run_text_editor_agent

st.set_page_config(page_title="AI Text Editor Agent", layout="wide")

st.title("📝 AI Text Editor Agent")
st.markdown("Iterative self-correcting writing assistant.")

# Sidebar Controls
with st.sidebar:
    st.header("Configuration")
    
    mode = st.radio("Mode", ["generate", "revise"])
    
    max_iterations = st.slider("Max Iterations", min_value=1, max_value=6, value=3)
    
    # Optional parameters (visual only for now as prompt handles them via task description usually,
    # but we can append them to task if we want rigorous usage)
    st.subheader("Style Parameters")
    style = st.selectbox("Style", ["Neutral", "Academic", "Business", "Creative"])
    audience = st.selectbox("Audience", ["General", "Expert", "Student", "Child"])
    length = st.selectbox("Length", ["Medium", "Short", "Long"])
    
    show_trace = st.checkbox("Show Iteration Trace", value=True)

# Main Input
task = st.text_area("Task Description", height=100, placeholder="Describe what to write or how to edit...")
user_text = ""

if mode == "revise":
    user_text = st.text_area("Original Text", height=200, placeholder="Paste text here to revise...")

# Run Button
if st.button("Run Agent", type="primary"):
    if not task:
        st.error("Please enter a task description.")
    elif mode == "revise" and not user_text:
        st.error("Please enter original text for revision.")
    else:
        # Augment task with parameters
        augmented_task = f"{task}\nStyle: {style}\nAudience: {audience}\nLength: {length}"
        
        with st.spinner(f"Agent working... (up to {max_iterations} loops)"):
            try:
                result = run_text_editor_agent(augmented_task, mode, user_text, max_iterations)
                
                # Display Result
                st.subheader("Final Result")
                st.success(f"Completed in {result['iterations']} iterations. Stop reason: {result['stopped_by']}")
                st.text_area("Final Text", value=result['final_text'], height=300)
                
                # Trace
                if show_trace:
                    st.divider()
                    st.subheader(" Process Trace")
                    for i, step in enumerate(result.get("trace", [])):
                        with st.expander(f"Iteration {step.get('iteration', '?')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**Draft Content**")
                                st.code(step.get("draft", ""), language=None)
                            with col2:
                                st.markdown("**Critique**")
                                st.json(step.get("critic", {}))
                                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
