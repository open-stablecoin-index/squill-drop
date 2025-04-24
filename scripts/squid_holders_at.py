import boa
import time, json
LIVE = False
FRAXSCAN_KEY = os.getenv("FRAXSCAN_KEY")
FRAXSCAN_API = 	"https://api.fraxscan.com/api"
RPC_URL = "https://rpc.frax.com"

block = 18922260
boa.env.fork(RPC_URL, block_identifier=block)

with open('contract_interaction_reports/contract_interactions_20250403_004317.json', 'r') as f:
    addrs = json.load(f)


contract_addrs = {
        'squid': '0x6e58089d8E8f664823d26454f49A5A0f2fF697Fe',
        'lp': '0x277FA53c8a53C880E0625c92C92a62a9F60f3f04',
        'gauge': '0xe5E5ed1B50AE33E66ca69dF17Aa6381FDe4e9C7e',
        'convex': '0x29FF8F9ACb27727D8A2A52D16091c12ea56E9E4d'
        }

contracts = {}
for k, v in contract_addrs.items():
    contracts[k] = boa.from_etherscan(v, k, FRAXSCAN_API, FRAXSCAN_KEY)
    print(contracts[k])
    time.sleep(1)

i=0
data = {}
for addr, addr_contract_data in addrs.items():
    i += 1
    bals = {}
    for k, v in contracts.items():
        bals[k] = v.balanceOf(addr) 
    print(i, len(addrs), addr, bals)
    data[addr] = bals

output_filename = f'balance_data_{block}.json'
with open(output_filename, 'w') as f:
    json.dump(data, f, indent=2)

print(f"Data saved to {output_filename}")

