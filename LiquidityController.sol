pragma solidity ^0.8.0;

contract LiquidityController {

    uint public totalLiquidity;

    event LiquidityAdded(uint amount);

    function addLiquidity(uint amount) public {

        totalLiquidity += amount;

        emit LiquidityAdded(amount);
    }

}
