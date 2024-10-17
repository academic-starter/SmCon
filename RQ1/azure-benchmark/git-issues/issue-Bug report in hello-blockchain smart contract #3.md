* SendRequest and SendResponse do not satisfy its specifications.
https://github.com/Azure-Samples/blockchain/blob/1b712d6d05cca8da17bdd1894de8c3d25905685d/blockchain-workbench/application-and-smart-contract-samples/hello-blockchain/HelloBlockchain.sol#L25-L34


https://github.com/Azure-Samples/blockchain/blob/1b712d6d05cca8da17bdd1894de8c3d25905685d/blockchain-workbench/application-and-smart-contract-samples/hello-blockchain/HelloBlockchain.sol#L37-L44

As documented by its following specification, SendRequest is only available when previous message has been responded, a.k.a., `Respond` state while SendResponse is only available when there is a request message, a.k.a., `Request` state.

https://github.com/Azure-Samples/blockchain/blob/1b712d6d05cca8da17bdd1894de8c3d25905685d/blockchain-workbench/application-and-smart-contract-samples/hello-blockchain/HelloBlockchain.json#L108-L147
