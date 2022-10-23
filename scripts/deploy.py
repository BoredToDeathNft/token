""" Deployer script """
import sys

from brownie import accounts
from brownie import BTD
from brownie import network


def deploy_main():
    """ Deploy on the main ETH net """
    real_placeholder_uri = ""
    admin_wallets = [

            ]
    print("You might want to use a fresh wallet and etherscan key for this one", file=sys.stderr)


def deploy_dev():
    """ Deploy on a dev network """
    owner = accounts[0]
    admins = [
            accounts[0],
            accounts[1],
            accounts[2],
            accounts[3]
            ]
    placeholder_uri = "QmcqTdMdNwQEjjwMdv4QLUcimXLjatomaoqXQKgRGLqcNW"



    contract = BTD.deploy(
            placeholder_uri,
            0x601712bfdd978644cd68a58882b050308671b98df39548ed215b5bbaea9ca872,
            admins,
            {"from": owner, "value": 1000000000000000000}
        )

    print(f"Contract has been deployed at: {contract}")



def deploy_test():
    """ Deploy on a test network """
    owner = accounts.load("ctf")
    other_admin = accounts.load("ctf1")
    placeholder_uri = "QmUnXR1eDn7wKtuZDSivPkQmm18i5iskoQRS8m8kdPa91V"

    contract = BTD.deploy(
            placeholder_uri,
            0x601712bfdd978644cd68a58882b050308671b98df39548ed215b5bbaea9ca872,
            [owner, other_admin],
            {"from": owner},
            publish_source=True
            )

    print(f"Contract has been deployed on {network.show_active()} at: {contract}")


def main():
    # if network.show_active() == "mainnet":
        # deploy_main()
    if network.show_active() == "development":
        deploy_dev()
    else:
        deploy_test()




if __name__ == "__main__":
    main()

