# Welcome to the SQUILL Token Airdrop!
![SQUILL Token Airdrop](https://substackcdn.com/image/fetch/w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F6cbd6acd-bf15-49cb-94fb-decb8b9c8f27_1536x1024.png)


We're pleased to release the [first phase of our airdrop](https://leviathannews.substack.com/p/leviathan-launches-squill) for "Squid Pro Quo: Independence, Life & Liberty" (aka SQUILL)

The symbolic first 1.776M of the total 10M supply of SQUILL began dropping as of April 15, 2025 -- tax day in the US.  

$SQUILL exists as the governance token for $OPEN, and the intiial phase of the airdrop targets $SQUID holders.  

A bit more on this trio of tokens:

### The Open Stablecoin Index: $OPEN

[$OPEN](https://app.reserve.org/ethereum/index-dtf/0x323c03c48660fe31186fa82c289b0766d331ce21/overview) is an onchain, equal-weight index of next-generation stablecoin networks. It's your gateway to the stablecoin multiverse, offering effortless exposure to the cutting edge of decentralized finance.

* [Details](https://leviathannews.substack.com/p/stablecoins-everyone-and-their-mom)

### The Governance Layer: $SQUILL

[$SQUILL](https://etherscan.io/token/0x7ebab7190d3d574ce82d29f2fa1422f18e29969c) governs the evolution of the OPEN index directly on mainnet, without intermediaries or committees. Holders who vote-lock into vlSQUILL shape the index and earn a share of TVL and minting fees.

* [Details](https://leviathannews.substack.com/p/leviathan-launches-squill)

### Decentralizing News: $SQUID

[$SQUID](https://fraxscan.com/token/0x6e58089d8e8f664823d26454f49a5a0f2ff697fe) is the lifeblood of [Leviathan News](https://leviathannews.xyz/), a reward, incentive, and governance asset for decentralized media. Participate in the ecosystem, and you're already earning SQUID. 

* [Details](https://leviathannews.substack.com/p/leviathan-news-squid-token-the-ultimate)


## Quick Start Guide

### Airdrop Calculation

The airdrop amounts are calculated using the `squid_holders_at.py` script, which determines the proportional distribution based on SQUID holdings. 

Having distributed SQUID fairly for contributions over the course of two years, deploying to SQUID holders is the fairest way to capture a slice of the most educated DeFi audience who focused on building throughout the bear market.

### Check Your Eligibility

1. Visit the designated blockchain explorer and connect your wallet.
2. Go to the contract: [0x17A81C3C7fD664911f00415c4F72b4dFd552053F](https://etherscan.io/address/0x17A81C3C7fD664911f00415c4F72b4dFd552053F#readContract)
3. Under "Read Contract", find the `eligible_addresses` function.
4. Enter your wallet address to check if you're eligible for the claim.

### Claim Your Reward

If you're eligible, you can claim your tokens in two ways:

#### Option 1: Through Etherscan
1. Visit the contract on the explorer: [0x17A81C3C7fD664911f00415c4F72b4dFd552053F](https://etherscan.io/address/0x17A81C3C7fD664911f00415c4F72b4dFd552053F#writeContract)
2. Connect your wallet.
3. Under "Write Contract", click `claim`.
4. Confirm the transaction in your wallet.

#### Option 2: Direct Contract Interaction
```vyper
# Call the claim function from an eligible address
function claim() external
```

**Note**: After claiming, your address will no longer be eligible for future claims.


## Technical Documentation

### Contract Overview

<em>This contract was forked from [zcor/survey-reward](https://github.com/zcor/survey-reward).  The contract is not audited, but presided over the distribution of thousands of dollars worth of rewards without incident.  However, smart contracts are dangerous, so make sure to read it carefully and use at your own risk!</em>

This contract implements a token distribution system for $SQUID holders, featuring:
- One-time token claims for whitelisted addresses.
- Owner-controlled address management.
- Pausable functionality for emergency stops.
- Two-step ownership transfer for security.

### Core Functions

```vyper
claim() external
    # Allows eligible addresses to claim their reward tokens

claim_for(addr: address) external
    # Allows claiming on behalf of eligible addresses

add_address(addr: address) external
    # Owner function to add eligible addresses

remove_address(addr: address) external
    # Owner function to remove addresses from eligibility
```

### Architecture

The contract relies on several modules:
- Ownable2Step for secure ownership management.
- Pausable module for emergency controls.
- ERC20 mock for testing.

### Security Features

1. **Access Control**
   - Owner-only functions for address management.
   - Two-step ownership transfer process.

2. **Safety Checks**
   - Balance verification before transfers.
   - Single-claim enforcement.
   - Pausable functionality for emergency situations.

3. **Anti-Griefing**
   - No loops in core functions.
   - Gas-efficient storage layout.

### Development

#### Local Setup
```bash
# Clone repository
git clone [repository_url]

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/
```

#### Testing
The contract includes comprehensive test coverage:
- Unit tests for core functionality.
- Hypothesis testing.

### Deployment

This contract is deployed on:
- Ethereum Mainnet: [0xPLACEHOLDER](#)

#### Liquidity Pools:
* Mainnet:
    * [Curve SQUILL/WETH](https://curve.fi/dex/ethereum/pools/factory-twocrypto-177/deposit/)
* Fraxtal:
    * [Fraxtal SQUID/SQUILL](https://curve.fi/dex/fraxtal/pools/factory-twocrypto-44/deposit/)


## Running Tests

### Default Test Run

By default, the test suite will run all tests except those in `tests/test_hypothesis.py`:

```bash
pytest
```

### Including Hypothesis Tests

To include the Hypothesis tests, use the `--include-hypothesis` flag:

```bash
pytest --include-hypothesis
```

This setup allows you to control the execution of the Hypothesis tests, running them only when explicitly desired.


---

Join the revolution with SQUILL and be part of a new cycle in decentralized finance. 

🦑 [OpenStablecoinIndex.com](https://openstablecoinindex.com/  )
