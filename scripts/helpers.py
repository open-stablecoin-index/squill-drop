import json
import subprocess
from datetime import datetime
from pathlib import Path

import yaml
from eth_abi import encode
from web3 import Web3


def get_constructor_arguments(reward_token):
    """Encode constructor arguments for contract verification"""
    w3 = Web3()

    # Convert addresses to checksum format
    reward_token = w3.to_checksum_address(reward_token)

    # Prepare the argument types and values
    types = ["address"]
    values = [reward_token]

    try:
        # Use eth_abi.encode directly
        encoded = encode(types, values)
        return "0x" + encoded.hex()
    except Exception as e:
        print(f"Encoding error: {str(e)}")
        print("Arguments:", values)
        print("Types:", types)
        return None


def get_vyper_bytecode():
    """Get the Vyper compiler output for contract verification"""
    try:
        result = subprocess.run(
            ["vyper", "-f", "solc_json", "contracts/SquillDrop.vy"],
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error getting Vyper bytecode: {e}")
        return None


def save_deployment_info(
    network: str,
    contract_address: str,
    constructor_args: str,
    airdrop,  # Contract instance
    deployment_params: dict,
):
    """Save deployment information to a YAML file with separate artifact storage"""
    # Create directory structure
    base_dir = Path("deployment")
    chain_dir = base_dir / network.lower()
    artifacts_dir = base_dir / "artifacts"

    # Create directories if they don't exist
    for dir_path in [chain_dir, artifacts_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)

    # Generate filenames
    date_str = datetime.now().strftime("%Y%m%d")
    addr_prefix = contract_address[:6].lower()
    yaml_filename = f"{date_str}_{addr_prefix}_squilldrop.yaml"
    artifact_filename = f"{date_str}_{addr_prefix}_squilldrop_vyper_output.json"

    # Save Vyper output separately
    vyper_output = get_vyper_bytecode()
    if vyper_output:
        artifact_path = artifacts_dir / artifact_filename
        with open(artifact_path, "w") as f:
            json.dump(vyper_output, f, indent=2)

    # Compile deployment data
    deployment_data = {
        "network": network,
        "contract_address": contract_address,
        "constructor_arguments": constructor_args,
        "deployment_timestamp": datetime.now().isoformat(),
        "deployment_parameters": {
            "reward_token": deployment_params["reward_token"],
            "reward_amount": deployment_params.get("reward_amount", 0),
            "total_recipients": deployment_params.get("total_recipients", 0),
        },
        "contract_state": {
            "owner": airdrop.owner() if hasattr(airdrop, "owner") else None,
        },
        "artifacts": {
            "vyper_output": f"artifacts/{artifact_filename}" if vyper_output else None
        },
    }

    # Save to YAML file
    with open(chain_dir / yaml_filename, "w") as f:
        yaml.dump(deployment_data, f, default_flow_style=False, sort_keys=False)

    print(f"\nDeployment info saved to: {chain_dir / yaml_filename}")
    if vyper_output:
        print(f"Vyper output saved to: {artifacts_dir / artifact_filename}")
