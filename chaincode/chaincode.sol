// SPDX-License-Identifier: MIT
pragma solidity 0.8.22;
// EVM-Version => PARIS, otherwise it will not work properly!

contract ChainCode {

    string[] public strList;

    constructor() payable {}

    function addStr(string memory str) public {
        strList.push(str);
    }

    function getStrList() public view returns (string[] memory){
        return strList;
    }
}