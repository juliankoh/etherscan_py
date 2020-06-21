# etherscan_py

Powerful Python wrapper over Etherscan API for data collection. 

## Description 

The Etherscan API has various inconsistencies between the endpoints such as encoding of values (hex vs base10) as well as the structure of data returned. This module simplifies and standardizes the structure of data that gets returned from Etherscan, as well as provides performance improvements such as parallelization in queries.

## Installation

To install the package, simply run the following command:

```
pip install etherscan_py
```

## Usage

To use the package, initialize a client with your Etherscan API key. 

```
from etherscan_py import etherscan_py
client = etherscan_py.Client(YOUR_API_KEY)
```

## Data Structures

The basic Etherscan Event data structure.

```
class EtherscanEvent:
    address: string
    topics: [string]
    data: string
    block_height: int
    timestamp: int
    gas_price: int
    gas_used: int
    logindex: int
    txhash: string
```

The basic Etherscan Event data structure, with additional information from the associated transaction that caused the event to be emitted. 

```
class EnrichedEvent(EtherscanEvent):
    address: string
    topics: [string]
    data: string
    block_height: int
    timestamp: int
    gas_price: int
    gas_used: int
    logindex: int
    txhash: string
    from_address: string
    to_address: string
    tx_input: string
    nonce: int
    position_in_block: int
    value: int
```

The basic Etherscan Transaction data structure. 

```
class EtherscanTransaction:
    txhash: string
    block_height: int
    timestamp: int
    nonce: int
    from_address: string
    to_address: string
    value: int
    gas_price: int
    tx_input: string
    position_in_block: int
    is_error: bool
```

## Methods


These are the supported methods:

1. `get_eth_price()`
	```
	>>> client.get_eth_price()
	>>> 229.16
	```
2. `get_latest_block_height()`
	```
	>>> client.get_latest_block_height()
	>>> 10309928
	```
3. `get_first_tx_block(address)`
	```
	>>> client.get_first_tx_block('0x27054b13b1B798B345b591a4d22e6562d47eA75a')
	>>> 4352086
	```
4. `get_tx_by_hash(txhash)`
	```
	>>> res = client.get_tx_by_hash('0xb8b56002413bb6b8a0fbf7f986715a297d678ecfc4fdcd0b37d9a88048e5c68e')
	>>> res.txhash
	>>> '0xb8b56002413bb6b8a0fbf7f986715a297d678ecfc4fdcd0b37d9a88048e5c68e'
	```
5. `get_all_events(address, topic, enriched_data=False, from_block=0, to_block='latest', thread_count=1)`
	```
	>>> res = client.get_all_events(
		address = '0x51c72befae54d365a9d0c08c486aee4f99285e08',
		topic = '0x56f54e5e291f84831023c9ddf34fe42973dae320af11193db2b5f7af27719ba6'		
	)
	>>> len(res)
	>>> 72
	```

6. `get_all_transactions(from_address, status, to_address='', fn_signature='', from_block=0, to_block='latest', thread_count=1)`
	
	status is either 0,1 or 2. 
        0: Failed
        1: Successful
        2: Both

	fn_signature is the first 10-characters of a tx's input_data 

	```
	>>> res = client.get_all_transactions(
		from_address = '0x274CeA454c35b6bB3fE07377E719e45dF9E3Cac6',
		status = 2,
		to_address = '0x51c72befae54d365a9d0c08c486aee4f99285e08'
	)
	>>> len(res)
	>>> 14
	```
