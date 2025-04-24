import boa
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
INITIAL_MINT = 1_000_000 * 10**18  # 1M tokens


def test_initial_state(survey, owner, token, reward_amount):
    """Test initial contract state after deployment"""
    print(f"Testing initial state...")
    print(f"Owner: {owner}")
    print(f"Token address: {token.address}")
    print(f"Survey address: {survey.address}")

    assert survey.owner() == owner
    assert survey.reward_token() == token.address
    assert not survey.paused()

    contract_balance = token.balanceOf(survey.address)
    print(f"Contract token balance: {contract_balance}")
    assert contract_balance >= reward_amount * 10


def test_eligibility_management(survey, owner, alice, bob):
    """Test adding and removing eligible addresses"""
    print(f"Initial state - Alice eligible: {survey.eligible_addresses(alice)}")

    # Add Alice to eligible addresses
    with boa.env.prank(owner):
        survey.add_address(alice, 10 * 10 ** 18)

    assert survey.eligible_addresses(alice) == 10 * 10 ** 18
    print(f"After adding - Alice eligible: {survey.eligible_addresses(alice)}")

    # Try to add from non-owner account
    with boa.env.prank(bob):
        with boa.reverts("!owner"):
            survey.add_address(bob, 11 * 10 ** 18)

    # Remove Alice
    with boa.env.prank(owner):
        survey.remove_address(alice)

    assert not survey.eligible_addresses(alice)


def test_successful_claim(survey, owner, alice, token, reward_amount):
    """Test successful token claim process"""
    initial_balance = token.balanceOf(alice)
    initial_contract_balance = token.balanceOf(survey.address)
    print(
        f"Initial balances - Alice: {initial_balance}, Contract: {initial_contract_balance}"
    )

    # Make Alice eligible
    with boa.env.prank(owner):
        survey.add_address(alice, reward_amount)

    # Claim tokens
    with boa.env.prank(alice):
        tx = survey.claim()
        print(f"Claim transaction successful: {tx}")

    final_balance = token.balanceOf(alice)
    final_contract_balance = token.balanceOf(survey.address)
    print(
        f"Final balances - Alice: {final_balance}, Contract: {final_contract_balance}"
    )

    assert final_balance == initial_balance + reward_amount
    assert final_contract_balance == initial_contract_balance - reward_amount
    assert not survey.eligible_addresses(alice)


def test_claim_for(survey, owner, alice, bob, token, reward_amount):
    """Test claiming on behalf of another address"""
    initial_alice_balance = token.balanceOf(alice)
    initial_bob_balance = token.balanceOf(bob)
    print(
        f"Initial balances - Alice: {initial_alice_balance}, Bob: {initial_bob_balance}"
    )

    # Make Alice eligible
    with boa.env.prank(owner):
        survey.add_address(alice, reward_amount)
        print(f"Added Alice to eligible addresses")

    # Bob claims for Alice
    with boa.env.prank(owner):
        tx = survey.claim_for(alice)
        print(f"Claim-for transaction successful: {tx}")

    final_alice_balance = token.balanceOf(alice)
    final_bob_balance = token.balanceOf(bob)
    print(f"Final balances - Alice: {final_alice_balance}, Bob: {final_bob_balance}")

    assert final_alice_balance == initial_alice_balance + reward_amount
    assert final_bob_balance == initial_bob_balance
    assert not survey.eligible_addresses(alice)


def test_paused_functionality(survey, owner, alice):
    """Test pause and unpause functionality"""
    # Make Alice eligible
    with boa.env.prank(owner):
        survey.add_address(alice, 10 ** 18)
        print("Added Alice to eligible addresses")

        # Pause contract
        survey.pause()
        print("Contract paused")

    assert survey.paused()

    # Try to claim while paused
    with boa.env.prank(alice):
        with boa.reverts("paused"):
            survey.claim()

    print("Claim attempt while paused properly reverted")

    # Unpause and claim
    with boa.env.prank(owner):
        survey.unpause()
        print("Contract unpaused")

    with boa.env.prank(alice):
        tx = survey.claim()
        print(f"Claim after unpause successful: {tx}")


@given(value=st.integers(min_value=1, max_value=INITIAL_MINT))
@settings(
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None,
    max_examples=10,
)
def test_token_operations(token, owner, alice, value):
    """Property-based testing of token operations"""
    print(f"Testing with value: {value}")

    initial_balance = token.balanceOf(alice)

    with boa.env.prank(owner):
        token.transfer(alice, value)

    assert token.balanceOf(alice) == initial_balance + value
    print(f"Transfer successful. New balance: {token.balanceOf(alice)}")


def test_pending_claim_amount(survey, owner, alice, bob, reward_amount):
    """Test pending claim amount for eligible and non-eligible addresses"""
    # Initially, both Alice and Bob should have no pending claims
    assert survey.pending_claim_amount(alice) == 0
    assert survey.pending_claim_amount(bob) == 0

    # Make Alice eligible
    with boa.env.prank(owner):
        survey.add_address(alice, reward_amount)

    # Alice should now have a pending claim amount
    assert survey.pending_claim_amount(alice) == reward_amount

    # Bob should still have no pending claims
    assert survey.pending_claim_amount(bob) == 0

    # Remove Alice's eligibility
    with boa.env.prank(owner):
        survey.remove_address(alice)

    # Alice should have no pending claims again
    assert survey.pending_claim_amount(alice) == 0

    # Test an address not in the eligible_addresses mapping
    charlie = boa.env.generate_address()
    assert survey.pending_claim_amount(charlie) == 0

    # Test with a very large claim amount
    large_claim_amount = 2**256 - 1  # Maximum uint256 value
    with boa.env.prank(owner):
        survey.add_address(alice, large_claim_amount)
    assert survey.pending_claim_amount(alice) == large_claim_amount
    
    # Reset Alice's claim amount
    with boa.env.prank(owner):
        survey.remove_address(alice)


def test_whitelisted_addresses_claim_amount(survey):
    """Test pending claim amount for whitelisted addresses"""
    # Addresses and their expected claim amounts from the _whitelist function
    whitelisted_addresses = {
        "0x277FA53c8a53C880E0625c92C92a62a9F60f3f04": 76080213292372400000000,
        "0xb19d6B66b18FAE0FcA1023138B229e5F970b5180": 57998416447911600000000,
        "0xEA7d6A3873CBB644a2FA3a124b00a25C33C661b8": 33721428966839200000000,
        # Add more addresses as needed
    }

    for addr, expected_amount in whitelisted_addresses.items():
        assert survey.pending_claim_amount(addr) == expected_amount
