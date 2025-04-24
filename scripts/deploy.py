import os

import boa
from dotenv import load_dotenv
from helpers import get_constructor_arguments, save_deployment_info
from load_account import load_account

# Configuration
FORK = True
NETWORK = "ETHEREUM"

# Load environment variables
load_dotenv()
ETHERSCAN_KEY = os.getenv("ETHERSCAN_API_KEY")
ETHERSCAN_API = os.getenv("ETHERSCAN_API")
RPC_URL = f"https://eth-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"

# Main deployment logic
if FORK:
    boa.fork(RPC_URL)
    token_contract = boa.load_partial("contracts/mocks/MockToken.vy")
    reward = token_contract.deploy("Test Token", "TEST", 18)
    reward._mint_for_testing(boa.env.eoa, 1_776_000 * 10**18)
    print(f"Minted {boa.env.eoa} {reward.balanceOf(boa.env.eoa)/10**18:,.2f}")

    REWARD_TOKEN = reward.address
else:
    REWARD_TOKEN = "0x7ebab7190d3d574ce82d29f2fa1422f18e29969c"
    boa.set_network_env(RPC_URL)

    # Set up network and load account
    acct = load_account()
    boa.env.add_account(acct)

    reward = boa.from_etherscan(REWARD_TOKEN, "Token", ETHERSCAN_API, ETHERSCAN_KEY)

print(
    f"Loaded reward token {reward.name()} (${reward.symbol()})\nTotal Supply: {reward.totalSupply() / 10**18:,.2f}"
)

# Deploy contract
print(f"\nDeploying with reward token {REWARD_TOKEN}")
reward_contract = boa.load_partial("contracts/SquillDrop.vy")
airdrop = reward_contract.deploy(REWARD_TOKEN)
print(f"Deployed to {airdrop.address}\n")

try:
    constructor_args = get_constructor_arguments(REWARD_TOKEN)
    print(f"Constructor Arguments Bytecode: {constructor_args}")

    # Save deployment info
    deployment_params = {
        "reward_token": REWARD_TOKEN,
        "reward_amount": 0,  # To be updated when distributing rewards
    }

    save_deployment_info(
        network=NETWORK,
        contract_address=airdrop.address,
        constructor_args=constructor_args,
        airdrop=airdrop,
        deployment_params=deployment_params,
    )

except Exception as e:
    print(f"Exception {e}")
