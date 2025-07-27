from google import genai
from google.oauth2 import service_account

import os
import json
import pandas as pd

from .paper_generation import create_question_paper, create_answer_sheet


# Set the path to your service account key file
# Replace 'path/to/your/service-account.json' with the actual path to your JSON file
SERVICE_ACCOUNT_FILE = "chat/service-account-key.json" 

# Define the scopes for accessing the Gemini API
# This is a critical step, without the correct scopes, requests will be rejected.
SCOPES = ['https://www.googleapis.com/auth/cloud-platform'] 

# Create credentials from the service account key file
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Initialize the GenAI client with the loaded credentials
client = genai.Client(vertexai=True, project="versatile-blend-466717-r7", location="us-central1", credentials=credentials)


def hello_world_prompt():

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Just say hello world!",
        )

        print(response.text)

        return response.text
    except: 
        return None
    

def class_subject_prompt(user_query):

    PROMPT1 = """ Your task is to extract "standard" and "subject" information from the user's query and format it as a JSON object.

    Here are the only supported combinations:
    - **CLASS 10 - MATHS**
    - **CLASS 12 - PHYSICS**

    If the user query contains information matching one of these supported combinations, populate the JSON object.
    If any one key is missing, then keep it empty string. If both are not present, return None

    Don't use ``` at the start & end of the json

    **JSON Format:**

    {
        "standard": {
            "id": "Standard Name",
            "name": "Standard Name"
        },
        "subject": {
            "id": "Subject Name",
            "name": "Subject Name"
        }
    }

    Example 1: 

    User Query - Create a paper for Class 10

    Output - 

    {
        "standard": {
            "id": "CLASS 10",
            "name": "CLASS 10"
        },
        "subject": {
            "id": "",
            "name": ""
        }
    }

    Example 2: 

    User Query - I need a question paper for class 12 & maths

    Output - 

    {
        "standard": {
            "id": "CLASS 12",
            "name": "CLASS 12"
        },
        "subject": {
            "id": "",
            "name": ""
        }
    }

    Example 3: 

    User Query - I'm interested in Class 9 chemistry paper

    Output - 

    {
        "standard": {
            "id": "",
            "name": ""
        },
        "subject": {
            "id": "",
            "name": ""
        }
    }

    Example 3: 

    User Query - Not a relevant query

    Output - 

    None

    #####################


    Actual User Query: """ + user_query + """

    Output - 

    """

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=PROMPT1,
        )

        json_response = json.loads(response.text)

        return json_response
    except Exception as e:
        print(e)
        return None
    
def extract_exam_specifications_prompt(user_query):
    PROMPT2 = """Your task is to extract exam paper specifications from the user's query.
    Specifically, you need to identify the 'difficulty', 'type' of questions, 'number of questions', and 'marks per question'.

    The output should be a JSON list of dictionaries. Each dictionary in the list represents a set of specifications.
    If multiple sets of specifications are mentioned (e.g., "3 easy MCQs for 1 mark each and 2 hard Subjective questions for 5 marks each"), extract all of them as separate dictionaries in the list.

    If a specific piece of information (difficulty, type, questions, marks) is not explicitly mentioned for a given specification set, keep its value as null.
    If the user query is not relevant to exam paper specifications at all, return None.

    Don't use ``` at the start & end of the json.

    **JSON Format:**

    [
        {
            "difficulty": "difficulty_level",
            "type": "question_type",
            "questions": number_of_questions,
            "marks": marks_per_question
        },
        // ... more dictionaries if multiple specifications are found
    ]

    **Supported Values for 'difficulty':**
    - 'easy'
    - 'medium'
    - 'hard'

    **Supported Values for 'type':**
    - 'MCQ' (Multiple Choice Questions)
    - 'Subjective' (Subjective Questions)

    **Example 1:**

    User Query: I need 5 easy mcqs, 1 mark each.

    Output:

    [
        {
            "difficulty": "easy",
            "type": "MCQ",
            "questions": 5,
            "marks": 1
        }
    ]

    **Example 2:**

    User Query: Create a paper with 3 medium Subjective questions, 10 marks each. Also, add 2 easy MCQs.

    Output:

    [
        {
            "difficulty": "medium",
            "type": "Subjective",
            "questions": 3,
            "marks": 10
        },
        {
            "difficulty": "easy",
            "type": "MCQ",
            "questions": 2,
            "marks": 0
        }
    ]

    **Example 3:**

    User Query: I want 7 hard questions.

    Output:

    [
        {
            "difficulty": "hard",
            "type": "",
            "questions": 7,
            "marks": 0
        }
    ]

    **Example 4:**

    User Query: Give me some general knowledge facts.

    Output:

    None

    **Example 5:**

    User Query: generate 3 medium mcq with 1 mark each.

    Output:

    [
        {
            "difficulty": "medium",
            "type": "MCQ",
            "questions": 3,
            "marks": 1
        }
    ]

    **Example 6:**

    User Query: not relevant query 

    Output:

    None

    #####################


    Actual User Query: """ + user_query + """

    Output -

    """

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=PROMPT2,
        )

        json_response = json.loads(response.text)

        return json_response
    except Exception as e:
        print(e)
        return None
    

def generate_mcq_answer_dict(curriculum, standard, subject, markdown, question_config):

    MCQ_PROMPT = """ System Prompt:
        You are a Question Paper Generator tasked with creating high-quality multiple-choice questions (MCQs) from the provided chapter content. You will be given:

        1. A JSON object specifying the exact number of questions to generate for each difficulty level ("Easy", "Medium", "Hard") Note that generate questions for only given difficulty.
        2. Don't add ``` characters at the start and the end of your response.
        3. Chapter content as a markdown with chapter names & page numbers for references
        4. Never reference something without context. Never mention this table or that reference without providing that context in the answer.

        You must strictly adhere to the specified number of MCQs per difficulty level. Generate only as many questions as requested—no more, no fewer.

        Your goal is to craft a balanced, concept-rich set of MCQs that assess not only factual recall but also higher-order thinking skills such as inference, synthesis, application, and reasoning.

        Difficulty Guidelines:
        1. Easy:
        - Focus on definitions, recognition, and basic understanding.
        - Avoid copying text; rephrase and contextualize.
        2. Medium:
        - Assess interpretation, application in new contexts, and relationships.
        3. Hard:
        - Require synthesis, critical thinking, or decision-making in unfamiliar contexts.

        Output Format:
        Return a list of JSON objects, each structured as follows:
        [
            {
                "question": "<Your MCQ question text (mention the marks count at the end of the question in square brackets like e.g [Marks 5])>",
                "options": {
                    "a": "<Option A>",
                    "b": "<Option B>",
                    "c": "<Option C>",
                    "d": "<Option D>"
                },
                "answer": "<Correct option key>",
                "reason": "<Explain why the chosen option is correct and why the other options are incorrect, if relevant.>",
                "difficulty": "Easy" | "Medium" | "Hard",
                "source": [<dict of chapter name & page numbers used to generate this question>]
            },
        ]

    """

    user_prompt = f""" # User prompt:
        Curriculum: {curriculum}
        Standard: {standard}
        Subject: {subject}
        Preference: {question_config}

        References: 

        {markdown}
    """

    prompt = MCQ_PROMPT + user_prompt 

    # print(prompt)

    try:

        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
        )

        # print(response.text)

        json_response = json.loads(response.text)

        return json_response
    except Exception as e:
        print(e)
        return None
    
def generate_subjective_answer_dict(curriculum, standard, subject, markdown, question_config):

    MCQ_PROMPT = """ System Prompt:
        You are a Question Paper Generator tasked with creating high-quality subjective questions from the provided chapter content. You will be given:

        1. A JSON object specifying the exact number of questions to generate for each difficulty level ("Easy", "Medium", "Hard") Note that generate questions for only given difficulty.
        2. Don't add ``` characters at the start and the end of your response.
        3. Chapter content as a markdown with chapter names & page numbers for references
        4. Never reference something without context. Never mention this table or that reference without providing that context in the answer.

        You must **strictly follow the provided question counts per difficulty level**—no more, no less.

        Your task is to generate a well-distributed, conceptually rich set of subjective questions that evaluate a range of cognitive skills from basic recall to advanced reasoning. 
        Distribute the questions across key concepts in the chapter, ensuring variety and cognitive depth as described in the taxonomy below.

        Each question must:
        - Match the specified difficulty level.
        - Be written as a stand-alone question (avoid referencing exact text or location).
        - Include a clearly defined answer with key points/ideas needed for full marks.        

        **Difficulty Taxonomy:**
            1. Easy:
                - Focus on fundamental concepts and definitions.
                - Encourage recognition and recall with clearly phrased, original questions.
            2. Medium:
                - Target deeper understanding, comparison, and moderate application.
                - Require understanding of relationships, sequences, or causes.
            3. Hard:
                - Challenge reasoning, synthesis of multiple ideas, or unfamiliar situations.
                - Encourage higher-order thinking like evaluation and hypothesis testing.


        Output Format:
        Return a list of JSON objects, each structured as follows:
        [
            {
                "question": "<Your question text (mention the marks count at the end of the question in square brackets like e.g [Marks 5])>",
                "difficulty": "Easy" | "Medium" | "Hard",
                "answer": "<Key points/ideas for a full mark answer>",
                "difficulty": "Easy" | "Medium" | "Hard",
                "source": [<dict of chapter name & page numbers used to generate this question>]
            },
        ]
    """

    user_prompt = f""" # User prompt:
        Curriculum: {curriculum}
        Standard: {standard}
        Subject: {subject}
        Preference: {question_config}

        References: 

        {markdown}
    """

    prompt = MCQ_PROMPT + user_prompt 

    # print(prompt)

    try:

        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
        )

        # print(response.text)

        json_response = json.loads(response.text)

        return json_response
    except Exception as e:
        print(e)
        return None
    

def generate_question_paper(user_input: dict):

    df = pd.read_csv("assets/qgenie_kb.csv")

    curriculum = user_input['curriculum']['name']
    standard = user_input['standard']['name']
    subject = user_input['subject']['name']
    topics = [topic['name'] for topic in user_input['topics']]


    markdown = ""

    for topic in topics:

        df_filter = df.apply(lambda x: topic.lower() in x['topic'].lower(), axis=1)

        if df_filter.sum().item() == 0:
            continue;
        
        markdown += "Chapter : " + topic + " \n \n "
        markdown += df[df_filter]['markdown'].iloc[0]

    master_json = []

    for question_config in user_input['question_config']:

        print(curriculum, standard, subject, topics)
        print(json.dumps(question_config, indent=4))

        print()

        if question_config['type'].lower() == "mcq":
            mcq_json = generate_mcq_answer_dict(
                curriculum,
                standard,
                subject,
                markdown,
                json.dumps(question_config),
            )

            if mcq_json != None:
                master_json.append(mcq_json)

            print(json.dumps(mcq_json, indent=4, ensure_ascii=True))
            
        else:
            subjective_json = generate_subjective_answer_dict(
                curriculum,
                standard,
                subject,
                markdown,
                json.dumps(question_config),
            )

            if subjective_json != None:
                master_json.append(subjective_json)

            print(json.dumps(subjective_json, indent=4, ensure_ascii=True))

    OUTPUT_FILENAME_QUESTION = os.path.join(os.getcwd(), "question_paper.pdf")
    OUTPUT_FILENAME_ANSWER = os.path.join(os.getcwd(), "answer_sheet.pdf")

    if len(master_json) == 0:

        if os.path.exists(OUTPUT_FILENAME_QUESTION):
            os.remove(OUTPUT_FILENAME_QUESTION)

        if os.path.exists(OUTPUT_FILENAME_ANSWER):
            os.remove(OUTPUT_FILENAME_ANSWER)

        return None, None, None, None;

    with open("test_json.json", 'w') as file:
        json.dump(master_json, file)

    exam_title = subject.title() + " Sample Paper"
    answer_title = f"{exam_title} - Answer Key"

    # Generate the PDF
    create_question_paper(master_json, OUTPUT_FILENAME_QUESTION, exam_title)

    # Generate the Answer Sheet PDF
    create_answer_sheet(master_json, OUTPUT_FILENAME_ANSWER, answer_title)

    return master_json, OUTPUT_FILENAME_QUESTION, OUTPUT_FILENAME_ANSWER, subject



if __name__ == "__main__":
    # print(json.dumps(class_subject_prompt(user_query="class 9 maths paper"), indent=4))
    # print(json.dumps(class_subject_prompt(user_query="Create a class 10 maths paper for 20 marks"), indent=4))


    # print(json.dumps(
    #     extract_exam_specifications_prompt(user_query="Medium difficulty Subjective questions like 2 or 3 and add more MCQ like 10 of them of 2 marks each"),
    #     indent=4
    # ))


    user_input = {
        "educator_id": "63e3c398-30b0-4325-9569-94fd482a127b",
        "curriculum": {
            "id": "CBSE",
            "name": "CBSE"
        },
        "standard": {
            "id": "CLASS 10",
            "name": "CLASS 10"
        },
        "subject": {
            "id": "MATHS",
            "name": "MATHS"
        },
        "topics": [
            {
                "id": "Real Numbers",
                "name": "Real Numbers"
            },
            {
                "id": "Polynomials",
                "name": "Polynomials"
            }
        ],
        "question_config": [
            {
                "type": "MCQ",
                "questions": 5,
                "marks": 1,
                "difficulty": "medium"
            },
            {
                "type": "Subjective",
                "questions": 3,
                "marks": 2,
                "difficulty": "medium"
            },
            {
                "type": "Subjective",
                "questions": 2,
                "marks": 5,
                "difficulty": "medium"
            }
        ],
        "query": "Pleae generate the question paper"
    }

    # generate_question_paper(user_input=user_input)




    pass