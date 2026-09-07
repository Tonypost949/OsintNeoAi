const hre = require("hardhat");

async function main() {
    console.log("Starting Web3 Infrastructure Deployment to Testnet...\n");
    const [deployer] = await hre.ethers.getSigners();
    console.log(`Executing deployment with wallet: ${deployer.address}`);

    // ==========================================
    // 1. Deploy Mock Tokens (For Testnet Only)
    // ==========================================
    console.log("\n--- Deploying Ecosystem Tokens ---");
    const MockERC20 = await hre.ethers.getContractFactory("ERC20Mock"); // Requires standard OpenZeppelin mock
    
    const usdc = await MockERC20.deploy("USD Coin", "USDC", deployer.address, hre.ethers.parseEther("1000000"));
    await usdc.waitForDeployment();
    console.log(`USDC (Settlement) deployed to: ${await usdc.getAddress()}`);

    const osintToken = await MockERC20.deploy("OSINT Coin", "OSINT", deployer.address, hre.ethers.parseEther("1000000"));
    await osintToken.waitForDeployment();
    console.log(`OSINT Token deployed to: ${await osintToken.getAddress()}`);

    const tftToken = await MockERC20.deploy("Tax-Funded Token", "TFT", deployer.address, hre.ethers.parseEther("1000000"));
    await tftToken.waitForDeployment();
    console.log(`TFT Token deployed to: ${await tftToken.getAddress()}`);

    // ==========================================
    // 2. Deploy Staking Gate [TASK-081]
    // ==========================================
    console.log("\n--- Deploying Staking Gate ---");
    // Setting the required stake to 100 OSINT tokens
    const requiredStake = hre.ethers.parseEther("100"); 
    
    const StakingGate = await hre.ethers.getContractFactory("StakingGate");
    const stakingGate = await StakingGate.deploy(await osintToken.getAddress(), requiredStake);
    await stakingGate.waitForDeployment();
    console.log(`StakingGate deployed to: ${await stakingGate.getAddress()}`);

    // ==========================================
    // 3. Deploy Multi-Pool Escrow
    // ==========================================
    console.log("\n--- Deploying Multi-Pool Escrow ---");
    const MultiPoolEscrow = await hre.ethers.getContractFactory("MultiPoolEscrow");
    const escrow = await MultiPoolEscrow.deploy(
        await usdc.getAddress(),
        await osintToken.getAddress(),
        await tftToken.getAddress()
    );
    await escrow.waitForDeployment();
    console.log(`MultiPoolEscrow deployed to: ${await escrow.getAddress()}`);

    // ==========================================
    // 4. Print Environment Variables for Azure
    // ==========================================
    console.log("\n==========================================");
    console.log("DEPLOYMENT COMPLETE. SAVE THESE ADDRESSES FOR AZURE ENV:");
    console.log(`STAKING_GATE_ADDRESS=${await stakingGate.getAddress()}`);
    console.log(`MULTI_POOL_ESCROW_ADDRESS=${await escrow.getAddress()}`);
    console.log("==========================================\n");
}

main().catch((error) => {
    console.error("Deployment failed:", error);
    process.exitCode = 1;
});
