* Constructor function does not satisfy its specification
https://github.com/Azure-Samples/blockchain/blob/1b712d6d05cca8da17bdd1894de8c3d25905685d/blockchain-workbench/application-and-smart-contract-samples/digital-locker/ethereum/DigitalLocker.sol#L18-L24

As documented by its following specification, Constructor funtion should finish with `Requested` state instead of `DocumentReview`.

https://github.com/Azure-Samples/blockchain/blob/1b712d6d05cca8da17bdd1894de8c3d25905685d/blockchain-workbench/application-and-smart-contract-samples/digital-locker/ethereum/DigitalLocker.json#L31

* Other implementation bugs according to contract specification.
https://github.com/Azure-Samples/blockchain/blob/1b712d6d05cca8da17bdd1894de8c3d25905685d/blockchain-workbench/application-and-smart-contract-samples/digital-locker/ethereum/DigitalLocker.json#L272-L421

1. BeginReviewProcess function should begin with `Requested` state.
https://github.com/Azure-Samples/blockchain/blob/1b712d6d05cca8da17bdd1894de8c3d25905685d/blockchain-workbench/application-and-smart-contract-samples/digital-locker/ethereum/DigitalLocker.sol#L29

2. UploadDocuments function should begin with `DocumentReview` state.
https://github.com/Azure-Samples/blockchain/blob/1b712d6d05cca8da17bdd1894de8c3d25905685d/blockchain-workbench/application-and-smart-contract-samples/digital-locker/ethereum/DigitalLocker.sol#L56

3. ShareWithThirdParty should begin with `AvailableToShare` state.
https://github.com/Azure-Samples/blockchain/blob/1b712d6d05cca8da17bdd1894de8c3d25905685d/blockchain-workbench/application-and-smart-contract-samples/digital-locker/ethereum/DigitalLocker.sol#L68

4. AcceptSharingRequest should begin with `SharingRequestPending` state.
https://github.com/Azure-Samples/blockchain/blob/1b712d6d05cca8da17bdd1894de8c3d25905685d/blockchain-workbench/application-and-smart-contract-samples/digital-locker/ethereum/DigitalLocker.sol#L84

5. RejectSharingRequest should begin with `SharingRequestPending` state.
https://github.com/Azure-Samples/blockchain/blob/1b712d6d05cca8da17bdd1894de8c3d25905685d/blockchain-workbench/application-and-smart-contract-samples/digital-locker/ethereum/DigitalLocker.sol#L95

6. RequestLockerAccess should begin with `AvailableToShare` state.
https://github.com/Azure-Samples/blockchain/blob/1b712d6d05cca8da17bdd1894de8c3d25905685d/blockchain-workbench/application-and-smart-contract-samples/digital-locker/ethereum/DigitalLocker.sol#L106

7. ReleaseLockerAccess should begin with `SharingWithThirdParty` state.
https://github.com/Azure-Samples/blockchain/blob/1b712d6d05cca8da17bdd1894de8c3d25905685d/blockchain-workbench/application-and-smart-contract-samples/digital-locker/ethereum/DigitalLocker.sol#118

8. RevokeAccessFromThirdParty should begin with `SharingWithThirdParty` state.
https://github.com/Azure-Samples/blockchain/blob/1b712d6d05cca8da17bdd1894de8c3d25905685d/blockchain-workbench/application-and-smart-contract-samples/digital-locker/ethereum/DigitalLocker.sol#L132 

9. Terminate should begin with `AvailableToShare|SharingRequestPending|SharingWithThirdParty` state.
https://github.com/Azure-Samples/blockchain/blob/1b712d6d05cca8da17bdd1894de8c3d25905685d/blockchain-workbench/application-and-smart-contract-samples/digital-locker/ethereum/DigitalLocker.sol#L143
