import os
import base64
import requests
import pandas as pd
import webbrowser
from loguru import logger
from cryptography.fernet import Fernet
from flask import Request
from loguru import logger
import threading
import time
from datetime import datetime
import dotenv

def load_app_env_vars():

    """
    Loads local environment and app data.
    """

    load_env = dotenv.load_dotenv()

    if not load_env:
        logger.error("Failed to load .env file. Ensure it exists in working directory and try again.")
        return None
        
    try:
        app_key = os.environ["APP_KEY"]
        app_secret = os.environ["APP_SECRET"]
    except KeyError as e:
        logger.error(f"Missing environment variable: {e}. Please add to .env and try again.")
        return None

    return (app_key, app_secret)

def construct_init_auth_url():

    """
    Constructs authorization url.
    """

    app_data = load_app_env_vars()
    app_key, app_secret = app_data[0], app_data[1]

    if not app_data:
        logger.error("There was an error loading app data.")
        return None, None, None

    logger.debug("Retrieved app data!")

    auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={app_key}&redirect_uri=https://127.0.0.1"
    logger.debug(f"Click to authenticate: {auth_url}")
        
    return app_key, app_secret, auth_url
    

def construct_headers_and_payload(returned_url, app_key, app_secret):

    """
    Constructs API headers and payload.
    """
    
    response_code = f"{returned_url[returned_url.index('code=') + 5: returned_url.index('%40')]}@"
    credentials = f"{app_key}:{app_secret}"
    base64_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    
    headers = {"Authorization": f"Basic {base64_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"}
    payload = {"grant_type": "authorization_code",
               "code": response_code, "redirect_uri": "https://127.0.0.1"}

    return headers, payload

def retrieve_tokens(headers, payload):

    """
    Retrieves tokens using headers and payload.
    """
    
    init_token_response = requests.post(
        url="https://api.schwabapi.com/v1/oauth/token",
        headers=headers,
        data=payload)
    init_tokens_dict = init_token_response.json()

    logger.debug("Retrieved tokens!")

    return init_tokens_dict

def init_tokens():

    """
    Initializes and stores relevant tokens.
    """

    # authorization needed for token
    app_key, app_secret, cs_auth_url = construct_init_auth_url()
    webbrowser.open(cs_auth_url)
    logger.info("Paste page URL:")
    returned_url = input()

    # retrieve tokens
    init_token_headers, init_token_payload = construct_headers_and_payload(returned_url, app_key, app_secret)
    init_tokens_dict = retrieve_tokens(headers=init_token_headers, payload=init_token_payload)

    refresh_token = init_tokens_dict["refresh_token"]
    access_token = init_tokens_dict["access_token"]

    dotenv.set_key(".env", "REFRESH_TOKEN", refresh_token)
    logger.info("Initialized tokens and stored refresh token in .env!")

    return access_token

def update_refresh_token(refresh_token):

    """
    Updates and stores refresh token."
    """

    load_env = dotenv.load_dotenv()
    if not load_env:
        logger.error("Failed to load .env file. Ensure it exists in working directory and try again.")
        return False

    dotenv.set_key(".env", "REFRESH_TOKEN", refresh_token)
    logger.debug("Updated refresh token in .env!")
    return True

def load_env_refresh_token():

    """
    Loads local environment and refresh token.
    """

    load_env = dotenv.load_dotenv()
    if not load_env:
        logger.error("Failed to load .env file. Ensure it exists in working directory and try again.")
        return None
        
    try:
        refresh_token = os.environ["REFRESH_TOKEN"]
    except KeyError as e:
        logger.error(f"Missing environment variable: {e}. You have not initialized the tokens.")
        return None

    return refresh_token

def refresh_tokens():

    """
    Get new tokens.
    """

    logger.info("Refreshing tokens...")

    # loading app data
    app_data = load_app_env_vars()
    app_key, app_secret = app_data[0], app_data[1]

    if not app_data:
        logger.error("There was an error loading app data.")
        return None

    # loading refresh token
    refresh_token = load_env_refresh_token()
    if not refresh_token:
        logger.error("There was an error loading the refresh token.")
        return None

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token}
    headers = {
        "Authorization": f'Basic {base64.b64encode(f"{app_key}:{app_secret}".encode()).decode()}',
        "Content-Type": "application/x-www-form-urlencoded"}
    
    refresh_token_response = requests.post(
        url="https://api.schwabapi.com/v1/oauth/token",
        headers=headers,
        data=payload)
    if refresh_token_response.status_code == 200:
        logger.info("Retrieved fresh tokens!")
    else:
        logger.error(f"Error refreshing access token: {refresh_token_response.text}")
        return None

    new_token_dict = refresh_token_response.json()
    logger.debug(new_token_dict)
    update_refresh_token(new_token_dict["refresh_token"])

    logger.info("Done refreshing tokens!")

    return new_token_dict["access_token"]

def refresh_token_handler():
    """
    Function wrapper for using as background process.
    """
    while True:
        refresh_tokens()
        time.sleep(1500) # 25 min refresh time

def dummy_function():
    """
    Dummy function for testing.
    """
    while True:
        logger.debug("Running...")
        time.sleep(0.5)
    

    # if __name__ == "__main__":
#     logger.info("Schwab API Custom Wrapper")
#     init_tokens()
# if __name__ == "__main__":

#     refresh_thread = threading.Thread(target = refresh_token_handler)
#     refresh_thread.daemon = True
#     refresh_thread.start()

#     dummy_function()

def get_target_account_num():

    """
    Load local environment and stored account number.
    """

    load_env = dotenv.load_dotenv()

    if not load_env:
        logger.error("Failed to load .env file. Ensure it exists in working directory and try again.")
        return None
        
    try:
        acc_num = os.environ["ACC_NUM"]
    except KeyError as e:
        logger.error(f"Missing environment variable: {e}. Please add to .env and try again.")
        return None

    return acc_num

