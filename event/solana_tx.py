import solana
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solana.transaction import Transaction
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from spl.token.instructions import TransferCheckedParams, transfer_checked
from spl.token.constants import TOKEN_PROGRAM_ID
import os
from solana.rpc.api import Client
from solders.keypair import Keypair

solana_client = Client("https://solana-devnet.g.alchemy.com/v2/egGF-dWcAHcKoH2gQgOnMa2XbtHJfQkD") 

private_key = "4LtgFaHZ1f8TVFiTwMpJUfogUiYu5JBomUcgop2TbYYszNExHM2aBakWuZykfUBx57sZVH9PdsQ5uFb2oGRorjmW"
account = Keypair.from_base58_string(private_key)
mint_address = "FX54WhzfPruhbmayknf2v7bVfLGbXJ3eYtdHV4nqR7Kx"


def transfer_spl_token(sender_account, recipient_address, amount, mint_address, decimals):
    recipient_pubkey = Pubkey(recipient_address)
    mint_pubkey = Pubkey(mint_address)

    # Fetch the associated token account of the recipient
    recipient_token_account = solana_client.get_token_accounts_by_owner(
        recipient_pubkey,
        {"mint": mint_pubkey}
    )

    if not recipient_token_account['result']['value']:
        raise ValueError("Recipient has no associated token account for this mint.")

    # Get the recipient's associated token account address
    recipient_token_account_address = Pubkey(
        recipient_token_account['result']['value'][0]['pubkey']
    )

    # Create transfer instruction
    transfer_instruction = transfer_checked(
        TransferCheckedParams(
            program_id=TOKEN_PROGRAM_ID,
            source=sender_account.public_key,
            mint=mint_pubkey,
            dest=recipient_token_account_address,
            owner=sender_account.public_key,
            amount=amount * (10 ** decimals),  # Adjust for decimals
            decimals=decimals,
        )
    )

    # Create transaction and sign it
    transaction = Transaction().add(transfer_instruction)
    response = solana_client.send_transaction(transaction, sender_account)

    return response
