// SPDX-License-Identifier: MIT
pragma solidity ^0.8.22;

contract ChainCode {
    string[] public strList; // Persistent storage variable

    function addStr(string memory str) public {
        strList.push(str); // Modifies storage
    }

    function getStrList() public view returns (string[] memory) {
        return strList; // Reads from storage
    }
}
