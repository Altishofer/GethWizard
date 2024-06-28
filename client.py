import json
import time
from typing import Mapping
from retry import retry
import requests

from eth_account import Account
from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.middleware import geth_poa_middleware


def print_with_frame(message) -> None:
    """
    Prints a large frame with a title inside
    Args:
        message: Title to put into the frame

    Returns: None

    """
    message_length = len(message)
    print(f"{' ' * 20}+{'-' * (message_length + 2)}+")
    print(f"{'*' * 20}| {message.upper()} |{'*' * 20}")
    print(f"{' ' * 20}+{'-' * (message_length + 2)}+")


class Blockchain:
    """
        Handles interaction with Oracle and Non-Validator Node of Blockchain Network
    """

    # static ip address of non-validator node with RPC-API
    __rpc_url = "http://localhost:8545"

    # static ip address of oracle with REST-API
    __oracle_url = "http://localhost:8081"

    # static REST header for communication with Oracle
    __rest_header = {
        'Content-type': 'application/json',
        'Accept': 'application/json'
    }

    def __init__(self):

        print_with_frame("BLOCKCHAIN INITIALIZATION: START")

        # randomly generated private key, needed to sign transaction
        self.__private_key = str()

        # public wallet address generated from the private key
        self.__acc_address = str()

        # ETH balance
        self.__balance = float()

        # generate randomized primary key
        self.__acc = self.__create_account()

        # configure web3 objects for using Proof-of-Authority
        self.__web3 = self.__initialize_web3()

        # call Oracle to sense if blockchain is ready
        print(f"{'-' * 25} CONNECT TO ORACLE {'-' * 25}")
        self.__wait_for_blockchain()

        # request ETH funds for creating transactions, paying gas
        self.__request_funds_from_oracle()

        # check if funds were assigned by checking directly with blockchain
        self.verify_balance()

        # request contract address and header from Oracle
        self.__contract_obj = self.__get_contract_from_oracle()

        print(f"{'-' * 25} CONNECTION TO ETHEREUM AND ORACLE READY {'-' * 25}")

        # TODO: remove before pushing to prod
        self.__testing()

    @classmethod
    @property
    def oracle_url(cls) -> str:
        return cls.__oracle_url

    @classmethod
    @property
    def rest_header(cls) -> Mapping[str, str]:
        return cls.__rest_header

    @retry((Exception, requests.exceptions.HTTPError), tries=20, delay=4)
    def __wait_for_blockchain(self) -> None:
        """
        Request state of blockchain from Oracle by periodic calls and sleep
        Returns: None
        """

        # check with oracle if blockchain is ready for requests
        response = requests.get(
            url=f"{self.__oracle_url}/status",
            headers=self.__rest_header,
            timeout=20
        )

        # raise Exception if status is not successful
        response.raise_for_status()

        return print(f"ORACLE: Blockchain is ready")

    def __initialize_web3(self):
        web3 = Web3(Web3.HTTPProvider(self.__rpc_url))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        web3.middleware_onion.add(construct_sign_and_send_raw_middleware(self.__acc))
        web3.eth.default_account = self.__acc_address
        print(f"CLIENT: Web3 is configured for PoA")
        return web3

    @retry((Exception, requests.exceptions.HTTPError), tries=3, delay=4)
    def __request_funds_from_oracle(self) -> None:
        """
        Requests funds from Oracle by sending public address
        Returns: None

        """

        # call oracle's faucet by Http post request
        response = requests.post(
            url=f"{self.__oracle_url}/faucet",
            json={f"address": self.__acc_address},
            headers=self.__rest_header,
            timeout=20
        )

        # raise Exception if status is not successful
        response.raise_for_status()

        return print(f"ORACLE: Received 500 ETH", flush=True)

    @retry((Exception, requests.exceptions.HTTPError), tries=3, delay=4)
    def __get_contract_from_oracle(self):
        """
        Requests header file and contract address, generates Web3 Contract object with it
        Returns: Web3 Contract object
        """

        response = requests.get(
            url=f"{self.__oracle_url}/contract",
            headers=self.__rest_header,
            timeout=20
        )

        # raise Exception if status is not successful
        response.raise_for_status()

        # convert response to json to extract the abi and address
        json_response = response.json()

        print(f"ORACLE: Initialized chain code: {json_response.get('address')}")

        # return an initialized web3 contract object
        return self.__web3.eth.contract(
            abi=json_response.get("abi"),
            address=json_response.get("address")
        )

    def __create_account(self):
        """
        Generates randomized primary key and derives public account from it
        Returns: None

        """
        print(f"{'-' * 25} REGISTER WORKING NODE {'-' * 25}")

        # generate random private key, address, public address
        acc = Account.create()

        # initialize web3 utility object
        web3 = Web3()

        # convert private key to hex, used in raw transactions
        self.__private_key = web3.to_hex(acc.key)

        # convert address type, used in raw transactions
        self.__acc_address = web3.to_checksum_address(acc.address)

        print(f"CLIENT: Account address: {self.__acc_address}")

        # return generated account
        return acc

    def verify_balance(self) -> int:
        """
        Calls blockchain directly for requesting current balance
        Returns: balance in ETH

        """

        # directly call view method from non-validator node
        balance = self.__web3.eth.get_balance(self.__acc_address, "latest")

        # convert wei to ether
        balance_eth = self.__web3.from_wei(balance, "ether")
        print(f"BLOCKCHAIN: Successfully verified balance of {balance_eth} ETH")

        return balance_eth

    def __sign_and_deploy(self, trx_hash):
        """
        Signs a function call to the chain code with the primary key and awaits the receipt
        Args:
            trx_hash: Transformed dictionary of all properties relevant for call to chain code

        Returns: transaction receipt confirming the successful write to the ledger

        """

        # transaction is signed with private key
        signed_transaction = self.__web3.eth.account.sign_transaction(trx_hash, private_key=self.__private_key)

        # confirmation that transaction was passed from non-validator node to validator nodes
        executed_transaction = self.__web3.eth.send_raw_transaction(signed_transaction.rawTransaction)

        # non-validator node awaited the successful validation by validation nodes and returns receipt
        transaction_receipt = self.__web3.eth.wait_for_transaction_receipt(executed_transaction)

        return transaction_receipt

    @retry(Exception, tries=3, delay=4)
    def get_stored_strings_from_ledger(self) -> list:
        """
        Reads all strings stored by chain code
        :return: list of str
        """

        # Call public 'view' method of chain code
        str_lst = self.__contract_obj.functions.getStrList().call({
            "from": self.__acc_address
        })

        print(f"Blockchain: getStrList => {str_lst}")
        return str_lst

    def post_string_to_ledger(self, word: str) -> json:
        """
        Push string to list on chain code
        :param word: single string
        :return: json of transaction receipt
        """
        unsigned_trx = self.__contract_obj.functions.addStr(word).build_transaction(
            {
                "chainId": self.__web3.eth.chain_id,
                "from": self.__acc_address,
                "nonce": self.__web3.eth.get_transaction_count(
                    self.__web3.to_checksum_address(self.__acc_address)
                ),
                "gasPrice": self.__web3.to_wei("1", "gwei")
            }
        )

        # sign transaction with primary key and execute
        conf = self.__sign_and_deploy(unsigned_trx)

        # convert response from chain code to json
        json_response = self.__web3.to_json(conf)

        print(f"Blockchain: added '{word}' to lst on blockchain")
        return json_response

    def __testing(self) -> None:
        """
        Iterative testing of all provided methods. Can be executed multiple times.
        :return: None
        """

        for word, iteration in zip(enumerate(["uff", "here", "are", "a", "few", "words"])):

            print("*" * 50, f"BLOCKCHAIN TESTING: iteration {iteration}", "*" * 50)
            start = time.time()

            # push word to chain code
            self.post_string_to_ledger(word)

            # request all words stored on chain code
            self.get_stored_strings_from_ledger()

            # request balance from Non-Validator Node
            self.verify_balance()

            print(f"BLOCKCHAIN: iteration {iteration} finished after {round(time.time() - start, 2)}s")

        print("*" * 50, f"BLOCKCHAIN TESTING: FINISHED", "*" * 50)


if __name__ == "__main__":
    b = Blockchain()
