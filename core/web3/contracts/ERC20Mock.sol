// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @dev Mock ERC20 Token for Local/Testnet deployment to represent USDC, OSINT, and TFT tokens.
 */
contract ERC20Mock is ERC20, Ownable {
    constructor(
        string memory name,
        string memory symbol,
        address initialOwner,
        uint256 initialSupply
    ) ERC20(name, symbol) Ownable(initialOwner) {
        _mint(initialOwner, initialSupply);
    }

    // Matches the IUtilityLedger interface signature needed by MultiPoolEscrow
    function mintReward(address miner, uint256 value) external onlyOwner {
        _mint(miner, value);
    }
}
