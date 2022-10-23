import os
import json
import subprocess



def add_wl(whitelist: list):
    """ If they are not already in the whitelist, then add the current accounts """

    with open("tests/whitelist", "r", encoding="utf-8")as fp:
        wl_accounts = fp.read().split("\n")[:-1]


    # Don't add the accounts to the whitelist if they are already there
    for wl in whitelist:
        if wl in wl_accounts:
            return


    for wl in whitelist:
        with open("tests/whitelist", "a", encoding="utf-8")as out:
            out.write(str(wl)+"\n")



def get_root(white_list: list):
    """ Get the merkle root via node """
    add_wl(white_list)
    return int(json.loads(subprocess.check_output(["node", "tests/merkle_commandline.js", "root"]).decode("utf-8")), 16)

def get_proof(white_list: list, address: str):
    add_wl(white_list)
    proof_str = json.loads(subprocess.check_output(["node", "tests/merkle_commandline.js", "proof", str(address)]).decode("utf-8"))

    proof = []
    for addr in proof_str:
        proof.append(int(addr, 16))

    return proof
