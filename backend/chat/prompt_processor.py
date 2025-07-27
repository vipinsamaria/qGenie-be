from google import genai
from google.oauth2 import service_account

import json


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
    

if __name__ == "__main__":
    # print(json.dumps(class_subject_prompt(user_query="class 9 maths paper"), indent=4))
    print(json.dumps(class_subject_prompt(user_query="Create a class 10 maths paper for 20 marks"), indent=4))


    # print(json.dumps(
    #     extract_exam_specifications_prompt(user_query="Medium difficulty Subjective questions like 2 or 3 and add more MCQ like 10 of them of 2 marks each"),
    #     indent=4
    # ))


    pass