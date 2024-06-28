
# GethWizard

🎉 This repository contains a basic implementation for a fully autonomous deployment of a Geth blockchain network. 🎮

[![GitHub issues](https://img.shields.io/github/issues/Altishofer/GethWizard.svg)](https://github.com/Altishofer/GuessMyWord/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/Altishofer/GethWizard.svg)](https://github.com/Altishofer/GuessMyWord/pulls)

The instructions below will guide you on how to set up and run the project locally.

## Features

- Simple generation of docker-compose.yml
- Deploys by default
  - one bootnode
  - one oracle (rest api)
  - three validator nodes (PoA)
  - one non-validator node (rpc api)
- Randomly generated accounts(pk, address, password) with each deployment
- Randomly generated ip-addresses and ports (for nodes without API)
- Many templates for oracle and external clients

## Prerequisites

Before getting started, make sure you have the following prerequisites:

- [Docker-Desktop V4.26.0](https://docs.docker.com/desktop/release-notes/#4260) 
- [Python V3.11](https://www.python.org/downloads/release/python-3114/)


## Installation

Follow these steps to set up the project:

1. Install dependencies
2. Start Docker-Desktop
3. Clone the repository (Windows:use CMD, not powershell)

   ```shell
   git clone https://github.com/Altishofer/GethWizard.git
   ```

4. Change into the cloned repository directory:

   ```shell
   cd GethWizard
   ```

5. Create a virtual environment
   ```shell
   python3.11 -m venv venv
   ```
   
6. Activate the virtual environment
   - Windows:
     ```shell
     venv\Scripts\activate
     ```
   - Linux & MacOS:
     ```shell
     source venv/bin/activate
     ```

7. Install project dependencies:

   ```shell
   pip install -r requirements.txt
   ```

8. Start the blockchain:

   ```shell
   python blockchain_deployer.py
   
   ```
- ✔️ Network chainnet <span style="color:green">created</span>
- ✔️ Container boot <span style="color:green">started</span>
- ✔️ Container oracle <span style="color:green">started</span>
- ✔️ Container rpc <span style="color:green">started</span>
- ✔️ Container validator_0 <span style="color:green">started</span>
- ✔️ Container validator_1 <span style="color:green">started</span>
- ✔️ Container validator_2 <span style="color:green">started</span>



9. Simulate an external service interacting with the chaincode 🎉
   ```shell
   python3 client.py
   ```
# Interaction & Debugging

## Metamask
- **Add New Blockchain on Metamask**:
  - Open Metamask and click on the network dropdown.
  - Select "Custom RPC" and enter the following URL: `http://localhost:8545`.
  - Click "Save" to add the new blockchain.

- **Load Wallet Address with Tokens**:
  - Make a POST request to `http://localhost:8081/faucet` with the following JSON body:
    ```json
    {
      "address": "<hexAddress>"
    }
    ```
  - Replace `<hexAddress>` with the actual wallet address.

## Remix
- **Connect Metamask to Remix**:
  - Open Remix and connect your Metamask wallet.
  - Set advanced compiler configurations:
    - EMV version: Paris
    - Compiler: 0.8.22
  - Compile `chaincode.sol`.

- **Get Deployed Contract Address**:
  - Make a GET request to `http://localhost:8081/contract` to retrieve the address of the deployed contract.
  - Provide Remix with this contract address to interact with it.
## Postman

### Ethereum (RPC):
- Use Postman to make RPC calls via `http://localhost:8545`.
- Example for getting block count:
  - URL: http://localhost:8545
  - Body (raw):
    ```json
    {
      "jsonrpc": "2.0",
      "method": "eth_getTransactionCount",
      "id": 280,
      "params": []
    }
    ```

### Oracle (REST):
- Use Postman to interact with REST endpoints via `http://localhost:8081`.
- Example for requesting 500 ETH to an address:
  - URL: http://localhost:8081/faucet
  - Body (raw):
    ```json
    {
      "address": "<hexAddress>"
    }
    ```

