import streamlit as st
import PyPDF2
import openai
import json
import time


def parse_pdf(pdf_file):
    # Parse the PDF and extract questions and options
    # Save the extracted data as a JSON file
    pass


def generate_flashcard_summary(question, context):
    # Prompt the LLM with the question and context
    # Generate a short flashcard summary using the LLM's response
    pass


def main():
    st.set_page_config(layout="wide")
    st.title("Question Solver")

    # Initialize session state variables
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "current_question" not in st.session_state:
        st.session_state.current_question = 0
    if "selected_options" not in st.session_state:
        st.session_state.selected_options = {}
    if "start_time" not in st.session_state:
        st.session_state.start_time = {}
    if "end_time" not in st.session_state:
        st.session_state.end_time = {}

    # Upload button for PDF
    pdf_file = st.file_uploader("Upload PDF", type="pdf")
    if pdf_file:
        #parse_pdf(pdf_file)
        st.session_state.questions = json.load(open("extracted_questions.json"))

    # Left panel with question numbers
    if st.session_state.questions:
        question_numbers = [f"Q{i + 1}" for i in range(len(st.session_state.questions))]
        selected_question = st.sidebar.radio("Select Question", question_numbers,
                                             index=st.session_state.current_question)
        st.session_state.current_question = question_numbers.index(selected_question)

    # Display selected question in the middle
    if st.session_state.questions:
        question = st.session_state.questions[st.session_state.current_question]
        st.header(question["question"])
        options = question["options"]
        selected_option = st.radio("Select Option", options, key=f"option_{st.session_state.current_question}")

        if st.session_state.current_question not in st.session_state.start_time:
            st.session_state.start_time[st.session_state.current_question] = time.time()

        if st.button("Submit"):
            st.session_state.selected_options[st.session_state.current_question] = selected_option
            st.session_state.end_time[st.session_state.current_question] = time.time()
            if st.session_state.current_question < len(st.session_state.questions) - 1:
                st.session_state.current_question += 1

        if st.button("Previous") and st.session_state.current_question > 0:
            st.session_state.current_question -= 1

        if st.button("Next") and st.session_state.current_question < len(st.session_state.questions) - 1:
            st.session_state.current_question += 1

    # Update right panel with stats
    if st.session_state.questions:
        with st.expander("Stats"):
            total_time = sum(st.session_state.end_time.get(i, 0) - st.session_state.start_time.get(i, 0) for i in
                             range(len(st.session_state.questions)))
            avg_time_per_question = total_time / len(st.session_state.questions)
            st.write(f"Average time per question: {avg_time_per_question:.2f} seconds")

            for i in range(len(st.session_state.questions)):
                question_time = st.session_state.end_time.get(i, 0) - st.session_state.start_time.get(i, 0)
                st.write(f"Time spent on Q{i + 1}: {question_time:.2f} seconds")

    # Generate report button
    if st.button("Generate Report"):
        # Retrieve questions, selected options, and correctness status
        report_data = []
        for i in range(len(st.session_state.questions)):
            question = st.session_state.questions[i]["question"]
            selected_option = st.session_state.selected_options.get(i)
            is_correct = selected_option == st.session_state.questions[i]["correct_option"]
            flashcard_summary = generate_flashcard_summary(question, st.session_state.questions[i]["context"])
            report_data.append({
                "question": question,
                "selected_option": selected_option,
                "is_correct": is_correct,
                "flashcard_summary": flashcard_summary
            })

        # Generate the report
        report = json.dumps(report_data, indent=2)

        # Provide download option for the report
        st.download_button(
            label="Download Report",
            data=report,
            file_name="question_solver_report.json",
            mime="application/json"
        )


if __name__ == "__main__":
    main()