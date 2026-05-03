// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FLRegistry {

    struct Update {
        uint round;
        uint clientId;
        string cid;
        string proofHash;
        bool verified;
    }

    Update[] public updates;

    mapping(uint => int) public reputation;

    event UpdateSubmitted(
        uint round,
        uint clientId,
        string cid
    );

    event ReputationUpdated(
        uint clientId,
        int reputation
    );

    function submitUpdate(
        uint round,
        uint clientId,
        string memory cid,
        string memory proofHash
    ) public {

        updates.push(Update(
            round,
            clientId,
            cid,
            proofHash,
            false
        ));

        emit UpdateSubmitted(round, clientId, cid);
    }

    function verifyUpdate(
        uint index,
        bool result
    ) public {

        updates[index].verified = result;

        if(result){
            reputation[updates[index].clientId] += 1;
        }
        else{
            reputation[updates[index].clientId] -= 1;
        }

        emit ReputationUpdated(
            updates[index].clientId,
            reputation[updates[index].clientId]
        );
    }

    function getReputation(uint clientId)
        public
        view
        returns(int)
    {
        return reputation[clientId];
    }
}