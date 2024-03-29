import time
import requests

from eth_account import Account
from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.middleware import geth_poa_middleware


class Blockchain:

    def __init__(self):
        self.__header = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        self.__private_key = str()
        self.__acc_address = str()
        self.__rpc_url = "http://localhost:8545"
        self.__oracle_url = "http://localhost:8081"
        self.__balance = float() # DDos protection?

        self.__wait_for_blockchain()
        self.__acc = self.__create_account()
        self.__web3 = self.__initialize_geth()
        self.__contract_obj = self.__get_contract_from_oracle()

        # TODO: remove before pushing to prod
        self.__testing()


    def __wait_for_blockchain(self):
        for _ in range(20):
            try:
                r = requests.get(
                    url=f"{self.__oracle_url}/status",
                    headers=self.__header,
                    timeout=10
                )
                if r.status_code == 200:
                    return
            except Exception as e:
                print(f"EXCEPTION: wait_for_blockchain => {e}")
                time.sleep(3)

    def __initialize_geth(self):
        web3 = Web3(Web3.HTTPProvider(self.__rpc_url))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        web3.middleware_onion.add(construct_sign_and_send_raw_middleware(self.__acc))
        web3.eth.default_account = self.__acc_address
        return web3

    def __get_contract_from_oracle(self):
        for _ in range(3):
            try:
                r = requests.get(
                    url=f"{self.__oracle_url}/getContract",
                    headers=self.__header,
                    timeout=10
                )
                if r.status_code == 200:
                    json_response = r.json()
                    print(f"Blockchain: Contract requested from oracle at address {json_response.get('address')}")
                    return self.__web3.eth.contract(
                        abi=json_response.get("abi"),
                        address=json_response.get("address")
                    )
            except Exception as e:
                print(f"EXCEPTION: get_contract_from_oracle() => {e}")
                time.sleep(2)

    def __create_account(self):
        acc = Account.create()
        web3 = Web3()
        self.__private_key = web3.to_hex(acc.key)
        self.__acc_address = web3.to_checksum_address(acc.address)
        for _ in range(3):
            try:
                r = requests.post(
                    url=f"{self.__oracle_url}/faucet",
                    json={f"address": self.__acc_address},
                    headers=self.__header,
                    timeout=10
                )
                if r.status_code == 200:
                    print(f"Blockchain: Funds successfully requested from oracle")
                    return acc
            except Exception as e:
                print(f"EXCEPTION: create_account() => {e}")
                time.sleep(2)

    def __request_balance(self):
        for _ in range(3):
            try:
                balance = self.__web3.eth.get_balance(self.__acc_address, "latest")
                balance_eth = self.__web3.from_wei(balance, "ether")
                print(f"Blockchain: Current balance of node = {balance_eth} ETH")
                return {
                    "address": self.__acc_address,
                    "balance_eth": self.__web3.from_wei(balance, "ether")
                }
            except Exception as e:
                print(f"EXCEPTION: request_balance() => {e}")
                time.sleep(2)

    def __sign_and_deploy(self, trx_hash):
        s_tx = self.__web3.eth.account.sign_transaction(trx_hash, private_key=self.__private_key)
        sent_tx = self.__web3.eth.send_raw_transaction(s_tx.rawTransaction)
        return self.__web3.eth.wait_for_transaction_receipt(sent_tx)

    def push_opinion(self, ip_address: str, opinion: int):
        for _ in range(3):
            try:
                unsigned_trx = self.__contract_obj.functions.rateNeighbor(ip_address, opinion).build_transaction(
                    {
                        "chainId": self.__web3.eth.chain_id,
                        "from": self.__acc_address,
                        "nonce": self.__web3.eth.get_transaction_count(
                            self.__web3.to_checksum_address(self.__acc_address)
                        ),
                        "gasPrice": self.__web3.to_wei("1", "gwei")
                    }
                )
                conf = self.__sign_and_deploy(unsigned_trx)
                json_reponse = self.__web3.to_json(conf)
                print(f"Blockchain: Rating {ip_address} with {opinion}")
                return json_reponse
            except Exception as e:
                print(f"EXCEPTION: push_opinion({ip_address}, {opinion}) => {e}")
                time.sleep(2)

    def get_reputation(self, ip_address: str) -> int:
        for _ in range(3):
            try:
                reputation = self.__contract_obj.functions.getReputation(ip_address).call({
                    "from": self.__acc_address,
                    "gasPrice": self.__web3.to_wei("1", "gwei")
                })
                scaled_reputation = int(reputation / 100)
                print(f"Blockchain: Reputation of {ip_address} = {scaled_reputation}%")
                return scaled_reputation
            except Exception as e:
                print(f"EXCEPTION: get_reputation({ip_address}) => {e}")
                time.sleep(2)

    def get_raw_reputation(self, ip_address: str) -> list:
        for _ in range(3):
            try:
                numbers = self.__contract_obj.functions.getLastBasicReputation(ip_address).call({
                    "from": self.__acc_address,
                    "gasPrice": self.__web3.to_wei("1", "gwei")
                })
                print(f"Blockchain: Raw reputation of {ip_address} = {numbers}")
                return numbers
            except Exception as e:
                print(f"EXCEPTION: get_raw_reputation({ip_address}) => {e}")
                time.sleep(2)

    def debug_getStrLst(self) -> list:
        for _ in range(3):
            try:
                strLst = self.__contract_obj.functions.getStrLst().call({
                    "from": self.__acc_address,
                    "gasPrice": self.__web3.to_wei("1", "gwei")
                })
                print(f"Blockchain: getStrLst => {strLst}")
                return strLst
            except Exception as e:
                print(f"EXCEPTION: debug_getStrLst() => {e}")
                time.sleep(2)

    def debug_addStr(self, string):
        for _ in range(3):
            try:
                unsigned_trx = self.__contract_obj.functions.addStr(string).build_transaction(
                    {
                        "chainId": self.__web3.eth.chain_id,
                        "from": self.__acc_address,
                        "nonce": self.__web3.eth.get_transaction_count(
                            self.__web3.to_checksum_address(self.__acc_address)
                        ),
                        "gasPrice": self.__web3.to_wei("1", "gwei")
                    }
                )
                conf = self.__sign_and_deploy(unsigned_trx)
                json_reponse = self.__web3.to_json(conf)
                print(f"Blockchain: added '{string}' to lst on blockchain")
                return json_reponse
            except Exception as e:
                print(f"EXCEPTION: debug_addStr({string}) => {e}")
                time.sleep(2)

    def __testing(self):
        for opinion, iteration in zip([22, 45, 98, 7, 68, 14, 79, 54, 33, 83], range(10)):

            print("*"*50, f"BLOCKCHAIN TESTING: iteration {iteration}", "*"*50, flush=True)
            start = time.time()
            ip = f"192.168.0.{iteration % 5}"

            self.debug_addStr(str(iteration % 5))
            self.debug_getStrLst()
            self.push_opinion(ip, opinion)
            self.__request_balance()
            self.get_reputation(ip)
            self.get_raw_reputation(ip)

            print(f"BLOCKCHAIN: iteration {iteration} finished after {round(time.time() - start, 2)}s", flush=True)

        print("*" * 50, f"BLOCKCHAIN TESTING: FINISHED", "*" * 50, flush=True)


if __name__ == "__main__":
    b = Blockchain()
