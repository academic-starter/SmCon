pragma solidity ^0.4.20;

contract DigitalLocker /* is WorkbenchBase('DigitalLocker', 'DigitalLocker') */
{
    enum StateType { Requested, DocumentReview, AvailableToShare, SharingRequestPending, SharingWithThirdParty, Terminated }
    address public Owner;
    address public BankAgent;
    string public LockerFriendlyName;
    string public LockerIdentifier;
    address public CurrentAuthorizedUser;
    string public ExpirationDate;
    string public Image;
    address public ThirdPartyRequestor;
    string public IntendedPurpose;
    string public LockerStatus;
    string public RejectionReason;
    StateType public State;

    function DigitalLocker(string lockerFriendlyName, address bankAgent) public
    {
        Owner = msg.sender;
        LockerFriendlyName = lockerFriendlyName;

        //State = StateType.DocumentReview; //////////////// should be StateType.Requested?
        // "StartState": "Requested",
        State = StateType.Requested;

        BankAgent = bankAgent;

        // ContractCreated();
    }

    function BeginReviewProcess() public
    {   
        // Fix
        if (State != StateType.Requested)
        {
            revert();
        }

        // Need to update, likely with registry to confirm sender is agent
        // Also need to add a function to re-assign the agent.
        if (Owner == msg.sender)
        {
            revert();
        }
        BankAgent = msg.sender;

        LockerStatus = 'Pending';
        State = StateType.DocumentReview;
        // ContractUpdated('BeginReviewProcess');
    }

    function RejectApplication(string rejectionReason) public
    {
       

        if (BankAgent != msg.sender)
        {
            revert();
        }

        RejectionReason = rejectionReason;
        LockerStatus = 'Rejected';
        State = StateType.DocumentReview;
        // ContractUpdated('RejectApplication');
    }

    function UploadDocuments(string lockerIdentifier, string image) public
    {
        // Fix
        if (State != StateType.DocumentReview)
        {
            revert();
        }

         if (BankAgent != msg.sender)
        {
            revert();
        }
            LockerStatus = 'Approved';
            Image = image;
            LockerIdentifier = lockerIdentifier;
            State = StateType.AvailableToShare;
            // ContractUpdated('UploadDocments');
    }

    function ShareWithThirdParty(address thirdPartyRequestor, string expirationDate, string intendedPurpose) public
    {
         // Fix
        if (State != StateType.AvailableToShare)
        {
            revert();
        }

        if (Owner != msg.sender)
        {
            revert();
        }

        ThirdPartyRequestor = thirdPartyRequestor;
        CurrentAuthorizedUser = ThirdPartyRequestor;

        LockerStatus = 'Shared' ;
        IntendedPurpose = intendedPurpose;
        ExpirationDate = expirationDate;
        State = StateType.SharingWithThirdParty;
        // ContractUpdated('ShareWithThirdParty');
    }

    function AcceptSharingRequest() public
    {
        // Fix
        if (State != StateType.SharingRequestPending)
        {
            revert();
        }

        if (Owner != msg.sender)
        {
            revert();
        }

        CurrentAuthorizedUser = ThirdPartyRequestor;
        State = StateType.SharingWithThirdParty;
        // ContractUpdated('AcceptSharingRequest');
    }

    function RejectSharingRequest() public
    {
        // Fix
        if (State != StateType.SharingRequestPending)
        {
            revert();
        }

        if (Owner != msg.sender)
        {
            revert();
        }
            LockerStatus = 'Available';
            CurrentAuthorizedUser = 0x0;
            State = StateType.AvailableToShare;
            // ContractUpdated('RejectSharingRequest');
    }

    function RequestLockerAccess(string intendedPurpose) public
    {
        // Fix
        if (State != StateType.AvailableToShare)
        {
            revert();
        }

        if (Owner == msg.sender)
        {
            revert();
        }

        ThirdPartyRequestor = msg.sender;
        IntendedPurpose = intendedPurpose;
        State = StateType.SharingRequestPending;
                // ContractUpdated('RequestLockerAccess');
    }

    function ReleaseLockerAccess() public
    {
        // Fix
        if (State != StateType.SharingWithThirdParty)
        {
            revert();
        }

        if (CurrentAuthorizedUser != msg.sender)
        {
            revert();
        }
        LockerStatus = 'Available';
        ThirdPartyRequestor = 0x0;
        CurrentAuthorizedUser = 0x0;
        IntendedPurpose = '';
        State = StateType.AvailableToShare;
        // ContractUpdated('AvailableToShare');
    }
    function RevokeAccessFromThirdParty() public
    {
        // Fix
        if (State != StateType.SharingWithThirdParty)
        {
            revert();
        }

        if (Owner != msg.sender)
        {
            revert();
        }
            LockerStatus = 'Available';
            CurrentAuthorizedUser = 0x0;
            State = StateType.AvailableToShare;
            // ContractUpdated('RevokeAccessFromThirdParty');
    }
    function Terminate() public
    {
         // Fix
        if (State != StateType.AvailableToShare && 
            State != StateType.SharingRequestPending && 
            State != StateType.SharingWithThirdParty
        )
        {
            revert();
        }

        if (Owner != msg.sender)
        {
            revert();
        }
        CurrentAuthorizedUser = 0x0;
        State = StateType.Terminated;
         // ContractUpdated('Terminate');
    }



}