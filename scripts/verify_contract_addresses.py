#!/usr/bin/env python3

"""
Verify that the addresses and amounts in the SquillDrop.vy contract match 
those in airdrop_balances.json.
"""

import json
import re
from web3 import Web3
import os
import sys
from dotenv import load_dotenv
import boa

def parse_json_with_comments(file_path):
    """Load address-amount pairs from a JSON file with potential comments."""
    try:
        with open(file_path, "r") as f:
            content = f.read()
            
            # Parse the addresses and amounts, ignoring commented out lines
            pattern = r'\["(0x[a-fA-F0-9]+)", "(\d+)"\]'
            commented_pattern = r'//\["(0x[a-fA-F0-9]+)", "(\d+)"\]'
            
            # First identify commented addresses
            commented_addresses = set()
            for match in re.finditer(commented_pattern, content):
                commented_addresses.add(match.group(1).lower())
                
            # Then get non-commented addresses
            active_data = {}
            for match in re.finditer(pattern, content):
                address = match.group(1)
                amount = match.group(2)
                if address.lower() not in commented_addresses:
                    # Store with checksum address as key
                    active_data[Web3.to_checksum_address(address)] = amount
                    
            return active_data
    except FileNotFoundError:
        raise

def extract_whitelist_from_contract():
    """Read the eligible_addresses from the deployed contract."""
    # Read contract ABI and address from environment or pass directly
    load_dotenv()
    
    # Choose network - adjust as needed
    RPC_URL = os.getenv("RPC_URL", "https://rpc.frax.com")  # Default to FRAXTAL if not specified
    
    try:
        print(f"Connecting to {RPC_URL}...")
        # Connect to network using boa
        boa.set_env(boa.env.fork(RPC_URL))
        
        # Load contract
        airdrop_address = os.getenv("AIRDROP_CONTRACT")
        if not airdrop_address:
            print("No contract address found. Please specify AIRDROP_CONTRACT in .env file or as environment variable")
            sys.exit(1)
            
        print(f"Loading contract at {airdrop_address}...")
        airdrop = boa.load_partial("contracts/SquillDrop.vy").at(airdrop_address)
        
        # Extract whitelist information
        contract_whitelist = {}
        
        # Get eligible addresses - this is a simplified approach
        # You might need to use events or other methods depending on how the contract data is accessible
        print("Extracting eligible addresses from contract...")
        
        # This part would need adjustment based on actual contract structure
        # We're using the contract's public mapping to query each address in our expected list
        
        return contract_whitelist
        
    except Exception as e:
        print(f"Error connecting to contract: {str(e)}")
        return {}

def parse_vyper_whitelist():
    """Parse the _whitelist() function in SquillDrop.vy to extract addresses and amounts."""
    try:
        with open("contracts/SquillDrop.vy", "r") as f:
            content = f.read()
            
            # Find the _whitelist function section
            whitelist_section = re.search(r'@internal\s+def\s+_whitelist\(\):\s+(.*?)(?=\n\n|\Z)', 
                                          content, re.DOTALL)
            
            if not whitelist_section:
                raise Exception("Could not find _whitelist function in contract")
                
            whitelist_content = whitelist_section.group(1)
            
            # Extract address-amount pairs
            pattern = r'self\.eligible_addresses\[(0x[a-fA-F0-9]+)\]\s+=\s+(\d+)'
            address_amounts = {}
            
            for match in re.finditer(pattern, whitelist_content):
                address = Web3.to_checksum_address(match.group(1))
                amount = match.group(2)
                address_amounts[address] = amount
                
            return address_amounts
    except Exception as e:
        print(f"Error parsing contract: {str(e)}")
        return {}

def main():
    # Load addresses from the JSON file
    v2_addresses = parse_json_with_comments("scripts/airdrop_balances.json")
    print(f"Loaded {len(v2_addresses)} addresses from airdrop_balances.json")
    
    # Parse the contract whitelist
    contract_addresses = parse_vyper_whitelist()
    print(f"Found {len(contract_addresses)} addresses in SquillDrop.vy contract")
    
    # Compare the two lists
    json_addresses_not_in_contract = []
    contract_addresses_not_in_json = []
    amount_mismatches = []
    
    # Check if all JSON addresses are in contract with matching amounts
    for addr, json_amount in v2_addresses.items():
        if addr not in contract_addresses:
            json_addresses_not_in_contract.append(addr)
        elif contract_addresses[addr] != json_amount:
            amount_mismatches.append({
                "address": addr,
                "json_amount": json_amount,
                "contract_amount": contract_addresses[addr]
            })
    
    # Check if all contract addresses are in JSON
    for addr in contract_addresses:
        if addr not in v2_addresses:
            contract_addresses_not_in_json.append(addr)
    
    # Report results
    if not json_addresses_not_in_contract and not contract_addresses_not_in_json and not amount_mismatches:
        print("\n✅ SUCCESS: All addresses and amounts match between airdrop_balances.json and the contract!")
    else:
        print("\n❌ Verification failed! Discrepancies found:")
        
        if json_addresses_not_in_contract:
            print(f"\n{len(json_addresses_not_in_contract)} addresses in JSON but not in contract:")
            for addr in json_addresses_not_in_contract:
                print(f"  - {addr}")
        
        if contract_addresses_not_in_json:
            print(f"\n{len(contract_addresses_not_in_json)} addresses in contract but not in JSON:")
            for addr in contract_addresses_not_in_json:
                print(f"  - {addr}")
        
        if amount_mismatches:
            print(f"\n{len(amount_mismatches)} amount mismatches:")
            for mismatch in amount_mismatches:
                print(f"  - {mismatch['address']}:")
                print(f"    JSON: {mismatch['json_amount']}")
                print(f"    Contract: {mismatch['contract_amount']}")
    
    # Generate summary report
    report = {
        "total_addresses_v2_json": len(v2_addresses),
        "total_addresses_contract": len(contract_addresses),
        "addresses_in_json_not_in_contract": json_addresses_not_in_contract,
        "addresses_in_contract_not_in_json": contract_addresses_not_in_json,
        "amount_mismatches": amount_mismatches
    }
    
    with open("scripts/verification_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed verification report saved to scripts/verification_report.json")

if __name__ == "__main__":
    main() 
