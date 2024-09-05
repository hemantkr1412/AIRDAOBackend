from rest_framework.decorators import api_view
from rest_framework.response import Response
from web3 import Web3
from xenplay_backend.config import config
import json
import os
from django.conf import settings


def get_web3():
    return Web3(Web3.HTTPProvider(config["WEB3_PROVIDER"]))


def get_contract():
    web3 = get_web3()
    contract_filepath = os.path.join(settings.BASE_DIR, "event/contract_abi.json")
    with open(contract_filepath, "r") as file:
        contract_json = json.load(file)
    abi = contract_json["abi"]
    return web3.eth.contract(config["contract_address"], abi=abi)


def create_event(eventId, title, outcomes):

    if not title or not outcomes:
        return Response({"error": "Title and outcomes are required."}, status=400)
    account = config["public_key"]
    private_key = config["private_key"]
    contract = get_contract()
    w3 = get_web3()
    try:
        transaction = contract.functions.createEvent(eventId, title, outcomes).build_transaction(
            {
                "from": account,
                "nonce": w3.eth.get_transaction_count(account),
                "gasPrice": w3.eth.gas_price,
            }
        )
        signed_tx = w3.eth.account.sign_transaction(transaction, private_key)

        # Send the transaction
        tx = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx)
        print(tx_receipt)
        tx_hash = tx_receipt["transactionHash"].hex()
        # Capture the emitted `EventCreated` event
        # event_filter = contract.events.EventCreated.create_filter(
        #     from_block=tx_receipt["blockNumber"], to_block=tx_receipt["blockNumber"]
        # )
        # print("event filter", event_filter)
        # events = event_filter.get_new_entries()
        # print("events",events)
        # event_id = events[0]['args']['eventId']
        # event_id = contract.functions.eventCount().call() - 1
        # print(event_id)
        # for event in events:
        #     event_id = event["args"]["eventId"]
        #     print(
        #         f"Event received: Event ID: {event['args']['eventId']}, Title: {event['args']['title']}, Outcomes: {event['args']['outcomes']}, IsActive: {event['args']['isActive']}"
        #     )
        # return {"tx_hash": tx_hash}
        return tx_hash
    except Exception as e:
        print("exception raise while calling create_event ", e)


@api_view(["POST"])
def update_event(request, event_id):
# def update_event(event_id):
    contract = get_contract()
    web3 = get_web3()
    account = config["public_key"]
    private_key = config["private_key"]
    nonce = web3.eth.get_transaction_count(account)
    transaction = contract.functions.updateEvent(event_id).build_transaction(
        {
            "nonce": nonce,
            "gasPrice": web3.eth.gas_price,
            "from": account,
        }
    )
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
    txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(txn_hash)
    print(tx_receipt)
    tx_hash = tx_receipt["transactionHash"].hex()
    # return tx_hash
    return Response({"transaction_hash": tx_hash})


def close_event(event_id, outcome_id):
    contract = get_contract()
    web3 = get_web3()
    account = config["public_key"]
    private_key = config["private_key"]
    nonce = web3.eth.get_transaction_count(account)
    try:
        # Simulate the transaction to catch errors before sending
        contract.functions.closeEvent(event_id, outcome_id).call({"from": account})

        # Build and sign the transaction
        transaction = contract.functions.closeEvent(
            event_id, outcome_id
        ).build_transaction(
            {
                "nonce": nonce,
                "gasPrice": web3.eth.gas_price,
                "from": account,
            }
        )
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
        txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)

        # Wait for transaction receipt
        tx_receipt = web3.eth.wait_for_transaction_receipt(txn_hash)
        tx_hash = tx_receipt["transactionHash"].hex()
        return tx_hash
    except Exception as e:
        print("Transaction failed:", e)


def claim_amount(amount, address):
    winner_address = Web3.to_checksum_address(address)
    contract = get_contract()
    web3 = get_web3()
    account = config["public_key"]
    private_key = config["private_key"]
    nonce = web3.eth.get_transaction_count(account)
    eth_ammount =  amount * (10 ** 18)
    try:
        transaction = contract.functions.withdrawAmount(
            int(eth_ammount), winner_address
        ).build_transaction(
            {
                "nonce": nonce,
                "gasPrice": web3.eth.gas_price,
                "from": account,
            }
        )
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
        txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(txn_hash)
        tx_hash = tx_receipt["transactionHash"].hex()
        return tx_hash
    except Exception as e:
        print("Transaction failed:", e)


@api_view(["GET"])
def check_contract_balance(request):
    contract = get_contract()
    balance = contract.functions.checkContractBal().call()
    return Response({"balance": balance})


@api_view(["POST"])
def change_owner(request):
    contract = get_contract()
    web3 = get_web3()
    new_owner = request.data["new_owner"]
    account = config["public_key"]
    private_key = config["private_key"]
    nonce = web3.eth.get_transaction_count(account)
    transaction = contract.functions.changeOwner(new_owner).build_transaction(
        {
            "nonce": nonce,
            "gasPrice": web3.eth.gas_price,
            "from": account,
        }
    )
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
    txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(txn_hash)
    print(tx_receipt)
    return Response({"transaction_hash": txn_hash})


@api_view(["GET"])
def get_outcome_info(request, event_id):
    contract = get_contract()
    titles, vote_counts = contract.functions.getOutcomeInfo(event_id).call()
    return Response({"titles": titles, "vote_counts": vote_counts})


@api_view(["GET"])
def get_user_prediction(request, event_id, outcome_id, user_address):
    contract = get_contract()
    prediction = contract.functions.getUserPrediction(
        event_id, outcome_id, user_address
    ).call()
    return Response({"prediction": prediction})


@api_view(["GET"])
def get_owner(request):
    contract = get_contract()
    owner = contract.functions.getOwner().call()
    return Response({"owner": owner})
