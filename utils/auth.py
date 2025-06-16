import boto3
import os
from dotenv import load_dotenv

# Load .env file values
load_dotenv()

def get_aws_credentials_from_cognito():
    region = os.getenv("AWS_REGION")
    username = os.getenv("COGNITO_USERNAME")
    password = os.getenv("COGNITO_PASSWORD")
    client_id = os.getenv("AWS_APP_CLIENT_ID")
    user_pool_id = os.getenv("AWS_USER_POOL_ID")
    identity_pool_id = os.getenv("AWS_IDENTITY_POOL_ID")

    # Step 1: Authenticate with Cognito User Pool using USER_PASSWORD_AUTH
    idp_client = boto3.client("cognito-idp", region_name=region)
    try:
        response = idp_client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password,
            },
            ClientId=client_id,
        )
    except idp_client.exceptions.NotAuthorizedException:
        raise Exception("❌ Cognito authentication failed. Check your username/password.")

    id_token = response["AuthenticationResult"]["IdToken"]

    # Step 2: Exchange token for temporary AWS credentials via Identity Pool
    identity_client = boto3.client("cognito-identity", region_name=region)
    identity_id = identity_client.get_id(
        IdentityPoolId=identity_pool_id,
        Logins={f"cognito-idp.{region}.amazonaws.com/{user_pool_id}": id_token}
    )["IdentityId"]

    credentials = identity_client.get_credentials_for_identity(
        IdentityId=identity_id,
        Logins={f"cognito-idp.{region}.amazonaws.com/{user_pool_id}": id_token}
    )["Credentials"]

    return credentials
