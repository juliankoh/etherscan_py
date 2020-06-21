#!/usr/bin/env python
import pytest
from etherscan_py import etherscan_py
import IPython

API_KEY = 'TGYHIR4U6CVPVZ1G14TI27JWINF25XFNVB'

client = etherscan_py.Client(API_KEY)

def test_get_all_transactions():
    address = '0x274CeA454c35b6bB3fE07377E719e45dF9E3Cac6'
    topic = '0x56f54e5e291f84831023c9ddf34fe42973dae320af11193db2b5f7af27719ba6'
    to_block = 10269416
    to_address = '0x51c72befae54d365a9d0c08c486aee4f99285e08'

    # Successful Transactions
    results = client.get_all_transactions(address, 2,"", "", 0, to_block, 1)
    assert len(results) == 32

    # Failed Transactions
    results = client.get_all_transactions(address, 0,"", "", 0, to_block, 1)
    assert len(results) == 8

    # Both Failed and Successful Transactions
    results = client.get_all_transactions(address, 1,"", "", 0, to_block, 1)
    assert len(results) == 24

    # Specify to_address
    results = client.get_all_transactions(address, 2, to_address, "", 0, to_block, 1)
    assert len(results) == 14

def test_get_all_events():
    contract_address = '0x51C72bEfAe54D365A9D0C08C486aee4F99285e08'
    topic = '0x56f54e5e291f84831023c9ddf34fe42973dae320af11193db2b5f7af27719ba6'
    from_block = 10268572
    to_block = 10268580

    results = client.get_all_events(contract_address, topic, True, from_block, to_block, 1)
    assert len(results) == 1
    assert results[0].from_address == '0xc16b2934a204cc5a7e9ed79e253e4aced4cd2478'
    assert results[0].to_address == '0x51c72befae54d365a9d0c08c486aee4f99285e08'
    assert results[0].position_in_block == 0

def test_get_first_tx_block():
    contract_address = "0x064409168198A7E9108036D072eF59F923dEDC9A"
    block = client.get_first_tx_block(contract_address)
    assert block == 7186427

    contract_address = "0x3fda67f7583380e67ef93072294a7fac882fd7e7"
    block = client.get_first_tx_block(contract_address)
    assert block == 6400278

    contract_address = "0x51c72befae54d365a9d0c08c486aee4f99285e08"
    block = client.get_first_tx_block(contract_address)
    assert block == 9983296

def test_get_latest_block_height():
    height = client.get_latest_block_height()
    assert type(height) == int

def test_get_tx_by_hash():
    txhash = '0xf217ba9ff27b611fca8ded2ad3bbd581a604bcfe38bbe38c0426bcbdfcfc8aac'
    client.get_tx_by_hash(txhash)