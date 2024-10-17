* AcceptOffer does not satisfy its specifications.
https://github.com/Azure-Samples/blockchain/blob/1b712d6d05cca8da17bdd1894de8c3d25905685d/blockchain-workbench/application-and-smart-contract-samples/simple-marketplace/ethereum/SimpleMarketplace.sol#L65-L73

As documented by its following specification, AcceptOffer is only available when at OfferPlaced state.
https://github.com/Azure-Samples/blockchain/blob/1b712d6d05cca8da17bdd1894de8c3d25905685d/blockchain-workbench/application-and-smart-contract-samples/simple-marketplace/ethereum/SimpleMarketplace.json#L139-L163


* Bug repair.
We can fix such bug by adding statements:
```solidity
    function AcceptOffer() public
    {
        // Fix
        if ( State != StateType.OfferPlaced ){
            revert();
        }
        ...
```
