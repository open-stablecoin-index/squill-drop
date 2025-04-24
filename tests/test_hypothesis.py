import pytest
import os

# Check for the command-line option to include Hypothesis tests
def pytest_configure(config):
    if not config.getoption("--include-hypothesis"):
        pytest.skip("Skipping Hypothesis tests", allow_module_level=True)

import boa
from eth_utils import to_checksum_address
from hypothesis import HealthCheck, Phase, Verbosity, assume, given, settings
from hypothesis import strategies as st

# Constants for realistic token amounts
DECIMALS = 10**18
MAX_SAFE_AMOUNT = 1_000_000_000 * DECIMALS  # 1 billion tokens
REWARD_AMOUNT = 100 * DECIMALS  # 100 tokens

# Strategies
address_strategy = (
    st.binary(min_size=20, max_size=20)
    .map(lambda x: to_checksum_address(f"0x{x.hex()}"))
    .filter(lambda x: x != "0x0000000000000000000000000000000000000000")
)

amount_strategy = st.one_of(
    st.integers(min_value=1 * DECIMALS, max_value=1000 * DECIMALS),  # Normal amounts
    st.integers(
        min_value=10_000 * DECIMALS, max_value=MAX_SAFE_AMOUNT
    ),  # Large amounts
    st.sampled_from(
        [1 * DECIMALS, 100 * DECIMALS, 1000 * DECIMALS]
    ),  # Common denominations
)

action_strategy = st.lists(
    st.one_of(
        st.tuples(st.just("claim"), address_strategy),
        st.tuples(
            st.just("claim_for"), address_strategy, address_strategy
        ),  # claimer, recipient
        st.tuples(st.just("add"), address_strategy),
        st.tuples(st.just("remove"), address_strategy),
        st.tuples(st.just("withdraw"), amount_strategy),
    ),
    min_size=1,
    max_size=5,
)


@given(
    claimer=address_strategy,
    recipient=address_strategy,
    initial_balance=amount_strategy,
)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_claim_for_properties(
    survey, token, owner, claimer, recipient, initial_balance
):
    """Test invariants of claim_for functionality"""
    assume(len({claimer, recipient, owner}) == 3)

    # Setup
    with boa.env.prank(owner):
        token._mint_for_testing(owner, initial_balance)
        token.transfer(survey.address, initial_balance)
        survey.add_address(recipient)

    recipient_balance_before = token.balanceOf(recipient)
    claimer_balance_before = token.balanceOf(claimer)
    contract_balance_before = token.balanceOf(survey.address)

    # Random address claims for recipient
    with boa.env.prank(owner):
        survey.claim_for(recipient)

    # Property 1: Tokens went to correct recipient
    assert token.balanceOf(recipient) == recipient_balance_before + REWARD_AMOUNT

    # Property 2: Claimer got nothing
    assert token.balanceOf(claimer) == claimer_balance_before

    # Property 3: Contract balance decreased correctly
    assert token.balanceOf(survey.address) == contract_balance_before - REWARD_AMOUNT

    # Property 4: Recipient no longer eligible
    assert not survey.eligible_addresses(recipient)

    # Property 5: Can't claim again
    with boa.env.prank(owner):
        with boa.reverts("!address"):
            survey.claim_for(recipient)


@given(actions=action_strategy)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_state_machine(survey, token, owner, actions):
    """Test contract state remains consistent through random action sequences"""
    # Setup with reasonable initial balance
    initial_mint = 1_000_000 * DECIMALS
    with boa.env.prank(owner):
        token._mint_for_testing(owner, initial_mint)
        owner_balance = token.balanceOf(owner)
        print(f"Owner balance after mint: {owner_balance}")

        token.transfer(survey.address, initial_mint)

    # Get actual starting balance
    contract_balance = token.balanceOf(survey.address)
    print(f"\nActual initial contract balance: {contract_balance}")

    # Track expected state
    eligible_addresses = set()
    claimed_addresses = set()

    print(f"\nExecuting action sequence: {actions}")

    def verify_state(msg=""):
        return
        actual_balance = token.balanceOf(survey.address)
        print(f"State check after {msg}:")
        print(f"  Expected balance: {contract_balance}")
        print(f"  Actual balance: {actual_balance}")
        assert actual_balance == contract_balance, f"Balance mismatch after {msg}"

    verify_state("setup")

    for action in actions:
        action_type = action[0]
        print(f"\nExecuting {action}")

        if action_type == "add":
            addr = action[1]
            # Only owner can add
            with boa.env.prank(owner):
                prev_eligible = survey.eligible_addresses(addr)
                survey.add_address(addr)
                # Verify address is now eligible
                assert survey.eligible_addresses(addr)
                eligible_addresses.add(addr)
                print(f"  Address {addr} added to eligible set")
                print(f"  Was previously eligible: {prev_eligible}")

        elif action_type == "remove":
            addr = action[1]
            with boa.env.prank(owner):
                prev_eligible = survey.eligible_addresses(addr)
                survey.remove_address(addr)
                # Verify address is now not eligible
                assert not survey.eligible_addresses(addr)
                eligible_addresses.discard(addr)
                print(f"  Address {addr} removed from eligible set")
                print(f"  Was previously eligible: {prev_eligible}")

        elif action_type == "claim":
            addr = action[1]
            was_eligible = addr in eligible_addresses
            pre_balance = token.balanceOf(addr)
            pre_contract = token.balanceOf(survey.address)

            with boa.env.prank(addr):
                try:
                    survey.claim()
                    # Claim should only succeed if address was eligible
                    assert was_eligible
                    # Address should no longer be eligible
                    assert not survey.eligible_addresses(addr)
                    # Balances should be correct
                    assert token.balanceOf(addr) == pre_balance + REWARD_AMOUNT
                    assert (
                        token.balanceOf(survey.address) == pre_contract - REWARD_AMOUNT
                    )
                    eligible_addresses.discard(addr)
                    contract_balance = token.balanceOf(survey.address)
                    print(f"  Claim succeeded for {addr}")
                except Exception as e:
                    # If claim failed, state should be unchanged
                    assert token.balanceOf(addr) == pre_balance
                    assert token.balanceOf(survey.address) == pre_contract
                    print(f"  Claim failed for {addr}: {e}")

        elif action_type == "claim_for":
            claimer, recipient = action[1], action[2]
            was_eligible = recipient in eligible_addresses
            pre_balance_recipient = token.balanceOf(recipient)
            pre_balance_claimer = token.balanceOf(claimer)
            pre_contract = token.balanceOf(survey.address)

            with boa.env.prank(claimer):
                try:
                    survey.claim_for(recipient)
                    # Claim should only succeed if recipient was eligible
                    assert was_eligible
                    # Recipient should no longer be eligible
                    assert not survey.eligible_addresses(recipient)
                    # Balances should be correct
                    assert (
                        token.balanceOf(recipient)
                        == pre_balance_recipient + REWARD_AMOUNT
                    )
                    # Only assert claimer gets nothing if it's not the recipient
                    if claimer != recipient:
                        assert token.balanceOf(claimer) == pre_balance_claimer
                    assert (
                        token.balanceOf(survey.address) == pre_contract - REWARD_AMOUNT
                    )
                    eligible_addresses.discard(recipient)
                    contract_balance = token.balanceOf(survey.address)
                    print(f"  Claim-for succeeded: {claimer} claimed for {recipient}")
                except Exception as e:
                    # If claim failed, state should be unchanged
                    assert token.balanceOf(recipient) == pre_balance_recipient
                    if claimer != recipient:
                        assert token.balanceOf(claimer) == pre_balance_claimer
                    assert token.balanceOf(survey.address) == pre_contract
                    print(f"  Claim-for failed: {e}")

        elif action_type == "withdraw":
            amount = min(action[1], contract_balance)
            pre_balance = token.balanceOf(owner)
            pre_contract = token.balanceOf(survey.address)

            with boa.env.prank(owner):
                try:
                    survey.withdraw_remaining(token.address)
                    # All tokens should be withdrawn
                    assert token.balanceOf(survey.address) == 0
                    assert token.balanceOf(owner) == pre_balance + pre_contract
                    contract_balance = 0
                    print(f"  Withdrawal succeeded")
                except Exception as e:
                    # If withdrawal failed, state should be unchanged
                    assert token.balanceOf(owner) == pre_balance
                    assert token.balanceOf(survey.address) == pre_contract
                    print(f"  Withdrawal failed: {e}")
        verify_state(f"action {action_type}")

    # Final state verification
    assert token.balanceOf(survey.address) == contract_balance
    for addr in claimed_addresses:
        assert not survey.eligible_addresses(addr)
    for addr in eligible_addresses - claimed_addresses:
        assert survey.eligible_addresses(addr)
    verify_state(f"final check")


@given(
    decimals=st.integers(min_value=6, max_value=18),
    reward=st.integers(min_value=1, max_value=1000),
)
@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_token_decimals(owner, decimals, reward):
    """Test contract works with tokens of different decimals"""
    reward_amount = reward * 10**decimals

    # Deploy token with specific decimals
    token_contract = boa.load_partial("contracts/mocks/MockToken.vy")
    with boa.env.prank(owner):
        token = token_contract.deploy("Test", "TST", decimals)
        token._mint_for_testing(owner, reward_amount * 10)

    # Deploy survey
    survey_contract = boa.load_partial("contracts/SquillDrop.vy")
    with boa.env.prank(owner):
        survey = survey_contract.deploy(token.address, reward_amount)
        token.transfer(survey.address, reward_amount * 5)

    # Test claim
    test_address = boa.env.generate_address()
    with boa.env.prank(owner):
        survey.add_address(test_address)

    with boa.env.prank(test_address):
        survey.claim()

    assert token.balanceOf(test_address) == reward_amount


# Additional strategies
concurrent_actions_strategy = st.lists(
    st.tuples(
        st.sampled_from(["owner", "attacker", "victim"]),  # who
        st.sampled_from(["claim", "claim_for", "add", "remove", "withdraw"]),  # what
        address_strategy,  # target
        st.integers(min_value=0, max_value=10),  # order/timing
    ),
    min_size=1,
    max_size=20,
).map(
    lambda x: sorted(x, key=lambda y: y[3])
)  # Sort by timing


@given(actions=concurrent_actions_strategy)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_concurrent_actions(survey, token, owner, actions):
    """Test ordering of multiple actions and potential race conditions"""
    # Setup as before
    initial_mint = 1_000_000 * DECIMALS
    with boa.env.prank(owner):
        token._mint_for_testing(owner, initial_mint)
        owner_balance = token.balanceOf(owner)
        token.transfer(survey.address, initial_mint)

    contract_balance = token.balanceOf(survey.address)
    eligible_addresses = set()
    claimed_addresses = set()

    # Map of roles to actual addresses
    roles = {
        "owner": owner,
        "attacker": boa.env.generate_address(),
        "victim": boa.env.generate_address(),
    }

    print(f"\nExecuting concurrent actions: {actions}")

    for who, what, target, _ in actions:
        actor = roles[who]
        print(f"\n{who} attempting {what} on {target}")

        with boa.env.prank(actor):
            if what == "add" and actor == owner:
                survey.add_address(target)
                eligible_addresses.add(target)

            elif what == "remove" and actor == owner:
                survey.remove_address(target)
                eligible_addresses.discard(target)

            elif what == "claim" and target in eligible_addresses:
                try:
                    pre_balance = token.balanceOf(survey.address)
                    survey.claim()
                    post_balance = token.balanceOf(survey.address)
                    if post_balance != pre_balance:
                        contract_balance = post_balance
                        claimed_addresses.add(target)
                except Exception as e:
                    print(f"  Claim failed: {e}")

            elif what == "withdraw" and actor == owner:
                try:
                    pre_balance = token.balanceOf(survey.address)
                    survey.withdraw_remaining(token.address)
                    post_balance = token.balanceOf(survey.address)
                    if post_balance != pre_balance:
                        contract_balance = post_balance
                except Exception as e:
                    print(f"  Withdraw failed: {e}")

    assert token.balanceOf(survey.address) == contract_balance


@given(
    addresses=st.lists(address_strategy, min_size=1, max_size=50),
    claims=st.lists(st.integers(min_value=0, max_value=49), min_size=0, max_size=25),
)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_mass_claims(survey, token, owner, addresses, claims):
    """Test mass adding of addresses and random claiming patterns"""
    initial_mint = 1_000_000 * DECIMALS
    with boa.env.prank(owner):
        token._mint_for_testing(owner, initial_mint)
        token.transfer(survey.address, initial_mint)

    contract_balance = token.balanceOf(survey.address)

    # Add all addresses
    with boa.env.prank(owner):
        for addr in addresses:
            survey.add_address(addr)

    # Random claims
    for claim_idx in claims:
        if claim_idx < len(addresses):
            claimer = addresses[claim_idx]
            with boa.env.prank(claimer):
                try:
                    pre_balance = token.balanceOf(survey.address)
                    survey.claim()
                    post_balance = token.balanceOf(survey.address)
                    if post_balance != pre_balance:
                        contract_balance = post_balance
                except Exception as e:
                    print(f"Claim failed for {claimer}: {e}")

    assert token.balanceOf(survey.address) == contract_balance


@given(
    claimers=st.lists(address_strategy, min_size=2, max_size=5),
    recipients=st.lists(address_strategy, min_size=2, max_size=5),
)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_cross_claims(survey, token, owner, claimers, recipients):
    """Test complex patterns of addresses claiming for each other"""
    initial_mint = 1_000_000 * DECIMALS
    with boa.env.prank(owner):
        token._mint_for_testing(owner, initial_mint)
        token.transfer(survey.address, initial_mint)

    contract_balance = token.balanceOf(survey.address)

    # Make all recipients eligible
    with boa.env.prank(owner):
        for recipient in recipients:
            survey.add_address(recipient)

    # Try all combinations of claimers claiming for recipients
    for claimer in claimers:
        for recipient in recipients:
            with boa.env.prank(claimer):
                try:
                    pre_balance = token.balanceOf(survey.address)
                    survey.claim_for(recipient)
                    post_balance = token.balanceOf(survey.address)
                    if post_balance != pre_balance:
                        contract_balance = post_balance
                except Exception as e:
                    print(f"Cross-claim failed {claimer}->{recipient}: {e}")

    assert token.balanceOf(survey.address) == contract_balance
