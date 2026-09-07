const hre = require("hardhat");

async function verifyContract(name, address, constructorArguments = []) {
    console.log(`\nVerifying ${name} at ${address}...`);
    try {
        await hre.run("verify:verify", {
            address: address,
            constructorArguments: constructorArguments,
        });
        console.log(`Successfully verified ${name} on Etherscan!`);
    } catch (error) {
        if (error.message.toLowerCase().includes("already verified")) {
            console.log(`${name} is already verified.`);
        } else {
            console.error(`Verification failed for ${name}:`, error.message);
        }
    }
}

async function main() {
    console.log("Starting Automated Etherscan Verification Pipeline...\n");

    const STAKING_GATE_ADDRESS = process.env.STAKING_GATE_ADDRESS;
    const MULTI_POOL_ESCROW_ADDRESS = process.env.MULTI_POOL_ESCROW_ADDRESS;
    const OSINT_TOKEN_ADDRESS = process.env.OSINT_TOKEN_ADDRESS;
    const TFT_TOKEN_ADDRESS = process.env.TFT_TOKEN_ADDRESS;
    const USDC_ADDRESS = process.env.USDC_ADDRESS;

    if (!STAKING_GATE_ADDRESS || !MULTI_POOL_ESCROW_ADDRESS) {
        throw new Error("Missing required contract addresses. Export them or add them to your .env file.");
    }

    const requiredStake = hre.ethers.parseEther("100");

    await verifyContract("StakingGate", STAKING_GATE_ADDRESS, [
        OSINT_TOKEN_ADDRESS,
        requiredStake
    ]);

    await verifyContract("MultiPoolEscrow", MULTI_POOL_ESCROW_ADDRESS, [
        USDC_ADDRESS,
        OSINT_TOKEN_ADDRESS,
        TFT_TOKEN_ADDRESS
    ]);

    console.log("\nAll contracts processed for Etherscan verification.");
}

main().catch((error) => {
    console.error("Verification script encountered an error:", error);
    process.exitCode = 1;
});
