from Crawler.utils.build_prompt import JSON_TEMPLATE
from groq import Groq
import json
from dotenv import load_dotenv
import os

def filter(total_links):
    prompt_sys= """
You are a helpful assistant that filters out the top 10 most relevant links from a list of links.
You have to choose the links that would provide the most usefull information about the said university so that more fields can be filled.
since you have to choose only 10 links, you have to be very selective and choose the most relevant ones."""


    prompt_user = """
The data regarding the links is provided as :
""" + str(total_links) + """

while the json template u have to fill is provided as :
""" + JSON_TEMPLATE + """

**Extremely Important***
    This information is being extracted to help students decide which university and program to pursue based on their academic and financial requirements. so i need max info on these things but also try to fill in atleast a little info on the rest of the fields too so there is something to show there too.

as a response i only need a json object wwith the top 10 relevant links filled in the attribute "links.
the format of the output json should be:
{
    "links": []
}

"""


    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    dotenv_path = os.path.join(BASE_DIR, ".env")

    load_dotenv(dotenv_path)
    
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": prompt_sys
            },
            {
                "role": "user", 
                "content": prompt_user
            }
        ],
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)

    return result["links"]




def filter2(unseen_links,seen_links, prev_json):
    prompt_sys= """
You are a helpful assistant that filters out the top 15 most relevant links from a list of links.
You have to choose the links that would provide the most usefull information about the said university that can be used to fill the information u feel is absent in this json.
since you have to choose only 15 links, you have to be very selective and choose the most relevant ones.
***Extremely Important***
    atleast all the programs of the university should atleast be mentioned in the json since it is the most important thing.
    This information is being extracted to help students decide which university and program to pursue based on their academic and financial requirements. so i need max info on these things but also try to fill in atleast a little info on the rest of the fields too so there is something to show there too.
"""

    prompt_user = """
I had previously used 10 links to curate a json (these are mentioned so u that if u think that a new link would offer 90 percent the same information offered by a selected link. u not use it).
The used links were :
""" + str(seen_links) + """

while the unused links that u have to filter are (u have to choose amongst these) :
""" + str(unseen_links) + """

while the current state of the json is:
""" + json.dumps(prev_json) + """

I reiterate that i need as much info about degree programs (thier financial and academic requirements) as possible

as a response i only need a json object with the top 15 relevant links filled in the attribute "links".
the format of the output json should be:
{
    "links": []
}
"""


    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    dotenv_path = os.path.join(BASE_DIR, ".env")

    load_dotenv(dotenv_path)
    
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": prompt_sys
            },
            {
                "role": "user", 
                "content": prompt_user
            }
        ],
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)

    with open("debug_prompt.txt", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    return result["links"]



def filter3(total_links):
    prompt_sys= """
You are a helpful assistant that filters out the top 5 most relevant pdf links from a list of links.
You have to choose the links that would provide the most usefull information about the programs offered in a said university so that more fields can be filled.
since you have to choose only 5 links, you have to be very selective and choose the most relevant ones that provide the most info
Duplicates should not exist in the final link set. If u can not reach 5 urls without duplicates, u can add fewer then 5 links"""


    prompt_user = """
The data regarding the links is provided as :
""" + str(total_links) + """

while the json template u have to fill is provided as :
""" + JSON_TEMPLATE + """
but remember that i only need info related to programs (their financial and academic requirements),
 so u can ignore the rest for now
**Extremely Important***
    This information is being extracted to help students decide which university and program to pursue based on their academic and financial requirements. so i need max info on these things 

as a response i only need a json object wwith the top 5 relevant links filled in the attribute "links".
the format of the output json should be:
{
    "links": []
}

"""


    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    dotenv_path = os.path.join(BASE_DIR, ".env")

    load_dotenv(dotenv_path)
    
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": prompt_sys
            },
            {
                "role": "user", 
                "content": prompt_user
            }
        ],
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)

    return result["links"]

