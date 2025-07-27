

from .prompt_processor import class_subject_prompt, extract_exam_specifications_prompt


def get_bot_reponse(req_body):
    if len(list(req_body['standard'].keys())) == 0:
        response = class_subject_prompt(req_body["query"])
        if response == None:
            return {
                    "bot": {
                        "text": "Default output",
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
                        "text": "Default output",
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
    return {
            "bot": {
                "text": "Please find the question paper generated here",
                "items": []
            },
            "type": "default"
        } 


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