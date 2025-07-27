from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import re
import json


def create_question_paper(sections_data, filepath, title, exam_time="3 Hours"):

    # Setup ReportLab styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenteredHeader', alignment=TA_CENTER, fontSize=16, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='InfoLine', alignment=TA_CENTER, fontSize=12))
    styles.add(ParagraphStyle(name='QuestionNumber', fontSize=12, fontName='Helvetica-Bold', spaceAfter=6, leftIndent=0))
    styles.add(ParagraphStyle(name='QuestionText', fontSize=12, spaceAfter=6, leading=14, leftIndent=18)) # Indent for question text
    styles.add(ParagraphStyle(name='OptionText', fontSize=11, spaceBefore=2, spaceAfter=2, leftIndent=36)) # Further indent for options
    styles.add(ParagraphStyle(name='MarksText', fontSize=10, textColor='#666666', alignment=TA_RIGHT))

    doc = SimpleDocTemplate(filepath, pagesize=letter)
    story = []

    # Add Header
    story.append(Paragraph(title, styles['CenteredHeader']))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(f"Time: {exam_time}", styles['InfoLine']))
    story.append(Spacer(1, 0.3 * inch))

    question_counter = 1
    for section_index, section in enumerate(sections_data):
        for q_data in section:
            question_text = q_data["question"]
            options = q_data.get("options")

            # Extract marks from question text if present
            marks_match = re.search(r'\[Marks (\d+)\]', question_text)
            marks_str = ""
            if marks_match:
                marks_str = f"[Marks: {marks_match.group(1)}]"
                # Remove marks from the question text for display
                question_text = question_text.replace(marks_match.group(0), "").strip()

            # Create a list to hold elements for the current question
            question_elements = []

            # Add question number
            # # Question Number and Text
            # story.append(Paragraph(f"{question_counter}. ", styles['QuestionNumber']))
            
            # # Question text with potential inline marks removed
            # question_para = Paragraph(f"{question_text}", styles['QuestionText'])
            # story.append(question_para)

            story.append(Paragraph(f"{question_counter})  {question_text}", styles['QuestionNumber']))
            
            # Add marks on a new line or aligned to the right if possible
            if marks_str:
                question_elements.append(Paragraph(marks_str, styles['MarksText']))
                question_elements.append(Spacer(1, 0.05 * inch)) # Small space after marks

            # Add options if available
            if options:
                # Ensure options are sorted (a, b, c, d)
                sorted_options = sorted(options.items())
                for key, value in sorted_options:
                    question_elements.append(Paragraph(f"({key}) {value}", styles['OptionText']))
                question_elements.append(Spacer(1, 0.2 * inch)) # Space after MCQ options
            else:
                # Add more space for subjective questions for students to write
                question_elements.append(Spacer(1, 0.8 * inch)) # More space for subjective questions

            # Add all elements for the current question to the main story
            story.extend(question_elements)
            
            question_counter += 1
        
        # Add a page break after each section for better organization, unless it's the last section
        # if section_index < len(sections_data) - 1:
        #      story.append(PageBreak())

    try:
        doc.build(story)
        print(f"Question paper '{filepath}' created successfully!")
    except Exception as e:
        print(f"Error creating PDF: {e}")


def create_answer_sheet(sections_data, filepath, title):

    # Setup ReportLab styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenteredTitle', alignment=TA_CENTER, fontSize=16, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='QuestionNumber', fontSize=12, fontName='Helvetica-Bold', spaceAfter=6, spaceBefore=12))
    styles.add(ParagraphStyle(name='QuestionText', fontSize=12, spaceAfter=6, leading=14))
    styles.add(ParagraphStyle(name='AnswerLabel', fontSize=11, fontName='Helvetica-Bold', spaceBefore=6))
    styles.add(ParagraphStyle(name='AnswerContent', fontSize=11, spaceBefore=2, spaceAfter=6, leftIndent=12))
    styles.add(ParagraphStyle(name='OptionText', fontSize=11, spaceBefore=2, spaceAfter=2, leftIndent=24)) # Style for options in answer sheet
    styles.add(ParagraphStyle(name='ReasonLabel', fontSize=11, fontName='Helvetica-Bold', spaceBefore=6))
    styles.add(ParagraphStyle(name='ReasonContent', fontSize=11, spaceBefore=2, spaceAfter=6, leftIndent=12))
    styles.add(ParagraphStyle(name='DifficultySource', fontSize=9, textColor='#555555', spaceBefore=4, spaceAfter=2))
    styles.add(ParagraphStyle(name='MarksText', fontSize=10, textColor='#666666', alignment=TA_RIGHT))


    doc = SimpleDocTemplate(filepath, pagesize=letter)
    story = []

    # Add Title
    story.append(Paragraph(title, styles['CenteredTitle']))
    story.append(Spacer(1, 0.3 * inch))

    question_counter = 1
    for section_index, section in enumerate(sections_data):
        for q_data in section:
            question_text = q_data["question"]
            options = q_data.get("options")
            answer = q_data.get("answer")
            reason = q_data.get("reason")
            difficulty = q_data.get("difficulty")
            source = q_data.get("source")

            # Extract marks from question text if present (and clean for display)
            marks_match = re.search(r'\[Marks (\d+)\]', question_text)
            marks_str = ""
            if marks_match:
                marks_str = f"[Marks: {marks_match.group(1)}]"
                question_text = question_text.replace(marks_match.group(0), "").strip() # Remove marks from question

            # # Question Number and Text
            # story.append(Paragraph(f"{question_counter}. ", styles['QuestionNumber']))
            
            # # Question text with potential inline marks removed
            # question_para = Paragraph(f"{question_text}", styles['QuestionText'])
            # story.append(question_para)

            story.append(Paragraph(f"{question_counter})  {question_text}", styles['QuestionNumber']))
            
            # Add marks on a new line or aligned to the right if possible
            if marks_str:
                story.append(Paragraph(marks_str, styles['MarksText']))
                story.append(Spacer(1, 0.05 * inch)) # Small space after marks

            # Add MCQ options if available in the question
            if options:
                sorted_options = sorted(options.items())
                for key, value in sorted_options:
                    story.append(Paragraph(f"({key}) {value}", styles['OptionText']))
                story.append(Spacer(1, 0.1 * inch)) # Small space after MCQ options list

            if options and answer:
                # For MCQs, show the correct option text
                story.append(Paragraph("<b>Correct Answer:</b>", styles['AnswerLabel']))
                correct_option_text = options.get(answer)
                story.append(Paragraph(f"({answer}) {correct_option_text}", styles['AnswerContent']))
            # elif answer:
            #     # For subjective questions, the 'answer' field is the solution
            #     story.append(Paragraph(answer.replace("\\n", "<br/>"), styles['AnswerContent'])) # Replace \n with <br/> for ReportLab

            # Add Reason/Solution
            if reason:
                story.append(Paragraph("<b>Reason:</b>", styles['ReasonLabel']))
                story.append(Paragraph(reason.replace("\\n", "<br/>"), styles['ReasonContent']))
            elif not options and answer: # If it's a subjective question and 'answer' is the full solution
                story.append(Paragraph("<b>Solution:</b>", styles['ReasonLabel']))
                story.append(Paragraph(answer.replace("\\n", "<br/>"), styles['ReasonContent']))

            # Add Difficulty
            if difficulty:
                story.append(Paragraph(f"<b>Difficulty:</b> {difficulty}", styles['DifficultySource']))

            # Add Source
            if source:
                source_str_parts = []
                for s in source:
                    chapter = s.get("Chapter") or s.get("chapter")
                    page_info = s.get("Page Number") or s.get("page_numbers")
                    
                    if chapter and page_info:
                        if isinstance(page_info, list):
                            pages = ", ".join(map(str, page_info))
                            source_str_parts.append(f"Chapter: {chapter}, Page(s): {pages}")
                        else:
                            source_str_parts.append(f"Chapter: {chapter}, Page: {page_info}")
                if source_str_parts:
                    story.append(Paragraph(f"<b>Source:</b> {' | '.join(source_str_parts)}", styles['DifficultySource']))
            
            story.append(Spacer(1, 0.3 * inch)) # Space after each question's answer/reason

            question_counter += 1
        
        # Add a page break after each section for better organization, unless it's the last section
        # if section_index < len(sections_data) - 1:
        #      story.append(PageBreak())

    try:
        doc.build(story)
        print(f"Answer sheet '{filepath}' created successfully!")
    except Exception as e:
        print(f"Error creating PDF: {e}")



if __name__ == "__main__":

    # Default Exam Details
    EXAM_NAME = "Mathematics Sample Paper"
    ANSWER_KEY_TITLE = f"{EXAM_NAME} - Answer Key"

    OUTPUT_FILENAME = "question_paper.pdf"
    OUTPUT_FILENAME_ANSWER = "answer_sheet.pdf"

    with open("test_json.json", 'r') as file:
        sections_data = json.load(file)

    # Generate the Answer Sheet PDF
    create_answer_sheet(sections_data, OUTPUT_FILENAME_ANSWER, ANSWER_KEY_TITLE)

    # Generate the PDF
    create_question_paper(sections_data, OUTPUT_FILENAME, EXAM_NAME)