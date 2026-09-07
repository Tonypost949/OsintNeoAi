// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

// Interface for the utility token ledgers (OSINT and TFT)
interface IUtilityLedger {
    function mintReward(address miner, uint256 value) external;
}

contract MultiPoolEscrow is Ownable {
    // The compliant stablecoin used for actual bounty payouts (e.g., USDC)
    IERC20 public settlementCoin; 

    // Pointers to the specific multi-ledger token contracts
    IUtilityLedger public osintToken;
    IUtilityLedger public taxFundedToken;

    // The UTXO-style Data Block representing an asset on the ledger
    struct DataBlock {
        bytes32 assetHash;
        bytes32 parentHash;
        address miner;
        string[] domainTags;
        bool isVerified;
    }

    // Maps the SHA-256 asset_hash from BigQuery to the on-chain data block
    mapping(bytes32 => DataBlock) public dataRegistry;

    event BlockRegistered(bytes32 indexed assetHash, address indexed miner);
    event BountyDistributed(bytes32 indexed closerHash, uint256 totalBounty);

    constructor(address _settlementCoin, address _osintToken, address _taxFundedToken) {
        settlementCoin = IERC20(_settlementCoin);
        osintToken = IUtilityLedger(_osintToken);
        taxFundedToken = IUtilityLedger(_taxFundedToken);
    }

    /**
     * @dev Called by the validated backend oracle when a block hits BigQuery.
     * Maps the Web2 data directly to the Web3 lineage tree.
     */
    function registerDataBlock(
        bytes32 _assetHash,
        bytes32 _parentHash,
        address _miner,
        string[] memory _domainTags
    ) external onlyOwner {
        dataRegistry[_assetHash] = DataBlock({
            assetHash: _assetHash,
            parentHash: _parentHash,
            miner: _miner,
            domainTags: _domainTags,
            isVerified: true
        });
        emit BlockRegistered(_assetHash, _miner);
    }

    /**
     * @dev Executes the Automated Split when a case is resolved and bounty funded.
     * Traverses the data ancestry to pay the Closer, Corroborator, and Catalyst.
     */
    function resolveCaseAndPayout(
        bytes32 _closerHash,
        uint256 _bountyAmount
    ) external onlyOwner {
        require(settlementCoin.balanceOf(address(this)) >= _bountyAmount, "Insufficient escrow funds");
        require(dataRegistry[_closerHash].isVerified, "Closer block not verified");

        // 1. Data Lineage Traversal (The Chain of Custody)
        DataBlock memory closer = dataRegistry[_closerHash];
        DataBlock memory corroborator = dataRegistry[closer.parentHash];
        DataBlock memory catalyst = dataRegistry[corroborator.parentHash];

        // 2. Algorithmic Weighting (40% Catalyst / 30% Corroborator / 30% Closer)
        uint256 catalystShare = (_bountyAmount * 40) / 100;
        uint256 corroboratorShare = (_bountyAmount * 30) / 100;
        uint256 closerShare = (_bountyAmount * 30) / 100;

        // 3. Stablecoin Settlement Payout
        if (catalyst.miner != address(0)) settlementCoin.transfer(catalyst.miner, catalystShare);
        if (corroborator.miner != address(0)) settlementCoin.transfer(corroborator.miner, corroboratorShare);
        if (closer.miner != address(0)) settlementCoin.transfer(closer.miner, closerShare);

        // 4. Multi-Token Tag Routing (Mining the Utility Tokens)
        _processUtilityRewards(closer);
        if (corroborator.miner != address(0)) _processUtilityRewards(corroborator);
        if (catalyst.miner != address(0)) _processUtilityRewards(catalyst);

        emit BountyDistributed(_closerHash, _bountyAmount);
    }

    /**
     * @dev Reads the domain_tags array and dynamically routes the utility rewards.
     * If a tag overlaps (e.g., TAX-FUNDED and OSINT), the miner is rewarded on both ledgers.
     */
    function _processUtilityRewards(DataBlock memory _block) internal {
        for (uint i = 0; i < _block.domainTags.length; i++) {
            bytes32 tagHash = keccak256(abi.encodePacked(_block.domainTags[i]));
            
            if (tagHash == keccak256(abi.encodePacked("OSINT"))) {
                osintToken.mintReward(_block.miner, 1 * 10**18); // Standard OSINT mint
            } 
            else if (tagHash == keccak256(abi.encodePacked("TAX-FUNDED"))) {
                taxFundedToken.mintReward(_block.miner, 1 * 10**18); // Standard TFT mint
            }
            // Future ledgers (e.g., "MED") can be seamlessly added here.
        }
    }
}
