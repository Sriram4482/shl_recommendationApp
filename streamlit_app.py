import streamlit as st
import requests
import pandas as pd

# App configuration
st.set_page_config(
    page_title="SHL Assessment Recommender",
    layout="wide"
)

# Sidebar
st.sidebar.title("Filters")
max_duration = st.sidebar.slider(
    "Maximum Duration (minutes)", 
    min_value=10, 
    max_value=120, 
    value=60
)

# Main content
st.title("SHL Assessment Recommendation System")

input_type = st.radio(
    "Input Type:",
    ("Text", "URL"),
    horizontal=True
)

if input_type == "Text":
    query = st.text_area(
        "Enter job description or requirements:",
        height=150
    )
else:
    query = st.text_input("Enter job description URL:")

if st.button("Get Recommendations"):
    if not query.strip():
        st.error("Please enter some text or URL")
    else:
        with st.spinner("Finding the best assessments..."):
            try:
                payload = {
                    "text": query,
                    "max_duration": max_duration
                } if input_type == "Text" else {
                    "url": query,
                    "max_duration": max_duration
                }
                
                endpoint = "/api/recommend" if input_type == "Text" else "/api/recommend-from-url"
                response = requests.post(
                    f"http://localhost:8000{endpoint}",
                    json=payload
                )
                
                if response.status_code == 200:
                    recommendations = response.json()
                    
                    if not recommendations:
                        st.warning("No assessments found matching your criteria")
                    else:
                        # Display as table
                        df = pd.DataFrame(recommendations)
                        st.dataframe(
                            df[['name', 'test_type', 'duration', 
                            'remote_testing', 'adaptive_irt']],
                            column_config={
                                "name": "Assessment Name",
                                "test_type": "Test Type",
                                "duration": "Duration",
                                "remote_testing": "Remote",
                                "adaptive_irt": "Adaptive"
                            },
                            use_container_width=True
                        )
                        
                        # Display details in expanders
                        for rec in recommendations:
                            with st.expander(f"🔍 {rec['name']}"):
                                st.markdown(f"**URL:** [{rec['url']}]({rec['url']})")
                                st.write(f"**Type:** {rec['test_type']}")
                                st.write(f"**Duration:** {rec['duration']}")
                                st.write(f"**Remote Testing:** {'✅ Yes' if rec['remote_testing'] else '❌ No'}")
                                st.write(f"**Adaptive/IRT:** {'✅ Yes' if rec['adaptive_irt'] else '❌ No'}")
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Add footer
st.markdown("---")
st.markdown("### About")
st.markdown("""
This system recommends SHL assessments based on job descriptions.
The recommendations are generated using semantic similarity between
the input text and assessment descriptions.
""")