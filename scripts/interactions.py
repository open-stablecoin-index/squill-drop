import requests
import pandas as pd
import time
import json
import os
from datetime import datetime

def get_contract_interactions(contracts, api_key=None, network="fraxtal"):
    """
    Gets all addresses that have interacted with specified contracts.
    
    Args:
        contracts (list): List of contract addresses to query
        api_key (str, optional): Explorer API key
        network (str): Network to query (fraxtal, sonic, etc.)
        
    Returns:
        dict: Dictionary mapping addresses to lists of contracts they interacted with
    """
    # Select the appropriate base API URL based on network
    base_urls = {
        "fraxtal": "https://api.fraxscan.com/api",
        "sonic": "https://api.sonicscan.org/api"
    }
    
    if network.lower() not in base_urls:
        raise ValueError(f"Unsupported network: {network}. Supported networks: {', '.join(base_urls.keys())}")
    
    base_url = base_urls[network.lower()]
    
    # Initialize tracking dictionary for addresses and their interactions
    address_interactions = {}
    
    for contract_address in contracts:
        print(f"Fetching transactions for contract {contract_address} on {network}...")
        
        # Create parameters for API request
        params = {
            'module': 'account',
            'action': 'tokentx',  # token transfers
            'contractaddress': contract_address,
            'startblock': 0,
            'endblock': 999999999,
            'sort': 'desc'
        }
        
        # Add API key if provided
        if api_key:
            params['apikey'] = api_key
        
        # Initialize variables for pagination
        page = 1
        offset = 1000  # Number of results per page
        more_data = True
        contract_address_count = 0
        
        # Loop through paginated results
        while more_data:
            # Add pagination parameters
            params['page'] = page
            params['offset'] = offset
            
            try:
                # Make API request
                response = requests.get(base_url, params=params)
                data = response.json()
                
                # Check if request was successful
                if data['status'] != '1':
                    print(f"API Error: {data.get('message', 'Unknown error')}")
                    break
                
                # Process transactions
                transactions = data['result']
                
                # Break if no more transactions
                if not transactions:
                    more_data = False
                    continue
                
                if page == 1:
                    print(f"Found transactions, processing in batches...")
                
                # Extract addresses and track their interactions with this contract
                for tx in transactions:
                    from_address = tx['from']
                    to_address = tx['to']
                    
                    # Track 'from' address interactions
                    if from_address not in address_interactions:
                        address_interactions[from_address] = []
                    if contract_address not in address_interactions[from_address]:
                        address_interactions[from_address].append(contract_address)
                    
                    # Track 'to' address interactions
                    if to_address not in address_interactions:
                        address_interactions[to_address] = []
                    if contract_address not in address_interactions[to_address]:
                        address_interactions[to_address].append(contract_address)
                
                contract_address_count += len(transactions)
                
                # Move to next page
                page += 1
                
                # Add a small delay to avoid rate limiting
                time.sleep(0.3)
                
            except Exception as e:
                print(f"Error processing page {page} for contract {contract_address}: {e}")
                break
        
        print(f"Processed {contract_address_count} transactions for contract {contract_address}")
    
    total_addresses = len(address_interactions)
    print(f"Found {total_addresses} unique addresses interacting with {len(contracts)} contracts")
    
    return address_interactions

def generate_reports(address_interactions, contracts, output_dir="contract_interaction_reports"):
    """
    Generate reports from the address interaction data.
    
    Args:
        address_interactions (dict): Dictionary of addresses and their contract interactions
        contracts (list): List of contract addresses that were queried
        output_dir (str): Directory to save the reports
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Convert the data to a more usable format for reporting
    records = []
    for address, interacted_contracts in address_interactions.items():
        # Create interaction flags for each contract
        interaction_flags = {contract: (contract in interacted_contracts) for contract in contracts}
        
        # Create a record for this address
        record = {"address": address, "interaction_count": len(interacted_contracts)}
        record.update({f"interacted_with_{contract[:8]}": flag for contract, flag in interaction_flags.items()})
        record["contracts"] = ",".join(interacted_contracts)
        records.append(record)
    
    # Create a DataFrame
    df = pd.DataFrame(records)
    
    # Sort by number of interactions (descending)
    df = df.sort_values("interaction_count", ascending=False)
    
    # Save as CSV (can be easily imported)
    csv_path = f"{output_dir}/contract_interactions_{timestamp}.csv"
    df.to_csv(csv_path, index=False)
    
    # Save as JSON (useful for programmatic access)
    json_path = f"{output_dir}/contract_interactions_{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump(address_interactions, f, indent=2)
    
    # Generate summary statistics
    summary = {
        "total_unique_addresses": len(address_interactions),
        "contracts_analyzed": len(contracts),
        "contracts": contracts,
        "addresses_per_contract": {},
        "addresses_with_multiple_contracts": sum(1 for contracts in address_interactions.values() if len(contracts) > 1),
    }
    
    # Count addresses per contract
    for contract in contracts:
        count = sum(1 for interacted_contracts in address_interactions.values() if contract in interacted_contracts)
        summary["addresses_per_contract"][contract] = count
    
    # Save summary as JSON
    summary_path = f"{output_dir}/summary_{timestamp}.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    
    # Create a readable summary report
    report = f"""
CONTRACT INTERACTION REPORT
==========================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY
-------
Total Unique Addresses: {summary['total_unique_addresses']}
Contracts Analyzed: {summary['contracts_analyzed']}
Addresses With Multiple Contracts: {summary['addresses_with_multiple_contracts']}

CONTRACTS
---------
{chr(10).join([f"- {contract}: {summary['addresses_per_contract'][contract]} addresses" for contract in contracts])}

FILES GENERATED
--------------
- CSV Report: {csv_path}
- JSON Data: {json_path}
- Summary: {summary_path}
    """
    
    # Save report
    report_path = f"{output_dir}/report_{timestamp}.txt"
    with open(report_path, "w") as f:
        f.write(report)
    
    print(f"\nReports saved in directory: {output_dir}/")
    print(report)
    
    return {
        "csv_path": csv_path,
        "json_path": json_path,
        "summary_path": summary_path,
        "report_path": report_path
    }

def main():
    # Input: List of contracts to analyze
    contracts = [
        "0x6e58089d8E8f664823d26454f49A5A0f2fF697Fe",  # SQUID 
        "0x277fa53c8a53c880e0625c92c92a62a9f60f3f04",   # SQUID/ETH Pool
        "0xe5E5ed1B50AE33E66ca69dF17Aa6381FDe4e9C7e", # Gauge
        "0x29FF8F9ACb27727D8A2A52D16091c12ea56E9E4d", # Convex
        "0xbf55bb9463bbbb6ad724061910a450939e248ea6" # LL
    ]
    
    # API key (if required)
    api_key = os.getenv("FRAXSCAN_KEY")
    
    # Network to use (fraxtal or sonic)
    network = "fraxtal"
    
    try:
        # 1. Get all addresses that interacted with the contracts
        address_interactions = get_contract_interactions(
            contracts=contracts,
            api_key=api_key,
            network=network
        )
        
        # 2. Generate reports
        generate_reports(
            address_interactions=address_interactions,
            contracts=contracts,
            output_dir="contract_interaction_reports"
        )
        
    except Exception as e:
        print(f"Error in main process: {str(e)}")

if __name__ == "__main__":
    main()
