import json
from openai import OpenAI

def gen_message_record(role, content):
    return {
        "role": role,
        "content": content
    }

def gen_user_message_record(content):
    return gen_message_record("user", content)

def is_message_record(thing):
    return isinstance(thing, dict) and "role" in thing and "content" in thing and isinstance(thing["content"], str)

def fetch_openai_json(messages, json_schema=None):
    _messages = []
    if isinstance(messages, str):
        _messages = [gen_user_message_record(messages)]
        
    elif isinstance(messages, dict):
        _messages = [gen_user_message_record(json.dumps(messages))]
    
    elif is_message_record(messages):
        _messages = [messages]
    
    elif isinstance(messages, list):
        _messages = [
            gen_user_message_record(msg) if isinstance(msg, str) 
            else gen_user_message_record(json.dumps(msg)) if isinstance(msg, dict) 
            else msg if is_message_record(msg)
            else AssertionError(f"Invalid message format: {msg}")
            for msg in messages
        ]
    
    else:
        raise ValueError("Invalid messages format. Must be a string, a message record, or a list of these.")
    
    response_content = OpenAI().chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=10000,
        messages=[
            *_messages,
            gen_message_record("user", json.dumps(json_schema)),
        ],
        response_format = { "type": "json_object" }
    )
    
    ret = response_content.choices[0].message.content
    # print("type of ret:", type(ret))
    try:
        return json.loads(ret)
    except Exception as e:
        print(f"Error parsing openai json response: {ret}, Error: {e}")
        return None


# def test_fetch_openai_json_response():
#     example_schema = json.dumps({
#         "type": "object",
#         "properties": {
#             "a": {
#                 "type": "string"
#             },
#             "b": {
#                 "type": "integer"
#             }
#         },
#         "required": ["a", "b"]
#     })
    
#     message = f"Generate a JSON object that matches the schema"
    
#     response_content = fetch_openai_json(example_schema, message)
#     print("response_content:", response_content)

# test_fetch_openai_json_response()