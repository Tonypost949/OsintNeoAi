// core/web3/hardhat.config.js
require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

const SEPOLIA_RPC_URL = process.env.SEPOLIA_RPC_URL || "";
const PRIVATE_KEY = process.env.PRIVATE_KEY || "";
const ETHERSCAN_API_KEY = process.env.ETHERSCAN_API_KEY || "";

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.20", // Matches the OpenZeppelin contracts standard
    settings: {
      optimizer: {
        enabled: true,
        runs: 200 // Optimizes the contract for cheaper gas execution
      }
    }
  },
  networks: {
    // Defines the live testnet
    sepolia: {
      url: SEPOLIA_RPC_URL,
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      chainId: 11155111
    },
    // Useful if you still want to run quick local tests: `npx hardhat test`
    hardhat: {
      chainId: 1337
    }
  },
  // Allows for automated smart contract verification on Etherscan
  etherscan: {
    apiKey: ETHERSCAN_API_KEY
  }
};
