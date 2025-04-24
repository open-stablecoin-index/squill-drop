# @version 0.4.0

"""
@title Squid Pro Quo: Independence, Life & Liberty ($SQUILL) Airdrop
@notice Airdrop Round 1,
@license MIT
@author Open Stable Index
@dev Forked from https://curve.substack.com/p/big-crypto-poll-results,
     details at https://github.com/zcor/survey-reward

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
    self._whitelist()


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


@internal
def _whitelist():
    self.eligible_addresses[0x277FA53c8a53C880E0625c92C92a62a9F60f3f04] = 76080213292372400000000
    self.eligible_addresses[0xb19d6B66b18FAE0FcA1023138B229e5F970b5180] = 57998416447911600000000
    self.eligible_addresses[0xEA7d6A3873CBB644a2FA3a124b00a25C33C661b8] = 33721428966839200000000
    self.eligible_addresses[0xBd4ab1139F2F6361f927b8552C3b97Fe81f0B528] = 18195381999580300000000
    self.eligible_addresses[0x9A27E685990B1a5C7Af688f634c5107763d0B566] = 14557541077765100000000
    self.eligible_addresses[0xb51074Da03c55E79e3526cF6bBf31873443EfC63] = 13307951059362000000000
    self.eligible_addresses[0x7644e5d0AF5433dB699895a2a33A60D497578E2c] = 7429604072326770000000
    self.eligible_addresses[0x47bDcF47753fBD125Ac7A6305F550eB0362617F8] = 7109307307497270000000
    self.eligible_addresses[0xF433771bE52fe3B915b5c3840Ffe9A55425766E3] = 5719683077837390000000
    self.eligible_addresses[0xDFeeAcB43f4bdF4F952EE0E47c99353dD2eDa192] = 5470646281110560000000
    self.eligible_addresses[0x4c47b2520E9f7E3da15dF09718d467f783b03858] = 5385559914428310000000
    self.eligible_addresses[0xDa80EA0a45b1af85bB44f9e5b3BD4393A9A4D751] = 4886082426831520000000
    self.eligible_addresses[0x5ae1283093f33C5F4C1e3a4F0C97d25EC78dC51d] = 4443979442119780000000
    self.eligible_addresses[0x5D51b10000D2abe6d619b9DE4B5846785B61Ce1a] = 4075175927154810000000
    self.eligible_addresses[0x95AB2a2F6e701873cEA0070dAc735589D089f6Bc] = 3752665919800490000000
    self.eligible_addresses[0x84641137BaC4Db68DE94Ec3D2ED89acE0AA88f20] = 3715883705643630000000
    self.eligible_addresses[0x6f0f535Da243E441352A9040E556F976B935453B] = 3633219742614980000000
    self.eligible_addresses[0x3acc2BffA4a5e75Fd4B7709a6fa2C3EEd94F664C] = 3573802210953350000000
    self.eligible_addresses[0x98Ab20307fdABa1ce8b16d69d22461c6dbe85459] = 3508404822726140000000
    self.eligible_addresses[0x318d0059efE546b5687FA6744aF4339391153981] = 3486968854118930000000
    self.eligible_addresses[0x34d6Dbd097f6b739C59D7467779549Aea60e1F84] = 2952299268958550000000
    self.eligible_addresses[0xa8577Bd52403e03C61A758E535F942FFC64cd070] = 2620357393997710000000
    self.eligible_addresses[0x1b34637198B30b95a1FDd60061Fa2345F6C7aD9c] = 2517182546884500000000
    self.eligible_addresses[0xF0Ee04aF67809247ef194443E388e42933279Ef3] = 2311882987020870000000
    self.eligible_addresses[0x84afb4B60844F8759154d6Ff7B0580Daa2D4e37d] = 2273498164353480000000
    self.eligible_addresses[0x329c54289Ff5D6B7b7daE13592C6B1EDA1543eD4] = 2150851650780690000000
    self.eligible_addresses[0x83334ef0C6f6396413C508A7762741e9FD8B20E9] = 1955903987360560000000
    self.eligible_addresses[0xAA7A9d80971E58641442774C373C94AaFee87d66] = 1733896146872000000000
    self.eligible_addresses[0xE89181B79dF4Be6a77901331f473E05C43329770] = 1630444600709690000000
    self.eligible_addresses[0x141C1C16237439c645033586f0CB85A271f0016F] = 1544438648022250000000
    self.eligible_addresses[0x561369B3eC94D001031822011B9231e1436bcc78] = 1514691185488310000000
    self.eligible_addresses[0xD39C1775E98A73fd0A9c8ECac8C9fEDb9BB81E45] = 1459557036145460000000
    self.eligible_addresses[0x72bE5d6be003E489B0d3F20A426969470F624f20] = 1419126460672410000000
    self.eligible_addresses[0x559524b8d5aF5292E4CA30B30eA3DC8261e1DeA4] = 1264375666805830000000
    self.eligible_addresses[0xccdf9178BC4f253E4d530Fd08d605E713DA77A9f] = 1247454428979210000000
    self.eligible_addresses[0xb8308617d780C1d843Db60148210Ba130186232C] = 1196212781191240000000
    self.eligible_addresses[0x9C828E8EeCe7a339bBe90A44bB096b20a4F1BE2B] = 1169468274242050000000
    self.eligible_addresses[0xF80abA7BD2B7ee74099CA4bc18d7d611CD641e79] = 1089034178951900000000
    self.eligible_addresses[0xa2917120C698fb5F2A03e3fD3524bdA85a3eaEF6] = 1069966367156710000000
    self.eligible_addresses[0x8b3EFBEfa6eD222077455d6f0DCdA3bF4f3F57A6] = 1055980282003940000000
    self.eligible_addresses[0x1d12C9FEC45746823861176CE05bdECDA06f2115] = 1012542789327830000000
    self.eligible_addresses[0xAE87E2bb252f7A5B855D64bfCdFeD07d7BF07bcc] = 997351104565606000000
    self.eligible_addresses[0x932e80D589F3259EA299d47e7d6FA048007f3Ed6] = 993804783704699000000
    self.eligible_addresses[0x7193342f776ebc03D819dce344a4cb8218613f2E] = 964084609778597000000
    self.eligible_addresses[0x9F3087a03C503F3E9920378951C090c585bB408e] = 935574619393639000000
    self.eligible_addresses[0x0Bd3Cb973f0B3a6734447fa2ec93b7C479a26dE0] = 935574619393639000000
    self.eligible_addresses[0x52256ef863a713Ef349ae6E97A7E8f35785145dE] = 935574619393639000000
    self.eligible_addresses[0x1dD50763ebf30966922c428177B090A90a634DE9] = 935574619393639000000
    self.eligible_addresses[0xD2d8E34Fa5BafA8E7903baBEf5fD9101Df45CE04] = 935574619393639000000
    self.eligible_addresses[0x17e06ce6914E3969f7BD37D8b2a563890cA1c96e] = 935574619393639000000
    self.eligible_addresses[0xA08212117eD24f10237d6e5e891bE7e8c9A0f2AD] = 935574619393639000000
    self.eligible_addresses[0x26602Bf417c4e57bA3d2268d7f93A1E16F29E069] = 847256375322881000000
    self.eligible_addresses[0x649f69CCd077Da03dFb11f4b1daAb4B625f5E9A3] = 847256375322881000000
    self.eligible_addresses[0x6129A2CF9D4f67C433a3EC867a912884936C1cbF] = 789026211011820000000
    self.eligible_addresses[0xE524D29daf6D7CDEaaaF07Fa1aa7732a45f330B3] = 773647569203824000000
    self.eligible_addresses[0x96Ad7a9f1EF57f46efc3553e8A4d4afCD8c77212] = 759911128856290000000
    self.eligible_addresses[0xaBd3ebf016304AB043FD744490e5C7647040B208] = 759911128856290000000
    self.eligible_addresses[0x7F6f138C955e5B1017A12E4567D90C62abb00074] = 759911128856290000000
    self.eligible_addresses[0x1B0583e43F6e2F93526D7b2dcC887106B030441D] = 758938131252119000000
    self.eligible_addresses[0x96de457F38673381B7280cAA1d004F73535B7A43] = 727877053888253000000
    self.eligible_addresses[0xf6de48B2E23E20a54a1677b93643E5F6cd0A6060] = 701680964545230000000
    self.eligible_addresses[0x7ab066BCD945264e1B1C8d451CB3517c973e676c] = 701680964545230000000
    self.eligible_addresses[0x48C26fADfeFbE063b1773aF4732565bcB55Adc64] = 701680964545230000000
    self.eligible_addresses[0xa521E425f37aCC731651565B41Ce3E5022274F4F] = 701680964545230000000
    self.eligible_addresses[0xf3B1B6e83Be4d55695f1D30ac3D307D9D5CA98ff] = 701680964545230000000
    self.eligible_addresses[0x42726b0570174227679521E48cDDf454357C8553] = 701680964545230000000
    self.eligible_addresses[0x0cb3e38741Ed54FDe0B7b7e1C93DCd28a4A6F15C] = 701680964545230000000
    self.eligible_addresses[0x69d08A457b0ff73291e0cb741cb863825561F616] = 632921218440577000000
    self.eligible_addresses[0x009d13E9bEC94Bf16791098CE4E5C168D27A9f07] = 614335718078640000000
    self.eligible_addresses[0x9A1e04ffd63230a0bdc723be5870AFF04af0bb02] = 613362720474469000000
    self.eligible_addresses[0xe8a4900BF1f3e498d6069f96158bCc132DBB7B44] = 605692686033036000000
    self.eligible_addresses[0x93CA2692Db73e975D6E8a7a4254c50A034239c9f] = 594385123425210000000
    self.eligible_addresses[0xA82c9ed42E7cea03Cfad4B03205E46d1a4a30998] = 581858205060009000000
    self.eligible_addresses[0xb53009E4dC25a494F3Bee03Ab121517e74b59F75] = 557605732442281000000
    self.eligible_addresses[0x71df067D1d2dF5291278b7C660Fd37d9b6272b4C] = 555132556163409000000
    self.eligible_addresses[0x0b98718264cA14d0A17C145FfE1e4F3c38a39372] = 555132556163409000000
    self.eligible_addresses[0x91212de083d29342F670FB69Ffa68176369e3B20] = 545892756946385000000
    self.eligible_addresses[0x505FB4560914eA9c3af22b75ca55c3881472ae45] = 526017474007878000000
    self.eligible_addresses[0x8575F0668CB0CDE8F3e3854cF915D98311Bb0057] = 526017474007878000000
    self.eligible_addresses[0x067214Ba2099775d25D82A3b814Dc35CE0cEEf72] = 526017474007878000000
    self.eligible_addresses[0x8973B848775a87a0D5bcf262C555859b87E6F7dA] = 472533868328996000000
    self.eligible_addresses[0x307d91591e57461d7476839E3e52BC620454F840] = 467787309696818000000
    self.eligible_addresses[0x41d76a4eDbc9F97ceDabA41da9ded98BA3BAC3Ef] = 467787309696818000000
    self.eligible_addresses[0x3304D37F3FE450c4326F2F9e50498FBFB0431b29] = 467787309696818000000
    self.eligible_addresses[0x0CF2A290EE5d5f16A891079a8a0381E238A27A5e] = 467787309696818000000
    self.eligible_addresses[0x0A3aF907dD774b93C745f5228ca84eb25a1582Fc] = 467787309696818000000
    self.eligible_addresses[0xc9645A47E927400B68fA169CF8E9DFDF3e3FFDFA] = 467787309696818000000
    self.eligible_addresses[0xFC52dF87a97E30F6AaF32e952cE3bD05a779DcAf] = 467787309696818000000
    self.eligible_addresses[0xE836e3cDBC912577E7beDBfa9A915a3319e3eFC4] = 467787309696818000000
    self.eligible_addresses[0x50f70fc008919a295583FD0598df8B18D06acef8] = 467787309696818000000
    self.eligible_addresses[0xC6a51D6E1f07e470CC4386F4FE295C3B8482dCed] = 467787309696818000000
    self.eligible_addresses[0x109DcCC4B8B99790d13C80AA41b17d749AA1882A] = 467787309696818000000
    self.eligible_addresses[0x58771946FE77fcA0234cc7A9F360d77Afb41CAf8] = 467787309696818000000
    self.eligible_addresses[0xc782b3d3a484aABA2C60b1238921CE0c0f6fd50C] = 467787309696818000000
    self.eligible_addresses[0x780AA4FAcE54B454BE640c1257A3BDA3917111EF] = 467787309696818000000
    self.eligible_addresses[0x5f31Fd28Bf4c9034Dc73C63aBF95759a1B8a8486] = 467787309696818000000
    self.eligible_addresses[0xc3E85B30bEa6529B3239e3DB7978f3C71845f487] = 467787309696818000000
    self.eligible_addresses[0x647268daEC544a07814e962145ba435dB2bB0982] = 467787309696818000000
    self.eligible_addresses[0x71C5E91ad3D7359196746EF7cc413E787761Be1d] = 467787309696818000000
    self.eligible_addresses[0xC507eD8BCfE049D934b6e32d1Ae482d0081eaefc] = 467787309696818000000
    self.eligible_addresses[0xe63E2CDd24695464C015b2f5ef723Ce17e96886B] = 467787309696818000000
    self.eligible_addresses[0x0988E41C02915Fe1beFA78c556f946E5F20ffBD3] = 467787309696818000000
    self.eligible_addresses[0xeEb061EDaAd7Be1cC8106Ea51Db59071c55359DA] = 467787309696818000000
    self.eligible_addresses[0x155ddAc174DC33A1c7054B90aE8c31228776D147] = 460901871165186000000
    self.eligible_addresses[0x1B3bBAb4f9975094b326C6b64644fF2723d163C4] = 450308958292386000000
    self.eligible_addresses[0x78b783e4DB4101CD298622963e7C9E72775a12f1] = 407611150177422000000
    self.eligible_addresses[0xfC4B2a62A06cb2E1C6A743E9aE327Bb16977E4c1] = 397292274572889000000
    self.eligible_addresses[0x84bC1fC6204b959470BF8A00d871ff8988a3914A] = 377047008883916000000
    self.eligible_addresses[0x0dAE2421e6Ad3B4C5dEA80C8EB94499679BaE823] = 355743722545788000000
    self.eligible_addresses[0x3c637470C140aD6B39CE7BAd3DDB5A045FA8D574] = 333531497519902000000
    self.eligible_addresses[0xa40eb69D2ADBD34Ea73ea1Dfd049F825e8216Eb0] = 328196088710942000000
    self.eligible_addresses[0x3c5c884D512a4513c9C7440be3c2533175178a09] = 321238901314999000000
    self.eligible_addresses[0x87edfD6b1B545d4358F0bF302B1a51660a0DFdF1] = 321238901314999000000
    self.eligible_addresses[0xa1992346630fa9539bc31438A8981c646C6698F1] = 321238901314999000000
    self.eligible_addresses[0xddB20A475AeeAd0ceA068f98Cf83b2465D83071F] = 310629001375245000000
    self.eligible_addresses[0xDcdf8164AAF9345E48E747e95B07d2782D09Cb40] = 292496498819930000000
    self.eligible_addresses[0x2A7051d7CBbEF7B6889f8e14774020b1653b94C1] = 240199427783124000000
    self.eligible_addresses[0x9b7e5d40fCb79bbF4171521F5a8e2e15808f82D7] = 235891583994805000000
    self.eligible_addresses[0x2b3de33A62A656c76Ed366FE55C49CfE142F5427] = 235891583994805000000
    self.eligible_addresses[0x12bd56B1AA999ecfAc7B56fC8e2fB0E5dCaDF419] = 233893654848410000000
    self.eligible_addresses[0x9B93B7bbBdAD456Fd3662B18c26Cd61755eD7ecC] = 233893654848410000000
    self.eligible_addresses[0x52EAF3F04cbac0a4B9878A75AB2523722325D4D4] = 233893654848410000000
    self.eligible_addresses[0xa9d2Ea5e931B55B6F11c7838459559EAfb9f61E0] = 233893654848410000000
    self.eligible_addresses[0x705550d868DD6da69Ed2C649eB15c9Fb4647C566] = 233893654848410000000
    self.eligible_addresses[0x8C8A542F9a0Deb10A2F310127FA396cAB984E6c3] = 233893654848410000000
    self.eligible_addresses[0x70CCBE10F980d80b7eBaab7D2E3A73e87D67B775] = 233893654848410000000
    self.eligible_addresses[0x6Abcba6cf08fbFd33CC09c73940E00D8dB6C7987] = 233893654848410000000
    self.eligible_addresses[0xBD6F210A624a792e7d30A2F7591Dc7Abce2F3C48] = 233893654848410000000
    self.eligible_addresses[0x82b1bF183B2AbaCD5edE6694e7ceF940E41b1845] = 233893654848410000000
    self.eligible_addresses[0xE39687eD7d3bea7E5ACE354211b95fc59AD2b444] = 233893654848410000000
    self.eligible_addresses[0xB272EF11Ad76ac73ddcD37955bd4E6d93fd21614] = 233893654848410000000
    self.eligible_addresses[0x35AA433e4b35de2C907b5c2d5703822e253AEF54] = 233893654848410000000
    self.eligible_addresses[0xEeE7FB850D28f5cabd5f1EDF540646b5bEA17CE5] = 233893654848410000000
    self.eligible_addresses[0xEe57B250e82902A178BEDa7A9fBa4ff63f8BdDc8] = 233893654848410000000
    self.eligible_addresses[0xcba3a6C78408608dad0FA7d203f862aD0c984AE1] = 233893654848410000000
    self.eligible_addresses[0xf4B03870807059042B98C7abe889d5E9ed787371] = 233893654848410000000
    self.eligible_addresses[0x8cF0A1Abc730D65E369726377878CC145e0d4716] = 233893654848410000000
    self.eligible_addresses[0x3c5Aac016EF2F178e8699D6208796A2D67557fe2] = 233893654848410000000
    self.eligible_addresses[0xD78ccB7Cd497aB5E85C1b2dA3733F0Ecfd9d5103] = 233893654848410000000
    self.eligible_addresses[0x542795BDcbeD4Dc47b535Add84C3A446Fb370289] = 233893654848410000000
    self.eligible_addresses[0x0Dc2e2cE90e814C0CFb655438237BD747d2247f3] = 233893654848410000000
    self.eligible_addresses[0x0444516Ed1a02863cCA7ddEB0937B15DFe33bEe0] = 233893654848410000000
    self.eligible_addresses[0x8aF0B9A9B751E086122bC340188Bd9d99b8C7ec1] = 233893654848410000000
    self.eligible_addresses[0x7BFe766FBF8A25A6cBC47d74cB9EbC7275965621] = 233893654848410000000
    self.eligible_addresses[0xd461cf004EdA0DDB0028B831B62bf38b3a6D1e5A] = 233893654848410000000
    self.eligible_addresses[0x4702D39c499236A43654c54783c3f24830E247dC] = 233893654848410000000
    self.eligible_addresses[0xd7Cc5B9E380eC67CDcC298Db485E17deB7847673] = 233893654848410000000
    self.eligible_addresses[0x92683a09B64148369b09f96350B6323D37Af6AE3] = 233893654848410000000
    self.eligible_addresses[0xf3D476566BCC8E882A3910F1471428522449d89E] = 233893654848410000000
    self.eligible_addresses[0x962228a90eaC69238c7D1F216d80037e61eA9255] = 233893654848410000000
    self.eligible_addresses[0x2fD798a8fcc64Ba1Bc62bF363A6A28F63e93D5b8] = 233893654848410000000
    self.eligible_addresses[0xc1f4D15C16A1f3555E0a5F7AeFD1e17AD4aaf40B] = 233893654848410000000
    self.eligible_addresses[0x668D4a494192147f396f2e55Dff1fED7C8BA595a] = 233893654848410000000
    self.eligible_addresses[0x941ec857134B13c255d6EBEeD1623b1904378De9] = 233893654848410000000
    self.eligible_addresses[0x2D07C0A3C8033Af7e3eEe470b15A3a7831009268] = 233893654848410000000
    self.eligible_addresses[0xAE72f47d88C3d719B281C4d302afB9cf2bD60319] = 233893654848410000000
    self.eligible_addresses[0x5a35455c3534fD0B652667e6a94a60E3e9A56546] = 233893654848410000000
    self.eligible_addresses[0xAA078f64D26b63353ad7138E0203E51ff54984aD] = 233893654848410000000
    self.eligible_addresses[0xC0f5b7f7703BA95dC7C09D4eF50A830622234075] = 233893654848410000000
    self.eligible_addresses[0x1Dbf3eF9Af78408f76f486239A5e105817316969] = 233893654848410000000
    self.eligible_addresses[0x718eF48DA682374b99e13b33D9eA75a59D23DE51] = 233893654848410000000
    self.eligible_addresses[0x92Da7f745fBa9BDdf369799Fa8864993A6e1127b] = 233893654848410000000
    self.eligible_addresses[0xB25C5E8fA1E53eEb9bE3421C59F6A66B786ED77A] = 233893654848410000000
    self.eligible_addresses[0x0b0b7736E66CD2840fDb08c9988f46204294A86F] = 230982146632857000000
    self.eligible_addresses[0xd184CF2f60Da3C54eD1fc371a3e04179C41570c6] = 226604085643744000000
    self.eligible_addresses[0xA44F500bDD82E2e783Ef292e2BcE6Ab5124A6394] = 221072878335933000000
    self.eligible_addresses[0x6C320A427a22012486722CF8e8b504aC1C0f3B2a] = 208537778524458000000
    self.eligible_addresses[0x420697d7E966861d57aBF4D8B5950eD5741Bf98d] = 203805575088711000000
    self.eligible_addresses[0x680fbd8DDD5Fcccf9667eeBc710482bFbfa52438] = 198629802637889000000
    self.eligible_addresses[0xbAA32387bd55553Ec806622d524b12BbB8242a19] = 196526804549828000000
    self.eligible_addresses[0xEB40A065854bd90126A4E697aeA0976BA51b2eE7] = 189248034010946000000
    self.eligible_addresses[0xfD8bD978f198503a0BA9C5D7f7586E23fC4A4b40] = 187246569485206000000
    self.eligible_addresses[0x5E926AcF797e72D08E66e1f6B2cFc49200453c6D] = 170756541522868000000
    self.eligible_addresses[0x26D4793a24eDeBa373505721E507aFf2f5c7B58F] = 168736746107627000000
    self.eligible_addresses[0x27629B5d175E899a19eD6B3a96016377d5eE4768] = 167411722394298000000
    self.eligible_addresses[0xa674F2C33f504345F50cA6C850F9fd8338612166] = 167411722394298000000
    self.eligible_addresses[0x61ABf360FEe2b472b8E6dCD94215120259A95Dd7] = 157463132545787000000
    self.eligible_addresses[0x66143d695baFf44a3C8549bBdb16098d55674F9D] = 152786366684183000000
    self.eligible_addresses[0x32DbEf8B3C7DD3E32C874D8A62162206518E5906] = 147620703067681000000
    self.eligible_addresses[0x36fDb65D2d484b036AdE6A2a418B05Da0c848f1B] = 145575410777651000000
    self.eligible_addresses[0xC0018a967500A646d19D232545a1d2ef0f3FFc35] = 145575410777651000000
    self.eligible_addresses[0x7904Ad7c992CDAb500dAa0f3366301b1f5365B62] = 145575410777651000000
    self.eligible_addresses[0xB8F7725F64a09A453B5736462343187eA84bbD44] = 145575410777651000000
    self.eligible_addresses[0xa57C6196f4B15e05436acc32f598c018a62C05D1] = 136860692309329000000
    self.eligible_addresses[0x49F9d409C580660b0F8e51835C4C6D2f4433E93C] = 136234425059958000000

