* ComputeTotal function does not satisfy its specification
https://github.com/Azure-Samples/blockchain/blob/1b712d6d05cca8da17bdd1894de8c3d25905685d/blockchain-workbench/application-and-smart-contract-samples/defective-component-counter/ethereum/DefectiveComponentCounter.sol#L24-L39

  
As documented by its following specification, computeTotal funtion can only be called once. However, in the contract implementation, there is no such restriction.
https://github.com/Azure-Samples/blockchain/blob/1b712d6d05cca8da17bdd1894de8c3d25905685d/blockchain-workbench/application-and-smart-contract-samples/defective-component-counter/ethereum/DefectiveComponentCounter.json#L73-L99

* Bug repair
We can fix such bug using the following statement.
```solidity
   // call this function to send a request
    function ComputeTotal() public
    {
        // Fix
        if (State != StateType.Create)
        {
            revert();
        }
       ...
```