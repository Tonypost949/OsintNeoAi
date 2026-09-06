// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title DualAuditTokenSystem
 * @notice Two-token incentive system for OsintNeoAi platform
 *  - TaxFundedToken (TFT): rewards taxpayer-funded inquiries and FOIA disclosures
 *  - OSINTCoin (OSINT): rewards general open-source intelligence investigations
 */
contract DualAuditTokenSystem {
    struct AuditProof {
        address investigator;
        string  caseId;
        string  category;       // "taxpayer" or "osint"
        uint256 exposedAmount;  // dollars of waste/fraud exposed (taxpayer) or impact score (osint)
        uint256 timestamp;
        bytes32 documentHash;
        bool    verified;
    }

    struct InvestigatorStats {
        uint256 tftBalance;
        uint256 osintBalance;
        uint256 totalAudits;
        uint256 totalExposedValue;
    }

    mapping(address => InvestigatorStats) public investigators;
    mapping(bytes32 => AuditProof) public proofs;
    bytes32[] public proofRegistry;

    uint256 public totalTFTMinted;
    uint256 public totalOSINTMinted;
    uint256 public totalValueExposed;

    uint256 public constant TFT_PER_1000_DOLLARS = 100;   // 100 TFT per $1,000 exposed
    uint256 public constant OSINT_PER_IMPACT      = 50;    // 50 OSINT per impact point

    event AuditSubmitted(bytes32 indexed proofId, address investigator, string category, uint256 amount);
    event AuditVerified(bytes32 indexed proofId, uint256 tftMinted, uint256 osintMinted);
    event TokensTransferred(address indexed from, address indexed to, string token, uint256 amount);

    modifier onlyVerified(bytes32 _proofId) {
        require(proofs[_proofId].verified, "Audit not yet verified");
        _;
    }

    function submitAudit(
        string calldata _caseId,
        string calldata _category,
        uint256 _exposedAmount,
        bytes32 _documentHash
    ) external returns (bytes32) {
        require(_category == "taxpayer" || _category == "osint", "Invalid category");

        bytes32 proofId = keccak256(abi.encodePacked(block.timestamp, msg.sender, _caseId));
        require(proofs[proofId].timestamp == 0, "Proof already exists");

        proofs[proofId] = AuditProof({
            investigator: msg.sender,
            caseId: _caseId,
            category: _category,
            exposedAmount: _exposedAmount,
            timestamp: block.timestamp,
            documentHash: _documentHash,
            verified: false
        });

        proofRegistry.push(proofId);
        emit AuditSubmitted(proofId, msg.sender, _category, _exposedAmount);
        return proofId;
    }

    function verifyAndMint(bytes32 _proofId) external {
        require(proofs[_proofId].timestamp != 0, "Proof not found");
        require(!proofs[_proofId].verified, "Already verified");

        proofs[_proofId].verified = true;
        AuditProof storage proof = proofs[_proofId];

        uint256 tftMinted = 0;
        uint256 osintMinted = 0;

        if (proof.category == "taxpayer") {
            tftMinted = (proof.exposedAmount / 1000) * TFT_PER_1000_DOLLARS;
            investigators[proof.investigator].tftBalance += tftMinted;
            totalTFTMinted += tftMinted;
            totalValueExposed += proof.exposedAmount;
        } else {
            osintMinted = (proof.exposedAmount / 10) * OSINT_PER_IMPACT;
            investigators[proof.investigator].osintBalance += osintMinted;
            totalOSINTMinted += osintMinted;
        }

        investigators[proof.investigator].totalAudits++;
        investigators[proof.investigator].totalExposedValue += proof.exposedAmount;

        emit AuditVerified(_proofId, tftMinted, osintMinted);
    }

    function transferTokens(address _to, string calldata _token, uint256 _amount) external {
        require(_to != address(0), "Invalid recipient");

        if (_token == "tft") {
            require(investigators[msg.sender].tftBalance >= _amount, "Insufficient TFT");
            investigators[msg.sender].tftBalance -= _amount;
            investigators[_to].tftBalance += _amount;
        } else if (_token == "osint") {
            require(investigators[msg.sender].osintBalance >= _amount, "Insufficient OSINT");
            investigators[msg.sender].osintBalance -= _amount;
            investigators[_to].osintBalance += _amount;
        } else {
            revert("Invalid token");
        }

        emit TokensTransferred(msg.sender, _to, _token, _amount);
    }

    function getBalance(address _investigator) external view returns (uint256 tft, uint256 osint) {
        return (investigators[_investigator].tftBalance, investigators[_investigator].osintBalance);
    }

    function getProofCount() external view returns (uint256) {
        return proofRegistry.length;
    }

    function getTotalStats() external view returns (uint256 audits, uint256 valueExposed, uint256 tft, uint256 osint) {
        return (proofRegistry.length, totalValueExposed, totalTFTMinted, totalOSINTMinted);
    }
}
