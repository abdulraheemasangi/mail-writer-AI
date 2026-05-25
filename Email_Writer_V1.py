import streamlit as st
import requests
import json
import os

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="AI Email Writer",
    page_icon="✉️",
    layout="centered"
)

st.title("✉️ AI Email Writer")

# =========================================================
# FILE PATH
# =========================================================
PURPOSE_FILE = "purposes.json"

# =========================================================
# DEFAULT PURPOSES
# =========================================================
default_purposes = [
    "Leave Request",
    "Meeting Request",
    "Project Update",
    "Follow Up",
    "Job Application",
    "Resignation",
    "Complaint",
    "Appreciation",
    "Client Proposal"
]

# =========================================================
# CREATE PURPOSE FILE IF NOT EXISTS
# =========================================================
if not os.path.exists(PURPOSE_FILE):

    with open(PURPOSE_FILE, "w") as file:
        json.dump(default_purposes, file)

# =========================================================
# LOAD PURPOSES
# =========================================================
with open(PURPOSE_FILE, "r") as file:
    purpose_list = json.load(file)

# =========================================================
# SESSION STATES
# =========================================================
if "suggested_points" not in st.session_state:
    st.session_state.suggested_points = []

# =========================================================
# ADD NEW PURPOSE
# =========================================================
st.subheader("➕ Add New Email Purpose")

new_purpose = st.text_input("Enter New Purpose")

if st.button("Add Purpose"):

    cleaned_purpose = new_purpose.strip()

    if cleaned_purpose != "":

        if cleaned_purpose not in purpose_list:

            purpose_list.append(cleaned_purpose)

            with open(PURPOSE_FILE, "w") as file:
                json.dump(purpose_list, file)

            st.success(f"'{cleaned_purpose}' added successfully!")

            st.rerun()

        else:
            st.warning("Purpose already exists")

    else:
        st.warning("Please enter a valid purpose")

# =========================================================
# PURPOSE DROPDOWN
# =========================================================
st.subheader("📌 Select Email Purpose")

selected_purpose = st.selectbox(
    "Choose Purpose",
    purpose_list
)

# =========================================================
# GENERATE IMPORTANT POINTS
# =========================================================
if st.button("Generate Important Points"):

    suggestion_prompt = f"""
    Generate 10 short professional important points
    for the following email purpose:

    {selected_purpose}

    Rules:
    - Return only bullet points
    - Keep each point short
    - Professional language only
    """

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": suggestion_prompt,
                "stream": False
            }
        )

        result = response.json()

        if "response" in result:

            raw_points = result["response"]

            # =========================================================
            # CLEAN AI OUTPUT
            # =========================================================
            lines = raw_points.split("\n")

            cleaned_points = []

            for line in lines:

                line = line.strip()

                if line != "":

                    line = line.replace("-", "")
                    line = line.replace("*", "")
                    line = line.replace("•", "")

                    cleaned_points.append(line.strip())

            st.session_state.suggested_points = cleaned_points

        elif "error" in result:

            st.error(result["error"])

        else:

            st.error("Unexpected response from AI")

    except Exception as e:

        st.error(str(e))

# =========================================================
# SELECT IMPORTANT POINTS
# =========================================================
st.subheader("✅ Select Important Points")

selected_points = st.multiselect(
    "Choose relevant points",
    st.session_state.suggested_points
)

# =========================================================
# OTHER INPUTS
# =========================================================
tone = st.selectbox(
    "Select Tone",
    [
        "Professional",
        "Friendly",
        "Formal",
        "Casual"
    ]
)

recipient = st.text_input("Recipient Name")

sender_name = st.text_input("Your Name")

# =========================================================
# DISPLAY SELECTED POINTS
# =========================================================
final_points = "\n".join(
    [f"- {point}" for point in selected_points]
)

st.text_area(
    "Selected Important Points",
    value=final_points,
    height=180
)

# =========================================================
# GENERATE EMAIL
# =========================================================
if st.button("Generate Email"):

    # =====================================================
    # VALIDATION
    # =====================================================
    if len(selected_points) == 0:

        st.warning("Please select at least one important point")

    else:

        prompt = f"""
        Write a complete {tone} email.

        Email Purpose:
        {selected_purpose}

        Recipient:
        {recipient}

        Sender Name:
        {sender_name}

        STRICTLY use ONLY the below selected important points:

        {final_points}

        Instructions:
        - Do not add extra assumptions
        - Keep email professional
        - Generate proper subject line
        - Generate concise email body
        """

        with st.spinner("Generating email..."):

            try:

                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "llama3",
                        "prompt": prompt,
                        "stream": False
                    }
                )

                result = response.json()

                # =====================================================
                # DISPLAY GENERATED EMAIL
                # =====================================================
                if "response" in result:

                    email_content = result["response"]

                    st.subheader("📧 Generated Email")

                    st.text_area(
                        "Generated Output",
                        value=email_content,
                        height=350
                    )

                elif "error" in result:

                    st.error(f"Ollama Error: {result['error']}")

                else:

                    st.error("Unexpected response received from Ollama")

            except Exception as e:

                st.error(f"Error: {str(e)}")