# @version 0.4.0

"""
@title Squid Pro Quo: Independence, Life & Liberty ($SQUILL) Airdrop
@notice Airdrop Round 3
@license MIT
@author Open Stable Index
@dev Forked from https://curve.substack.com/p/big-crypto-poll-results,
     details at https://github.com/open-stablecoin-index/squill-drop 

                                                                     -++++-
                                                                     #####+
                                                                     #####+
                                                        -+++++-      #####+
                                                        +######-     #####+
                                                        +######+     #####+
                                                        +#######-    #####+
                                                        +#######+    #####+
                                      +#############+   +########-   #####+
                                      +#############+   +########+   #####+
                                      +##############-  +#########   #####+
                                      +#####-           +#########+  #####+
                     +##########-     +#####-           +##########  #####+
                     +############+   +#####-           +#####+####+ #####+
                     +#############+  +#####-           +#####-#####-#####+
                     +####-   +####+  +#####-           +##### #####++####+
                     +####-   -#####  +############+    +##### -#####+####+
        -#######+    +####-   -#####  +############+    +#####  +#########+
       +##########-  +####-   +#####  +############+    +#####  -#########+
      +####   +###+  +####+--+#####+  +#####-           +#####   +########+
      +###+   -###+  +############+   +#####-           +#####   +########+
      +###+    ###+  +###########+    +#####-           +#####    +#######+
      +###+    ###+  +####----        +#####-           +#####    +#######+
      +###+   -###+  +####-           +#####-           +#####     +######+
      +###+   +###+  +####-           +##############-  +#####      ######+
       +##########   +####-           +##############-  +#####      +#####+
        -#######-    +####-           +##############-  +#####       #####+

"""

from ethereum.ercs import IERC20

import ownable_2step as ownable
import pausable


# ================================================================== #
# ⚙️ Modules
# ================================================================== #

initializes: ownable
exports: (
    ownable.owner,
    ownable.pending_owner,
    ownable.transfer_ownership,
    ownable.accept_ownership,
)

initializes: pausable[ownable := ownable]
exports: (
    pausable.paused,
    pausable.pause,
    pausable.unpause,
)


# ================================================================== #
# 📣 Events
# ================================================================== #

event Claim:
    user: address
    value: uint256


# ================================================================== #
# 💾 Storage
# ================================================================== #

reward_token: public(IERC20)
eligible_addresses: public(HashMap[address, uint256])


# ================================================================== #
# 🚧 Constructor
# ================================================================== #

@deploy
def __init__(reward_token: IERC20):
    ownable.__init__()
    pausable.__init__()
    self.reward_token = reward_token


# ================================================================== #
# 👀 View Functions
# ================================================================== #

@external
@view
def pending_claim_amount(addr: address) -> uint256:
    """
    @notice Pending claim amount
    @param addr Address to check
    @return Amount of tokens received on claim
    """
    if self.eligible_addresses[addr] > 0:
        return self.eligible_addresses[addr]
    return 0


# ================================================================== #
# ✍️ Write Functions
# ================================================================== #

@external
def claim():
    """
    @notice Allows whitelisted addresses to withdraw tokens
    """
    self._claim(msg.sender)


@external
def claim_for(addr: address):
    """
    @notice Allows whitelisted addresses to withdraw tokens
    @param addr Eligible address for claim
    """
    ownable._check_owner()
    self._claim(addr)


# ================================================================== #
# 👑 Admin Functions
# ================================================================== #

@external
def add_address(addr: address, claim_value: uint256):
    """
    @notice Adds an address to the whitelist
    @param addr Address to add
    """

    ownable._check_owner()
    self.eligible_addresses[addr] = claim_value


@external
def remove_address(addr: address):
    """
    @notice Removes an address from the whitelist
    @param addr Address to remove
    """
    ownable._check_owner()
    self.eligible_addresses[addr] = 0


@external
def withdraw_remaining(_token: IERC20):
    """
    @notice Allows owner to withdraw any remaining tokens
    @param _token Token address to withdraw
    """
    ownable._check_owner()
    amount: uint256 = staticcall _token.balanceOf(self)
    assert amount > 0, "!balance"
    assert extcall _token.transfer(msg.sender, amount), "!transfer"


@external
def add_bulk_addresses(
    addrs: DynArray[address, 10000], claim_values: DynArray[uint256, 10000]
):
    """
    @notice Bulk-add up to 10000 addresses with their claim amounts
    @param addrs         Array of recipient addresses
    @param claim_values  Array of claim values (same length as `addrs`)
    """
    ownable._check_owner()
    assert len(addrs) == len(claim_values), "len mismatch"

    for i: uint256 in range(10000):
        if i >= len(addrs):
            break
        self.eligible_addresses[addrs[i]] = claim_values[i]


# ================================================================== #
# 🏠 Internal Functions
# ================================================================== #

@internal
def _claim(_user: address):
    pausable._check_unpaused()
    assert self.eligible_addresses[_user] > 0, "!address"

    _amount: uint256 = self.eligible_addresses[_user]
    _balance: uint256 = staticcall self.reward_token.balanceOf(self)
    assert _balance >= _amount, "!balance"

    # Update state before transfer
    self.eligible_addresses[_user] = 0

    # Transfer tokens to the caller
    assert extcall self.reward_token.transfer(_user, _amount), "!transfer"

    log Claim(_user, _amount)
