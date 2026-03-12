pragma solidity ^0.8.0;

contract PiRCToken {

    string public name = "PiRC Token";
    string public symbol = "PIRC";
    uint8 public decimals = 18;

    uint public totalSupply;

    mapping(address => uint) public balanceOf;

    event Transfer(address indexed from, address indexed to, uint value);

    function mint(address to, uint amount) public {
        balanceOf[to] += amount;
        totalSupply += amount;
        emit Transfer(address(0), to, amount);
    }

    function transfer(address to, uint amount) public {

        require(balanceOf[msg.sender] >= amount, "balance too low");

        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;

        emit Transfer(msg.sender, to, amount);
    }
}
