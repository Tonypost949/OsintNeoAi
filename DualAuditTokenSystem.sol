// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title Dual Audit Token Ecosystem: TaxFundedToken (TFT) & OSINTCoin (OSINT)
 * 
 * 1. TaxFundedToken (TFT): Minted specifically for taxpayer-funded audits,
 *    government spending inquiries, FOIA releases, and non-profit tax waste exposures.
 * 
 * 2. OSINTCoin (OSINT): Minted for general open-source investigations, corporate oversight,
 *    missing person research, civil rights tracking, and user-driven investigations.
 */

contract DualAuditTokenSystem {
    address public platformAdmin;

    // --- TaxFundedToken (TFT) ---
    string public tftName = "TaxFunded Token";
    string public tftSymbol = "TFT";
    uint256 public tftTotalSupply;
    mapping(address => uint256) public tftBalanceOf;

    // --- OSINTCoin (OSINT) ---
    string public osintName = "OSINT Coin";
    string public osintSymbol = "OSINT";
    uint256 public osintTotalSupply;
    mapping(address => uint256) public osintBalanceOf;

    // Structure for On-Chain Dual Proofs
    struct AuditProof {
        string inquiryId;
        string category; // "TAX_FUNDED" or "GENERAL_OSINT"
        string targetEntity;
        uint256 impactScore;
        address whistleblowerRecipient;
        uint256 mintedAmount;
        uint256 timestamp;
    }

    mapping(bytes32 => AuditProof) public onChainAuditLedger;

    event TaxFundedTokenMinted(address indexed recipient, uint256 amount, string foiaId);
    event OSINTCoinMinted(address indexed recipient, uint256 amount, string inquiryId);

    constructor() {
        platformAdmin = msg.sender;
    }

    modifier onlyAdmin() {
        require(msg.sender == platformAdmin, "Only OsintNeoAi Platform Admin can mint");
        _;
    }

    /**
     * @dev Mint TaxFundedToken (TFT) for government/tax-payer audits
     */
    function mintTaxFundedToken(
        string memory foiaId,
        string memory targetEntity,
        uint256 taxWasteAmount,
        address recipient
    ) external onlyAdmin returns (bytes32) {
        bytes32 proofHash = keccak256(abi.encodePacked(foiaId, targetEntity, taxWasteAmount, block.timestamp));
        uint256 rewardAmount = (taxWasteAmount / 1000) * 100 * (10**18);

        onChainAuditLedger[proofHash] = AuditProof({
            inquiryId: foiaId,
            category: "TAX_FUNDED",
            targetEntity: targetEntity,
            impactScore: taxWasteAmount,
            whistleblowerRecipient: recipient,
            mintedAmount: rewardAmount,
            timestamp: block.timestamp
        });

        tftTotalSupply += rewardAmount;
        tftBalanceOf[recipient] += rewardAmount;

        emit TaxFundedTokenMinted(recipient, rewardAmount, foiaId);
        return proofHash;
    }

    /**
     * @dev Mint OSINTCoin (OSINT) for general user investigations
     */
    function mintOSINTCoin(
        string memory inquiryId,
        string memory targetEntity,
        uint256 impactScore,
        address recipient
    ) external onlyAdmin returns (bytes32) {
        bytes32 proofHash = keccak256(abi.encodePacked(inquiryId, targetEntity, impactScore, block.timestamp));
        uint256 rewardAmount = impactScore * 50 * (10**18);

        onChainAuditLedger[proofHash] = AuditProof({
            inquiryId: inquiryId,
            category: "GENERAL_OSINT",
            targetEntity: targetEntity,
            impactScore: impactScore,
            whistleblowerRecipient: recipient,
            mintedAmount: rewardAmount,
            timestamp: block.timestamp
        });

        osintTotalSupply += rewardAmount;
        osintBalanceOf[recipient] += rewardAmount;

        emit OSINTCoinMinted(recipient, rewardAmount, inquiryId);
        return proofHash;
    }
}
