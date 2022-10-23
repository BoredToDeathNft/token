const fs = require('fs')
const keccak256 = require("keccak256");
const { MerkleTree } = require("merkletreejs");




// Read data, turn it into an array of addresses, and remove the empty line from the end
const data = fs.readFileSync('tests/whitelist', "UTF-8");
let white_list = data.split(/\r?\n/)
white_list.pop()



const leaf_nodes = white_list.map(addr => keccak256(addr));
const merkle_tree = new MerkleTree(leaf_nodes, keccak256, { sortPairs: true });


if (process.argv[2] == "proof")
{
    console.log(JSON.stringify(merkle_tree.getHexProof(keccak256(process.argv[3]))))
}


if (process.argv[2] == "root")
{
    console.log(JSON.stringify(merkle_tree.getHexRoot()))
}
