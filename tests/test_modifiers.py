"""
A number of tests to make sure modifiers are being enforced correctly
"""

import merkle

from brownie import BTD
from brownie import accounts

from test_main import get_accounts
from test_main import test_deploy


def test_only_admin():
    """
        Test that all functions marked as onlyAdmin
        can be called by an admin, but *not* by a non-admin.
    """
    # Arrange
    contract = test_deploy()
    admin_accounts, whitelist_accounts, regular_accounts = get_accounts()
    uri = "lol"


    # Act & some Assert
    contract.pause({"from": admin_accounts[0]})
    contract.unpause({"from": admin_accounts[0]})
    try:
        contract.pause({"from": whitelist_accounts[-1]})
        contract.unpause({"from": whitelist_accounts[-1]})
        contract.pause({"from": regular_accounts[0]})
        contract.unpause({"from": regular_accounts[0]})
        assert False, "Should not be able to use this function with non-admin accounts."
    except: # pylint: disable=bare-except
        pass


    contract.adminMint(admin_accounts[0], 10, {"from": admin_accounts[0]})
    try:
        contract.adminMint(whitelist_accounts[-1], 10, {"from": whitelist_accounts[-1]})
        contract.adminMint(regular_accounts[0], 10, {"from": regular_accounts[0]})
        assert False, "Should not be able to use this function with non-admin accounts."
    except: # pylint: disable=bare-except
        pass



    assert contract.minted() > 3, "Throwing this exception because less than"+\
                                  " 3 will make the next bit fail."

    assert contract.minted() < 3000, "Throwing this exception because more than"+\
                                  " 3000 will make the next bit fail."


    contract.burnToken(1, {"from": admin_accounts[0]})
    try:
        contract.burnToken(1, {"from": whitelist_accounts[-1]})
        contract.burnToken(2, {"from": regular_accounts[0]})
        assert False, "Should not be able to use this function with non-admin accounts."
    except: # pylint: disable=bare-except
        pass


    contract.withdraw(100, {"from": admin_accounts[0]})
    try:
        contract.withdraw(100, {"from": whitelist_accounts[-1]})
        contract.withdraw(100, {"from": regular_accounts[0]})
        assert False, "Should not be able to use this function with non-admin accounts."
    except: # pylint: disable=bare-except
        pass


    contract.setMintPrice(100, {"from": admin_accounts[0]})
    try:
        contract.setMintPrice(100, {"from": whitelist_accounts[-1]})
        contract.setMintPrice(100, {"from": regular_accounts[0]})
        assert False, "Should not be able to use this function with non-admin accounts."
    except: # pylint: disable=bare-except
        pass


    contract.setPublicSale(True, {"from": admin_accounts[0]})
    contract.setPublicSale(False, {"from": admin_accounts[0]})
    try:
        contract.setPublicSale(True, {"from":  whitelist_accounts[-1]})
        contract.setPublicSale(False, {"from": whitelist_accounts[-1]})
        contract.setPublicSale(True, {"from":  regular_accounts[0]})
        contract.setPublicSale(False, {"from": regular_accounts[0]})
        assert False, "Should not be able to use this function with non-admin accounts."
    except: # pylint: disable=bare-except
        pass


def test_only_whitelist():
    """
        Test all functions that are marked by onlyWhiteList
    """
    contract = test_deploy()
    admin_accounts, whitelist_accounts, regular_accounts = get_accounts()

    contract.whiteListMint(1, merkle.get_proof(whitelist_accounts, whitelist_accounts[0]), {"from": whitelist_accounts[0]})
    try:
        # Try mint tokens with non whitelisted accounts, but using a whitelist proof
        contract.whiteListMint(1, merkle.get_proof(whitelist_accounts, whitelist_accounts[0]), {"from": admin_accounts[0]})
        contract.whiteListMint(1, merkle.get_proof(whitelist_accounts, whitelist_accounts[0]), {"from": regular_accounts[0]})
        assert False, "Should not be able to use this function with non-wl accounts."
    except: # pylint: disable=bare-except
        pass

    try:
        # Try mint tokens with non-whitelist accounts and an incorrect proof
        contract.whiteListMint(1, merkle.get_proof(whitelist_accounts, admin_accounts[0]), {"from": admin_accounts[0]})
        contract.whiteListMint(1, merkle.get_proof(whitelist_accounts, regular_accounts[0]), {"from": regular_accounts[0]})
        assert False, "Should not be able to use this function with non-wl accounts."
    except: # pylint: disable=bare-except
        pass
