// SPDX-License-Identifier: MIT
pragma solidity ^0.8.22;

contract ChainCode {
    string[] storage public strList; // Storage variable

    function addStr(string memory str) public {
        strList.push(str); // Modifies storage
    }

    function getStrList() public view returns (string[] memory) {
        return strList; // Reads from storage
    }
}
