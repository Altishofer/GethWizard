
# GethWizard

🎉 This repository contains a basic implementation for a fully autonomous deployment of a Geth blockchain network. 🎮

[![GitHub issues](https://img.shields.io/github/issues/Altishofer/GethWizard.svg)](https://github.com/Altishofer/GuessMyWord/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/Altishofer/GethWizard.svg)](https://github.com/Altishofer/GuessMyWord/pulls)

The instructions below will guide you on how to set up and run the project locally.

## Features

- Simple generation of docker-compose.yml
- Deploys by default
  - 1 bootnode
  - 1 oracle
  - 3 validator nodes
  - 1 rpc - node
- Newly generated addresses and primary keys with each deployment
- provides many templates for oracle server and external client

## Interaction & Debugging
- see app.py in /oracle and external_service.py to see structure of requests
- Remix and Metamask
  - set url of new blockchain on Metamask: http://localhost:8545
  - call http://localhost:8081/faucet to load any wallet-address with tokens
  - Set advanced compiler configurations on remix >> EMV version >> Paris
  - Compile chaincode.sol with compiler: 0.8.22
  - call http://localhost:8081/getContract to get the randomly generated address
  - insert address into remix to deply compiled contract at address
- Postman
  - remote-procedure-calls (rpc) via http://localhost:8545
  - representational state transfer (rest) via http://localhost:8081


## Prerequisites

Before getting started, make sure you have the following prerequisites:

- [Docker-Desktop](https://docs.docker.com/desktop/release-notes/#4260)
- [Python3.11](https://www.python.org/downloads/release/python-3114/)


## Installation

Follow these steps to set up the project:

1. Install dependencies
2. Clone this repository to your local machine:
3. Start Docker-Desktop

4. Clone the repository

   ```shell
   git clone https://github.com/Altishofer/GethWizard.git
   ```

5. Change into the cloned repository directory:

   ```shell
   cd GethWizard
   ```

6. Install project dependencies:

   ```shell
   pip3 install requirements.txt
   ```

7. Start the blockchain:

   ```shell
   python3 deploy_blockchain.py
   ```

8. Simulate an external service interacting with the chaincode 🎉
   ```shell
   python3 external_service.py
   ```
