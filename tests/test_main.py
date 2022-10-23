""" Test the project contract """
import random
import merkle

from hashlib import sha1
from brownie import accounts
from brownie import BTD



# globals
placeholder_token_uri = "QmWgwxv727vTzMhqE74KVHY3JhwfdWH6ZBf6CUB8Hax6wT"


def get_accounts() -> tuple:
    """ Get all the available accounts in their own groups """
    # Define the various user groups.
    admin_accounts = [
            accounts[0],
            accounts[1],
            accounts[2],
            ]

    # Account 2 is both wl and admin
    whitelist_accounts = [
            accounts[2],
            accounts[3],
            accounts[4],
            accounts[5],
            accounts[6],
            accounts[7]
            ]

    regular_accounts = [
            accounts[8],
            accounts[9]
            ]

    return admin_accounts, whitelist_accounts, regular_accounts


def test_deploy() -> BTD:
    """ Deploy the contract """
    # Arrange
    expected_suppply = 3333
    expected_start_id = 0
    admin_accounts, white_list, _ = get_accounts()
    root = merkle.get_root(white_list)

    # Act
    contract = BTD.deploy(
            placeholder_token_uri,
            root,
            admin_accounts,
            {"from": admin_accounts[0], "value": 1000000000000000000}
            )
    supply = contract.totalSupply()
    minted = contract.minted()

    # Assert
    assert expected_suppply == supply, "The total supply of tokens is not correct"
    assert expected_start_id == minted, "Token mints did not start from 1?"

    # Return
    return contract


def test_mint_all():
    """
        This test attempts to mint all tokens through the adminMint feature.

        While it does some important testing, it primarily exists to
        help other tests that rely on the tokens being sold out first.
    """
    # Arrange
    contract = test_deploy()
    admin_accounts, _, _ = get_accounts()
    expected_minted = contract.totalSupply()

    # Act
    for _ in range(0, contract.totalSupply(), 33):
        contract.adminMint(admin_accounts[0], 33, {"from": admin_accounts[0]})
    minted = contract.minted()

    # Assert
    assert expected_minted == minted, "Minted amount differs from the total supply!"

    # Return
    return contract


def test_admin_mint():
    """
        Testing the adminMint (or airdrop) function.
    """
    # Arrange
    contract = test_deploy()
    minted = contract.minted()
    print('minted: ',minted , type(minted))
    admin_accounts, _, _ = get_accounts()

    # Act
    contract.adminMint(admin_accounts[0], 1, {"from": admin_accounts[0]})

    # Assert
    assert contract.minted() == minted + 1, "Minting token did not increment the counter."

    # Return
    return contract


def test_burn_token():
    """ Test the burnToken function """
    # Arrange
    token_to_burn = 1
    contract = test_admin_mint() # Already minted one
    admin_accounts, _, _ = get_accounts()


    # Act
    contract.tokenURI(token_to_burn) # Make sure its valid
    contract.burnToken(token_to_burn, {"from": admin_accounts[0]})

    # Assert
    try:
        contract.tokenURI(token_to_burn)
        assert False, "Should not be able to access a burned token"
    except: # pylint: disable=bare-except
        pass

    # Return
    return contract


def test_withdraw():
    """
        Test the withdraw function of the contract.

        For the test to pass, all admin accounts should receive the same
        amount of ETH from the contract.
    """
    # Arrange
    admin_accounts, whitelist_accounts, _ = get_accounts()
    contract = BTD.deploy(
            "placeholder",
            merkle.get_root(whitelist_accounts),
            [
                admin_accounts[0],
                admin_accounts[1],
                admin_accounts[2]
                ],
            {
                "from": admin_accounts[0],
                "value": 3000
                }
        )

    balance1 = admin_accounts[1].balance()
    balance2 = admin_accounts[2].balance()

    # Act
    contract.withdraw(1000, {"from": admin_accounts[0]})

    # Assert
    # Not testing admin0 because their balance will change with gas fees.
    assert balance1 + 1000 == admin_accounts[1].balance(), "Not the right amount of ETH was transferred to admin1"
    assert balance2 + 1000 == admin_accounts[2].balance(), "Not the right amount of ETH was transferred to admin2"
    assert contract.balance() == 0, "Did all the money leave the contract?"


def test_withdraw_overdraft():
    """
        Test to make sure that no ETH is sent out to any admin, if there is not
        enough ETH for all admins.

        This should just be the EVM reverting transactions, but better test to make
        sure it actually happens.
    """
    # Arrange
    admin_accounts, whitelist_accounts, _ = get_accounts()
    contract = BTD.deploy(
            "placeholder",
            merkle.get_root(whitelist_accounts),
            [
                admin_accounts[0],
                admin_accounts[1],
                admin_accounts[2]
                ],
            {
                "from": admin_accounts[0],
                "value": 2000 # Only enough ETH for 2 admins
                }
        )

    balance1 = admin_accounts[1].balance()
    balance2 = admin_accounts[2].balance()

    # Act
    try:
        contract.withdraw(1000, {"from": admin_accounts[0]})
        assert False, "This should crash"
    except: # pylint: disable=bare-except
        pass

    # Assert
    # Test balances just in case.
    # Not testing admin0 because their balance will change with gas fees.
    assert contract.balance() == 2000, "No money should leave the contract!"
    assert balance1 + 1000 > admin_accounts[1].balance(),\
            "No admin should have more money!"
    assert balance2 + 1000 > admin_accounts[2].balance(),\
            "No admin should have more money!"


def test_pause():
    """ Pause the contract and test if you can still mint and transfer """
    # Arrange
    contract = test_deploy()
    admin_accounts, whitelist_accounts, _ = get_accounts()

    # Act & Arrange
    contract.pause({"from": admin_accounts[0]})
    try:
        contract.adminMint(admin_accounts[0], 2, {"from": admin_accounts[0]})
        # TODO: Test for non admin mint methods too
        assert False, "Should not have managed to call this."
    except: # pylint: disable=bare-except
        pass


    try:
        contract.whiteListMint(1, merkle.get_proof(whitelist_accounts, whitelist_accounts[0]), {"from": whitelist_accounts[0], "value": 5000000000000000})
        # TODO: Test for non admin mint methods too
        assert False, "Should not have managed to call this."
    except: # pylint: disable=bare-except
        pass

    # Return the paused contract
    return contract


def test_unpause():
    """ Test the unpause functionality """
    # Arrange
    contract = test_pause()
    admin_accounts, _, _ = get_accounts()

    # Act
    contract.unpause({"from": admin_accounts[0]})
    contract.adminMint(admin_accounts[0], 2, {"from": admin_accounts[0]})

    # Assert
    assert True, "If it got here without crashing, then that's good enough!"

    # Return
    return contract


def test_set_mint_price():
    """ Test if setting the mint price works """
    # Arrange
    contract = test_deploy()
    admin_accounts, _, _ = get_accounts()
    new_price = 1000000000000000000000000

    # Act
    contract.setMintPrice(new_price, {"from": admin_accounts[0]})
    current_price = contract.mintPrice()

    # Assert
    assert current_price == new_price, "Mint price was not set successfully"

    # Return
    return contract


def test_whitelist_mint():
    """
        Make sure the white-list mint works with the right arguments.
    """
    # Arrange
    contract = test_deploy()
    mint_price = contract.mintPrice()
    _, whitelist_accounts, _ = get_accounts()

    # Act
    for i, account in enumerate(whitelist_accounts):
        # Cannot mint 0 tokens
        if i < 1:
            continue

        price = ((i-2)*mint_price if i-2 > 0 else 0)
        contract.whiteListMint(i, merkle.get_proof(whitelist_accounts, account), {"from": account, "value": price})

    # Assert
    for i, account in enumerate(whitelist_accounts):
        assert contract.balanceOf(account) == i,\
                "Did not mint the right amount of tokens for this account!"

    # Return
    return contract


def test_whitelist_over_limit():
    """
        Make sure that white lists cannot mint more than what is allowed for test_whitelist_mint
    """
    # Arrange
    contract = test_deploy()
    _, whitelist_accounts, _ = get_accounts()
    max_per_wl = contract.maxPerWL()
    mint_price = contract.mintPrice()
    free_mints = contract.freeMints()

    # Act
    contract.whiteListMint(max_per_wl, merkle.get_proof(whitelist_accounts, whitelist_accounts[0]), {"from": whitelist_accounts[0], "value": (mint_price-free_mints)*max_per_wl})

    # Assert
    try:
        contract.whiteListMint(1, merkle.get_proof(whitelist_accounts, whitelist_accounts[0]), {"from": whitelist_accounts[0], "value": mint_price})
        assert False, "Should not be able to mint more than what is allowed per wl!"
    except: # pylint: disable=bare-except
        pass

    # Return
    return contract


def test_public_mint():
    """
        Enable the public mint, try to mint, then disable it, then try again.
    """
    # Arrange
    contract = test_deploy()
    mint_price = contract.mintPrice()
    admin_accounts, _, regular_accounts = get_accounts()

    # Act and Assert
    try:
        contract.publicMint(2, {"from": regular_accounts[0], "value": 2*mint_price})
        assert False, "Should not be able to mint yet"
    except: # pylint: disable=bare-except
        pass

    contract.setPublicSale(True, {"from": admin_accounts[0]})
    assert contract.publicSale() is True, "Did not set the instance variable correctly!"

    contract.publicMint(2, {"from": regular_accounts[0], "value": 2*mint_price})
    assert contract.balanceOf(regular_accounts[0]) == 2, "Did not mint enough tokens!"

    contract.setPublicSale(False, {"from": admin_accounts[0]})
    assert contract.publicSale() is False, "Did not set the instance variable correctly!"

    try:
        contract.publicMint(2, {"from": regular_accounts[0], "value": 2*mint_price})
        assert False, "Should not be able to mint anymore"
    except: # pylint: disable=bare-except
        pass

    # Return
    return contract
