pragma solidity ^0.4.20;

contract SimpleMarketplace /* is WorkbenchBase('SimpleMarketplace', 'SimpleMarketplace') */
{
    enum StateType { 
      ItemAvailable,
      OfferPlaced,
      Accepted
    }

    address public InstanceOwner;
    string public Description;
    int public AskingPrice;
    StateType public State;

    address public InstanceBuyer;
    int public OfferPrice;

    function SimpleMarketplace(string description, int price) public
    {
        InstanceOwner = msg.sender;
        AskingPrice = price;
        Description = description;
        State = StateType.ItemAvailable;
        // ContractCreated();
    }

    function MakeOffer(int offerPrice) public
    {
        if (offerPrice == 0)
        {
            revert();
        }

        if (State != StateType.ItemAvailable)
        {
            revert();
        }
        
        if (InstanceOwner == msg.sender)
        {
            revert();
        }

        InstanceBuyer = msg.sender;
        OfferPrice = offerPrice;
        State = StateType.OfferPlaced;
        // ContractUpdated('MakeOffer');
    }

    function Reject() public
    {
        if ( State != StateType.OfferPlaced )
        {
            revert();
        }

        if (InstanceOwner != msg.sender)
        {
            revert();
        }

        InstanceBuyer = 0x0;
        State = StateType.ItemAvailable;
        // ContractUpdated('Reject');
    }

    function AcceptOffer() public
    {
        // Fix: AcceptOffer is available only in StateType.OfferPlaced
        if ( State != StateType.OfferPlaced ){
            revert();
        }

        if ( msg.sender != InstanceOwner )
        {
            revert();
        }

        State = StateType.Accepted;
        // ContractUpdated('AcceptOffer');
    }
}