// SPDX-License-Identifier: MIT
pragma solidity 0.8.22;
// EVM-Version => PARIS, otherwise it will not work properly!

contract ChainCode {

    // persistent storage array, expensive in gas but dynamic in size
    string[] public strList;

    // contract can be loaded with ETH during deployment
    constructor() payable {}

    // public method persistently storing string
    function addStr(string memory str) public {
        strList.push(str);
    }

    // public method returning stored strings, free of gas since of type view
    function getStrList() public view returns (string[] memory){
        return strList;
    }
}