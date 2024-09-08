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


class SchwabClient:

    def __init__(self):
        self.base_url = "https://api.schwabapi.com"
        self.access_token = init_tokens()
        self.target_account_num = get_target_account_num()

        # need to add checks
        
        self.accounts = self.get_accounts()
        self.target_account = self.get_target_account()
        self.target_account_hash = self.target_account["hashValue"]

    def update_access_token(self):
        self.access_token = refresh_tokens()

    def get_accounts(self):
        response = requests.get(f'{self.base_url}/trader/v1/accounts/accountNumbers',
                            headers={'Authorization': f'Bearer {self.access_token}'})
        if response.status_code != 200:
            logger.error("Failed to get accounts.")
            return None
        accounts = response.json()
        return accounts

    def get_target_account(self):
        accountNums = [account["accountNumber"] for account in self.accounts]
        idx = accountNums.index(self.target_account_num)
        return self.accounts[idx]

    # for dashboard 
    # get account val for risk management methods
    def account_details(self):
        response  = requests.get(f'{self.base_url}/trader/v1/accounts/{self.target_account_hash}',
                                headers={'Authorization': f'Bearer {self.access_token}'})
        if response.status_code != 200:
            logger.error("Failed to get account details.")
            return None
        accounts = response.json()
        print(accounts)
        return accounts

# if __name__ ==  "__main__":

#     client = SchwabClient()
#     client.account_details()
