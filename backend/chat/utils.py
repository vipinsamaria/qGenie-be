

from .prompt_processor import class_subject_prompt, extract_exam_specifications_prompt, generate_question_paper
from google.cloud import storage
import os


DEFAULT_MESSAGE = """Hello! I'm your dedicated AI assistant, here to simplify and speed up the process of generating question papers for your classes. My goal is to save you valuable time, allowing you to focus more on teaching and less on administrative tasks.

To help me create the perfect question paper for your students, please let me know the standard (e.g., Class 10, Class 12) and the subject (e.g., Maths, Physics) you're preparing for. Once I have this basic information, we can then refine the paper with specific topics, question types, and difficulty levels."""

def get_bot_reponse(req_body):
    if len(list(req_body['standard'].keys())) == 0:
        response = class_subject_prompt(req_body["query"])
        if response == None:
            return {
                    "bot": {
                        "text": DEFAULT_MESSAGE,
                        "items": []
                    },
                    "type": "default"
                }
        else:
            return {
                "bot": {
                    "text": "Please confirm the standard & subject for the paper",
                    "items": [
                        response
                    ]
                },
                "type": "standard_subject_config"
            }
        
    elif len(req_body['question_config']) == 0:

        response = extract_exam_specifications_prompt(req_body["query"])

        if response == None:
            return {
                    "bot": {
                        "text": DEFAULT_MESSAGE,
                        "items": []
                    },
                    "type": "default"
                }
        else:
            return {
                "bot": {
                "text": "Please confirm the standard and subject for which question paper needs to be constructed",
                "items": response,
            },
            "type": "confirm_config"
        }
    """
    {"educator_id":"63e3c398-30b0-4325-9569-94fd482a127b","curriculum":{"id":"CBSE","name":"CBSE"},"standard":{"id":"CLASS 10","name":"CLASS 10"},"subject":{"id":"MATHS","name":"MATHS"},"topics":[{"id":"Real Numbers","name":"Real Numbers"},{"id":"Polynomials","name":"Polynomials"}],"question_config":[{"type":"MCQ","questions":5,"marks":1,"difficulty":"medium"},{"type":"Subjective","questions":3,"marks":2,"difficulty":"medium"},{"type":"Subjective","questions":2,"marks":5,"difficulty":"medium"}],"query":"Pleae generate the question paper"}
    
    """

    response, question_paper_path, answer_sheet_path, subject = generate_question_paper(req_body)

    if response == None:
        return {
                    "bot": {
                        "text": "Our servers encountered an error! We are looking into it. Thank you.",
                        "items": []
                    },
                    "type": "default"
                }
    

    unique_id = os.urandom(6).hex()

    # Use descriptive and distinct names
    QUESTION_DESTINATION_BLOB_NAME = f"pdfs/{unique_id}_{subject.lower()}_question_paper.pdf"
    ANSWER_DESTINATION_BLOB_NAME = f"pdfs/{unique_id}_{subject.lower()}_answer_sheet.pdf"

    # --- Dummy variables for the example ---
    project_id = "qgenie-467111"
    bucket_name = "qgenie-question-papers"
    # ----------------------------------------

    # Call the updated function to get signed URLs
    question_url = upload_and_get_signed_url(project_id, bucket_name, question_paper_path, QUESTION_DESTINATION_BLOB_NAME)
    answer_url = upload_and_get_signed_url(project_id, bucket_name, answer_sheet_path, ANSWER_DESTINATION_BLOB_NAME)


    # Return the signed URLs
    return {
        "bot": {
            "text": f"Please find the files generated here \n\nQuestion Paper: {question_url} \n\nAnswer Sheet: {answer_url}",
            "items": []
        },
        "type": "default"
    }


import datetime
from google.cloud import storage

def upload_and_get_signed_url(project_id, bucket_name, source_file_path, destination_blob_name):
    """
    Uploads a file to GCS and returns a time-limited signed URL for access.
    
    Args:
        project_id (str): Your Google Cloud project ID.
        bucket_name (str): Name of the GCS bucket.
        source_file_path (str): Local path to the file.
        destination_blob_name (str): Name for the file in the bucket.
    
    Returns:
        str: A signed URL to access the file, or None on error.
    """
    try:
        storage_client = storage.Client(project=project_id)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        
        # Upload the file
        blob.upload_from_filename(source_file_path)
        print(f"File {source_file_path} uploaded to {destination_blob_name}.")

        # Generate a signed URL, valid for 1 hour (you can change this)
        expiration_time = datetime.timedelta(hours=1)
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=expiration_time,
            method="GET",
        )
        
        print(f"Generated Signed URL: {signed_url}")
        return signed_url
    
    except Exception as e:
        print(f"Error processing file: {e}")
        return None

# def upload_pdf_to_gcs(project_id, bucket_name, source_file_path, destination_blob_name):
#     """
#     Uploads a PDF file to a Google Cloud Storage bucket and makes it publicly accessible.
    
#     Args:
#         project_id (str): Your Google Cloud project ID.
#         bucket_name (str): Name of the GCS bucket.
#         source_file_path (str): Local path to the PDF file.
#         destination_blob_name (str): Name for the file in the bucket.
    
#     Returns:
#         str: Public URL of the uploaded file.
#     """
#     try:
#         # Initialize the GCS client
#         storage_client = storage.Client(project=project_id)
        
#         # Get the bucket
#         bucket = storage_client.bucket(bucket_name)
        
#         # Create a blob object
#         blob = bucket.blob(destination_blob_name)
        
#         # Upload the file
#         blob.upload_from_filename(source_file_path)
        
#         # Make the blob publicly accessible
#         blob.make_public()
        
#         # Get the public URL
#         public_url = blob.public_url
        
#         print(f"File {source_file_path} uploaded to {destination_blob_name}.")
#         print(f"Public URL: {public_url}")
        
#         return public_url
    
#     except Exception as e:
#         print(f"Error uploading file: {e}")
#         return None




"""

    elif req_body["query"] == "create config":
        return {
                "bot": {
                "text": "Please confirm the standard and subject for which question paper needs to be constructed",
                "items": [
                    {
                        "standard": {
                            "standard_id": "CLASS 9",
                            "standard_name": "CLASS 9"
                        },
                        "subject": {
                            "subject_id": "Science",
                            "subject_name": "Science"
                        }
                    }
                ],
            },
            "type": "confirm_config"
        }
    elif req_body["query"] == "Pleae generate the question paper":
        return {
                "bot": {
                "text": "Please download the paper",
                "items": [
                ],
            },
            "type": "confirmed"
        }
    return {
        "bot": {
            "text": "Please confirm the difficulty, type, questions and marks for which question paper needs to be constructed",
            "items": [
                    {
                        "difficulty": 'medium',
                        "type": 'MCQ',
                        "questions": 3,
                        "marks": 1
                    }
            ]
        },
        "type": "confirm_config"
    }

"""


"""
build seperate table for curriculum with following properties:
{
    _id: UUID,
    curriculum: str
}

build seperate table for standard with following properties:
{
    _id: UUID,
    curriculum_id: <_id of the curriculum this standard belongs to>
    standard: str
}

build seperate table for subject with following properties:
{
    _id: UUID,
    standard_id: <_id of the standard this subject belongs to>
    subject: str
}

build seperate table for topics with following properties:
{
    _id: UUID,
    subject_id: <_id of the subject this topic belongs to>
    topic: str,
    gcs_url: <url of the bucket object for this topic>
    extraction: dict
}

examples to use for populating these tables before hand are as follows:-

Curriculum      Standard        Subject     Topic
CBSE            Class 10        Science     ...
CBSE            Class 10        English     ...
.
.
.


for certain keys in topics table documents : 
there will be a seperate API which is 
path = /add_knowledge_base
method = post

payload = {
    subject_id UUID,
    topic: str,
    file: <Binary>
}

// this api uploads the file provided in the payload to a GCS bucket and once done, then creates a record in the topic table with provided subject_id and add the gcs object private_url and store this against the key called "gcs_url". 
// Once done then it will call a function called extract_content(topic_Id, gcs_url) which return a dict and that dict is then written against the value of key "extraction" in the  document with the provided topic_Id.

reponse = {
    curriculum: {
        id: UUID,
        topic: str,
    },
    standard: {
        id: UUID,
        standard: str,
    },
    subject: {
        id: UUID,
        subject: str,
    },
    topic: {
        id: UUID,
        topic: str,
    }
}




// api to fetch curriculum for the educator
payload = {
    educator_id: UUID
}

//since the curriculum_id is mapped to institute and educator is mapped to institute via the affiliation code. So use this context to find the correct curriculum id

reponse = {
    curriculum: {
        id: UUID,
        name: str
}

// api to fetch standard for the given curriculum
payload = {
    curriculum_id: UUID
}

reponse = {
    standards: [
        {
            standard_id: UUID,
            standard: str
        }
    ]
}

// api to fetch subject for the given standard
payload = {
    standard_id: UUID
}

reponse = {
    subjects: [
        {
            subject_id: UUID,
            subject: str
        }
    ]
}


// api to fetch topics for the given subject
payload = {
    subject_id: UUID
}

reponse = {
    topics: [
        {
            topic_id: UUID,
            topic: str
        }
    ]
}

// function get_bot_message()

input = {
    "educator_id": UUID,
    "curriculum: curriculum_id,
    "standard": standard_id,
    "subject": subject_id,
    "topics": arr[topic_id], 
    "question_config": [
        {
            difficulty: str,
            type: str,
            marks: int,
            frequency: int
        }
    ],
    "user": str
}

output = {
    bot: {
        "text": str,
        items: arr;
    }
    type: str
}

exmaples for get_bot_message():

1. input = {
    "educator_id": 123,
    "curriculum: CBSE,
    "standard": null,
    "subject": null,
    "topics": null, 
    "question_config": null,
    "user": "I want a maths paper for class 10 of 20 marks"
}

output = {
    bot: {
        text: "Please confirm the standard and subject for which question paper needs to be constructed",
        items: [
            {
                standard: {
                    standard_id: UUID,
                    standard_name: str
                },
                subject: {
                    subject_id: UUID,
                    subject_name: str
                }
            }
        ]
    }
    type: "standard_subject_config"
}



2. input = {
    "educator_id": 123,
    "curriculum: CBSE,
    "standard": Class 10,
    "subject": Maths,
    "topics": ['topic_id', 'topic_id', 'topic_id'], 
    "question_config": null,
    "user": "Medium difficulty with 5 MCQ questions of 1 mark each, 3 Short answers of 2 marks each and 2 long answers of 5 marks each"
}

output = {
    bot: {
        text: "Please confirm your question paper structure:",
        items: [
        {
            difficulty: "easy",
            type: "MCQ",
            count: 3,
            frequency: 1
        },
        .
        .
        .
    ]
    }
    type: "question_config"
}

3. input = {
    "educator_id": 123,
    "curriculum: CBSE,
    "standard": Class 10,
    "subject": Maths,
    "topics": ['topic_id', 'topic_id', 'topic_id'], 
    "question_config": [
        {
            difficulty: 'medium',
            type: 'MCQ',
            questions: 3,
            marks: 1
        },
        .
        .
        .
    ],
    "user": "Confirmed - Generate question paper"
}

output = {
    bot: {
        text: "Here is your generated question paper: [Download Question Paper](https://example.com/paper.pdf)",
        items: []
    type: "confirm_config"
}


if function faced any error then, error_message schema:
{
    bot: {
        text: "Appologies to understand your concern. QGenie is build to asssit you in building comprehensive evaluation exams. Please rephrase your query correctly.",
    }
    type: "error"
}

"""