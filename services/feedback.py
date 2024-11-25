import os
from openai import OpenAI
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

'''
CITATIONS:
OpenAI. (2024, October 25). Quickstart guide. OpenAI. Retrieved October 25, 2024, from https://platform.openai.com/docs/quickstart
ChatGPT. (2024, October 25). Chat session. https://chatgpt.com/share/671bc3ca-9958-8009-a7f4-da90a0f7ccf2
OpenAI. (2024, October 25). Prompt engineering. OpenAI. Retrieved October 25, 2024, from https://platform.openai.com/docs/guides/prompt-engineering
NVIDIA. (2024, October 25). LLAMA 3.1 Nemotron 70B instruct. NVIDIA. Retrieved October 25, 2024, from https://build.nvidia.com/nvidia/llama-3_1-nemotron-70b-instruct
'''

models = {
    "nemotron": {
        "name": "nvidia/llama-3.1-nemotron-70b-instruct",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": os.environ.get("NVIDIA_API_KEY")
    },
    "llama": {
        "name": "Meta-Llama-3.1-405B-Instruct",
        "base_url": "https://models.inference.ai.azure.com",
        "api_key": os.environ.get("GITHUB_API_KEY")
    }
}
model = models[os.environ.get("MODEL")]

client = OpenAI(
    base_url = model["base_url"],
    api_key = model["api_key"]
)

def query_openai_api(messages: list):
    '''
    Llama-3.1-Nemotron-70B-Instruct is a large language model customized by NVIDIA in order to improve the helpfulness of LLM generated responses.
    '''
    completion = client.chat.completions.create(
        model=model["name"],
        messages=messages,
        temperature=0.2,
        top_p=1,
        max_tokens=1024,
        stream=True
    )

    response = ""
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            response += chunk.choices[0].delta.content

    return response

def query_azure_api(messages: list):
    client = ChatCompletionsClient(
        endpoint=model["base_url"],
        credential=AzureKeyCredential(model["api_key"]),
    )
    response = client.complete(
        messages=messages,
        temperature=0.2,
        top_p=1.0,
        max_tokens=1024,
        model=model["name"],
    )
    feedback = response.choices[0].message.content
    return feedback



def generate_feedback(writing_sample: str, focus: str = None):
    if not focus:
        focus = '''higher-order concerns, such as:
- Strength and complexity of the argument
- Clarity and organization of ideas
- Factual accuracy
- Use of evidence and examples'''

    system_prompt = f'''
You are grade school ELA teacher providing feedback on a student essay.

First, identify the greatest strength and biggest weakness in the writing sample.
Focus on {focus}

Then, provide praise on the strength and constructive feedback on the weakness.
Use language that is encouraging and supportive, suited for a young grade school student.
Use examples, comparisons, and/or questions to illustrate your points.

Your response should be 3-5 sentences, formatted like this (do not preface, start with the word Glow):
Glow: [praise]
Grow: [constructive feedback]

'''
    if os.environ.get("MODEL") == "nemotron":
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": writing_sample}
        ]
        response = query_openai_api(messages)

    elif os.environ.get("MODEL") == "llama":
        messages = [
            SystemMessage(content=system_prompt),
            UserMessage(content=writing_sample)
        ]
        response = query_azure_api(messages)

    print("RESPONSE:\n\n")
    print(response)

    return response


def analyze_trends(essays: list, assignment_focus: str = None):
    '''
    Analyze trends in student essays.
    '''
    if not assignment_focus:
        assignment_focus = '''higher-order concerns, such as:
- Strength and complexity of the argument
- Clarity and organization of ideas
- Factual accuracy
- Use of evidence and examples'''

    system_prompt = f'''
    You are a grade school ELA teacher. You have been given a set of student essays to review.
    The focus of the assignment was on {assignment_focus}.
    Each of the essays received LLM-generated feedback.
    Analyze the essays (with their respective feedback) and identify common strengths and weaknesses.
    They will be formatted as follows:
    ----------------------------------------
    Submission #[number]
    Essay: [essay content]
    Feedback: [LLM-generated feedback]
    Provide a list of 1-2 strengths and 1-2 weaknesses you observed in the student essays and feedback, paying special attention to strengths and weaknesses related to the assignment focus.
    Format your response using this structure:
    STRENGTHS:
    [bulleted list of strengths with * at the beginning of each line]
    WEAKNESSES:
    [bulleted list of weaknesses with * at the beginning of each line]
    '''

    user_essays = ""
    for i, essay in enumerate(essays):
        user_essays += f'''
        ----------------------------------------
        Submission #{i + 1}
        Essay: {essay["content"]}
        Feedback: {essay["feedback"]}
        '''

    if os.environ.get("MODEL") == "nemotron":
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_essays}
        ]
        response = query_openai_api(messages)

    elif os.environ.get("MODEL") == "llama":
        messages = [
            SystemMessage(content=system_prompt),
            UserMessage(content=user_essays)
        ]
        response = query_azure_api(messages)
    # Format the response
    strengths = response.split('STRENGTHS:')[1].split('WEAKNESSES:')[0].strip()
    weaknesses = response.split('WEAKNESSES:')[1].split('ADDITIONAL COMMENTS:')[0].strip()
    strengths = strengths.replace('***', '*')
    weaknesses = weaknesses.replace('***', '*')
    strengths = strengths.replace('**', '*')
    weaknesses = weaknesses.replace('**', '*')
    strengths = strengths.split('*')
    weaknesses = weaknesses.split('*')
    return strengths, weaknesses