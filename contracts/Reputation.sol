// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract Reputation {

    struct Update {
        uint round;
        uint clientId;
        string cid;
        string proofHash;
        uint accuracy;
        bool verified;
    }

    mapping(uint => uint) public reputation;
    Update[] public updates;

    event UpdateSubmitted(
        uint round,
        uint clientId,
        string cid,
        uint accuracy
    );

    event UpdateVerified(
        uint round,
        uint clientId,
        bool result
    );

    // =============================
    // Client submit model update
    // =============================
    function submitUpdate(
        uint round,
        uint clientId,
        string memory cid,
        string memory proofHash,
        uint accuracy
    ) public {

        updates.push(
            Update(
                round,
                clientId,
                cid,
                proofHash,
                accuracy,
                false
            )
        );

        emit UpdateSubmitted(
            round,
            clientId,
            cid,
            accuracy
        );
    }

    // =============================
    // Server verify update
    // =============================
    function verifyUpdate(
        uint clientId,
        uint round,
        bool result
    ) public {

        for (uint i = 0; i < updates.length; i++) {

            if (
                updates[i].clientId == clientId &&
                updates[i].round == round
            ) {

                updates[i].verified = result;

                if (result) {
                    reputation[clientId] += 1;
                } else {

                    if (reputation[clientId] > 0) {
                        reputation[clientId] -= 1;
                    }

                }

                emit UpdateVerified(
                    round,
                    clientId,
                    result
                );

                break;
            }
        }
    }

    // =============================
    // Get reputation
    // =============================
    function getReputation(uint clientId)
        public
        view
        returns (uint)
    {
        return reputation[clientId];
    }

    // =============================
    // Get all updates
    // =============================
    function getUpdates()
        public
        view
        returns (Update[] memory)
    {
        return updates;
    }
}