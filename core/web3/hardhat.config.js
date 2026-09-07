// core/web3/hardhat.config.js
require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

const SEPOLIA_RPC_URL = process.env.SEPOLIA_RPC_URL || "";
const PRIVATE_KEY = process.env.PRIVATE_KEY || "";
const ETHERSCAN_API_KEY = process.env.ETHERSCAN_API_KEY || "";

const isValidPrivateKey = PRIVATE_KEY && PRIVATE_KEY.length === 64 && /^[0-9a-fA-F]+$/.test(PRIVATE_KEY);

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    sepolia: {
      url: SEPOLIA_RPC_URL,
      accounts: isValidPrivateKey ? [PRIVATE_KEY] : [],
      chainId: 11155111
    },
    hardhat: {
      chainId: 1337
    }
  },
  etherscan: {
    apiKey: ETHERSCAN_API_KEY
  }
};
