// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title PiRC-101 Sovereign Vault (Hardened Reference Model)
 * @author EslaM-X Protocol Architect
 * @notice Formalizes 10M:1 Credit Expansion with Hardened Exit Throttling Logic (Deterministic Spec).
 */
contract PiRC101Vault {
    // --- Constants ---
    uint256 public constant QWF_MAX = 10_000_000; // 10 Million Multiplier
    uint256 public constant EXIT_CAP_PPM = 1000; // 0.1% Daily Exit Limit

    // --- State Variables ---
    struct GlobalState {
        uint256 totalReserves; // External Pi Locked
        uint256 totalREF;      // Total Internal Credits Minted
        uint256 lastExitTimestamp;
        uint256 dailyExitAmount;
    }

    GlobalState public systemState;
    mapping(address => mapping(uint8 => uint256)) public userBalances;
    
    // Provenance Invariant Psi: Track Mined vs External Status
    mapping(address => bool) public isSnapshotWallet;

    // --- Events ---
    event CreditExpanded(address indexed user, uint256 piDeposited, uint256 refMinted, uint256 phi);
    event CreditThrottledExit(address indexed user, uint256 refBurned, uint256 piWithdrawn, uint256 remainingCap);

    /**
     * @notice Deposits External Pi and Mints Internal REF Credits.
     */
    function depositAndMint(uint256 _amount, uint8 _class) external {
        require(_amount > 0, "Amount must be greater than zero");
        
        // --- Mock Oracle Data (Decentralized Aggregation Required for Production) ---
        uint256 piPrice = 314000; // $0.314 (scaled to 6 decimals)
        uint256 currentLiquidity = 10_000_000 * 1e6; // $10M Market Depth (scaled to 6 decimals)

        // --- Calculate Phi (The Throttling Coefficient) ---
        uint256 phi = calculatePhi(currentLiquidity, systemState.totalREF);
        
        // --- Insolvency Guardrail Check ---
        require(phi > 0, "Minting Paused: External Solvency Guardrail Activated.");

        // --- Expansion Logic ---
        uint256 capturedValue = (_amount * piPrice) / 1e6;
        
        // Provenance Logic: Direct snapshot wallet usage receives higher weight (Placeholder 1.0 vs 10M)
        uint256 wcf = 1e18; // 1.0 default
        if (isSnapshotWallet[msg.sender]) {
            wcf = 1e25; // Placeholder for high mined Pi weight
        }

        uint256 mintAmount = (capturedValue * QWF_MAX * phi * wcf) / 1e36;

        // --- Update State ---
        systemState.totalReserves += _amount;
        systemState.totalREF += mintAmount;
        userBalances[msg.sender][_class] += mintAmount;

        emit CreditExpanded(msg.sender, _amount, mintAmount, phi);
    }

    /**
     * @notice Pure, deterministic calculation of the Phi guardrail invariant.
     */
    function calculatePhi(uint256 _depth, uint256 _supply) public pure returns (uint256) {
        if (_supply == 0) return 1e18; // 1.0 (Full Expansion)
        uint256 ratio = (_depth * 1e18) / _supply; // simplified 1:1 QWF scaling assumption
        if (ratio >= 1.5e18) return 1e18; // Healthy threshold (Gamma = 1.5)
        return (ratio * ratio) / 2.25e18; // Quadratic Throttling (ratio^2 / Gamma^2)
    }

    // --- 🚨 NEW: HARDENED EXIT THROTTLING LOGIC 🚨 ---

    /**
     * @notice Conceptual Function for Withdrawal/Exit. Demonstrates the exit throttling mechanism.
     * @param _refAmount REF Credits user wants to liquidate.
     * @param _class Target utility class.
     * @return piOut The actual Pi value (scaled Conceptual USD Value) to be conceptualized as withdrawn.
     */
    function conceptualizeWithdrawal(uint256 _refAmount, uint8 _class) external returns (uint256 piOut) {
        require(userBalances[msg.sender][_class] >= _refAmount, "Insufficient REF balance");

        // --- Mock Oracle Data ---
        uint256 piPrice = 314000; // $0.314 (scaled to 6 decimals)
        uint256 currentLiquidity = 10_000_000 * 1e6; // $10M Market Depth

        // --- Dynamic State Update: Calculate remaining exit cap ---
        uint256 currentTime = block.timestamp;
        if (currentTime >= systemState.lastExitTimestamp + 1 days) {
            systemState.lastExitTimestamp = currentTime;
            systemState.dailyExitAmount = 0; // Reset daily counter
        }

        // Available Exit Door (USD Depth * EXIT_CAP_PPM / 1e6)
        uint256 availableDailyDoorUsd = (currentLiquidity * EXIT_CAP_PPM) / 1e6;
        uint256 remainingDailyUsdCap = availableDailyDoorUsd > systemState.dailyExitAmount ? availableDailyDoorUsd - systemState.dailyExitAmount : 0;

        // --- Conceptual Conversion and Throttling ---
        // 1. Conceptualize REF USD Value: Assume 1 Pi always buys fixed USD conceptual value
        // Note: For a true stable system, 1 REF would target a fixed USD peg (e.g., $1/10M), which is missing in this view.
        // For simplicity, we just convert the raw Pi value captured earlier.
        uint256 refUsdConceptualValue = (_refAmount * piPrice) / (QWF_MAX * 1e6); // Simplified

        // 2. Apply Throttling based on Remaining Daily USD Cap
        uint256 allowedRefUsdValue = _refAmount <= QWF_MAX ? refUsdConceptualValue : remainingDailyUsdCap;
        piOut = (allowedRefUsdValue * 1e6) / piPrice; // Conceptualized Pi out

        // 3. Final Invariant Solvency Check: Can the available exit door absorb this exit?
        // This is where Phi's twin operates at the exit door. If too many REF try to crowd through, they get throttled.
        if (refUsdConceptualValue > allowedRefUsdValue) {
            // Extreme Throttling scenario: User gets back less conceptualized Pi.
            piOut = (allowedRefUsdValue * 1e6) / piPrice;
        }

        // --- Execute Updates ---
        userBalances[msg.sender][_class] -= _refAmount;
        systemState.totalREF -= _refAmount; // REF is conceptually burned
        
        systemState.totalReserves -= piOut; // Solvency drain from Reserves conceptualized
        systemState.dailyExitAmount += allowedRefUsdValue;

        emit CreditThrottledExit(msg.sender, _refAmount, piOut, remainingDailyUsdCap);
    }
}
