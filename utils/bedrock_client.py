import os
import json
import boto3
from dotenv import load_dotenv
from .auth import get_aws_credentials_from_cognito

load_dotenv()

def get_bedrock_client():
    creds = get_aws_credentials_from_cognito()
    session = boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretKey"],
        aws_session_token=creds["SessionToken"],
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )
    return session.client("bedrock-runtime")

def call_claude_model(user_input, model_id):
    import boto3
    import json
    import os
    from .auth import get_aws_credentials_from_cognito

    creds = get_aws_credentials_from_cognito()

    session = boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretKey"],
        aws_session_token=creds["SessionToken"],
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )

    client = session.client("bedrock-runtime")

    # ✅ Inject system.md content directly into user input
    with open("system.md", "r", encoding="utf-8") as f:
        system_prompt = f.read().strip()

    # 👇 Combine system + user prompt into the first user message
    combined_prompt = f"{system_prompt}\n\nUser: {user_input}"

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {"role": "user", "content": combined_prompt}
        ],
        "max_tokens": 1024,
        "temperature": 0.3,
        "top_p": 1
    })

    response = client.invoke_model(
        body=body,
        modelId=model_id,
        accept="application/json",
        contentType="application/json"
    )

    result = json.loads(response["body"].read())

    if isinstance(result.get("content"), list):
        return result["content"][0]["text"]
    return result.get("completion", "[No response]")
