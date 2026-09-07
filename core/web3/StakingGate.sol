// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract StakingGate is Ownable {
    IERC20 public stakingToken; // e.g., USDC or the platform's native token
    uint256 public requiredStakeAmount;

    struct UserProfile {
        uint256 reputationScore;
        uint256 activeStakes;
        bool isQuarantined;
    }

    // The Quarantine Queue [TASK-081]
    struct Submission {
        bytes32 assetHash;
        address miner;
        bool isReviewed;
        bool isApproved;
    }

    mapping(address => UserProfile) public users;
    mapping(bytes32 => Submission) public submissions;

    event SubmissionStaked(bytes32 indexed assetHash, address indexed miner, uint256 stakedAmount);
    event StakeSlashed(bytes32 indexed assetHash, address indexed miner, uint256 slashedAmount);
    event SubmissionApproved(bytes32 indexed assetHash, address indexed miner);

    constructor(address _stakingToken, uint256 _requiredStakeAmount) {
        stakingToken = IERC20(_stakingToken);
        requiredStakeAmount = _requiredStakeAmount;
    }

    /**
     * @dev Front-door entry for all new data. Forces untrusted miners to lock collateral.
     */
    function stakeAndSubmit(bytes32 _assetHash) external {
        UserProfile storage profile = users[msg.sender];
        require(!profile.isQuarantined, "Account is quarantined for spamming");
        
        // High-reputation users (Score > 100) bypass the physical staking requirement
        uint256 amountToStake = (profile.reputationScore > 100) ? 0 : requiredStakeAmount;

        if (amountToStake > 0) {
            require(
                stakingToken.transferFrom(msg.sender, address(this), amountToStake), 
                "Stake transfer failed. Cannot submit data."
            );
            profile.activeStakes += amountToStake;
        }

        // Lock submission into the Quarantine Queue
        submissions[_assetHash] = Submission({
            assetHash: _assetHash,
            miner: msg.sender,
            isReviewed: false,
            isApproved: false
        });

        emit SubmissionStaked(_assetHash, msg.sender, amountToStake);
    }

    /**
     * @dev Called by the Web2 Oracle (or Peer Reviewers) once the data is verified.
     * Approves data, refunds stakes, or slashes scammers.
     */
    function reviewSubmission(bytes32 _assetHash, bool _isValid) external onlyOwner {
        Submission storage sub = submissions[_assetHash];
        require(!sub.isReviewed, "Asset already reviewed");
        
        sub.isReviewed = true;
        UserProfile storage profile = users[sub.miner];

        if (_isValid) {
            sub.isApproved = true;
            profile.reputationScore += 10; // Build reputation
            
            // Refund their stake if one was locked
            if (profile.activeStakes >= requiredStakeAmount) {
                profile.activeStakes -= requiredStakeAmount;
                stakingToken.transfer(sub.miner, requiredStakeAmount);
            }
            emit SubmissionApproved(_assetHash, sub.miner);
        } else {
            // [TASK-081] - Slash the spammer's staked collateral
            if (profile.activeStakes >= requiredStakeAmount) {
                profile.activeStakes -= requiredStakeAmount;
                // Slashed tokens are kept in the contract treasury or burned
            }
            
            // Destroy reputation and quarantine if they hit zero
            if (profile.reputationScore >= 10) {
                profile.reputationScore -= 10;
            } else {
                profile.reputationScore = 0;
                profile.isQuarantined = true; // Permanently lock the fake account
            }
            
            emit StakeSlashed(_assetHash, sub.miner, requiredStakeAmount);
        }
    }
}
