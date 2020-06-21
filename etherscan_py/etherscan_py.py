import requests
import IPython
import copy
from threading import Thread, Lock
import itertools
from toolz import partition

class EtherscanEvent:
    def __init__(self, event):
        self.address = event['address']
        self.topics = event['topics']
        self.data = event['data']
        self.block_height = int(event['blockNumber'], 16)
        self.timestamp = int(event['timeStamp'], 16)
        self.gas_price = int(event['gasPrice'], 16)
        self.gas_used = int(event['gasUsed'], 16)
        self.logindex = event['logIndex']
        self.txhash = event['transactionHash']
        self.txindex = event['transactionIndex']

class EnrichedEvent(EtherscanEvent):
    def __init__(self, event, transaction):
        super().__init__(event)
        self.from_address = transaction['from']
        self.to_address = transaction['to']
        self.tx_input = transaction['input']
        self.nonce = transaction['nonce']
        self.position_in_block = int(transaction['transactionIndex'], 16)
        self.value = int(transaction['value'], 16)

class EtherscanTransaction:
    def __init__(self, transaction):
        self.block_height = int(transaction['blockNumber'])
        self.timestamp = int(transaction['timeStamp'])
        self.nonce = transaction['nonce']
        self.from_address = transaction['from']
        self.to_address = transaction['to']
        self.value = int(transaction['value'])
        self.gas_price = int(transaction['gasPrice'])
        self.gas_used = int(transaction['gasUsed'])
        self.tx_input = transaction['input']
        self.position_in_block = int(transaction['transactionIndex'])
        self.is_error = self.is_error(transaction['isError'])

    def is_error(self, is_error):
        if is_error == '0':
            return False
        else:
            return True

def chunks(start, end, n):
    l = range(start, end+1)
    res = []

    d, r = divmod(len(l), n)
    for i in range(n):
        si = (d+1)*(i if i < r else r) + d*(0 if i < r else i - r)
        res.append(l[si:si+(d+1 if i < r else d)])
    
    return list(map(lambda x: (x[0], x[-1]),res))

class Client:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def get(self, module, action, extra_data=""):
        url = f"http://api.etherscan.io/api?module={module}&action={action}&{extra_data}&apikey={self.api_key}"
        r = requests.get(url)
        if r.status_code == 200:
            res = r.json()
            # Requests that are proxied to the JSON-RPC have different structure
            if module == 'proxy':
                return res['result']
            else:
                if res['status'] == '1':
                    return res['result']
                else:
                    raise Exception("Invalid Etherscan request")
        else:
            raise Exception("Invalid HTTP request")

    def get_eth_price(self):
        eth_price = self.get("stats", "ethprice")
        return int(eth_price['ethusd'])

    def get_latest_block_height(self):
        block = self.get("proxy", "eth_blockNumber")
        return int(block, 16)

    def get_first_tx_block(self, contract_address):
        extra_data = f"address={contract_address}&page=1&offset=1&sort=asc"
        res = self.get("account", "txlist", extra_data)
        block_number = int(res[0]['blockNumber'])
        return block_number

    def get_tx_by_hash(self, txhash):
        extra_data = f"txhash={txhash}&"
        res = self.get("proxy", "eth_getTransactionByHash", extra_data)
        return res

    def threaded_search(self, fn_name, address, from_block=0, to_block='latest', thread_count=1, **kwargs):    
        if from_block == 0:
            from_block = self.get_first_tx_block(address)
        
        if to_block == 'latest':
            to_block = self.get_latest_block_height()

        block_ranges = chunks(from_block, to_block, thread_count)
        lock = Lock()
        threads, lst = [], []

        for i in range(thread_count):
            s,e = block_ranges[i]
            t = Thread(target=self.threaded_search_lock, args=(fn_name, lst, address, from_block, to_block, lock, kwargs))
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        return list(itertools.chain(*lst))

    def threaded_search_lock(self, fn_name, lst, address, from_block, to_block, lock, args):
        results = fn_name(address, from_block, to_block, args)
        with lock:
            lst.append(results)
        return 


    def get_transactions(self, address, from_block, to_block, args, results_copy=[]):
        # 0 - Failed
        # 1 - Sucess
        # 2 - Both
        status = args['status']
        try:
            fn_signature = args['fn_signature']
        except KeyError:
            fn_signature = ""

        
        results = copy.copy(results_copy)
        last_height = from_block

        extra_data = f"address={address}&startblock={from_block}&endblock={to_block}&sort=asc"
        res = self.get("account", "txlist", extra_data)

        def add_to_results(tx):
            if fn_signature == "":
                results.append(EtherscanTransaction(tx))
            else:
                if len(tx['input']) > 10:
                    if tx['input'][:10] == fn_signature:
                        results.append(EtherscanTransaction(tx))

        for tx in res:
            if status == 2:
                add_to_results(tx)
            elif status == 1:
                if tx['isError'] == '0':
                    add_to_results(tx)
            else:
                if tx['isError'] == '1':
                    add_to_results(tx)

        if results == []:
            return results
        else:
            try:    
                last_height = results[-1].block_height
            except:
                raise Exception(f"Got bad response from Etherscan when querying logs for address {address}")

        # Max number of results returned in one query
        if len(res) != 1000:
            return results
        else:
            return get_events(address, last_height, to_block, args, results)


    def get_events(self, address, from_block, to_block, args, events_copy=[]):
        topic = args['topic']
        enriched_data = args['enriched_data']

        events = copy.copy(events_copy)
        last_height = from_block

        extra_data = f"fromBlock={from_block}&toBlock={to_block}&address={address}&topic0={topic}"
        res = self.get("logs", "getLogs", extra_data)

        for event in res:
            if enriched_data:
                transaction = self.get_tx_by_hash(event['transactionHash'])
                events.append(EnrichedEvent(event, transaction))
            else:
                events.append(EtherscanEvent(event))

        if events == []:
            return events
        else:
            try:    
                last_height = events[-1].block_height
            except:
                raise Exception(f"Got bad response from Etherscan when querying logs for address {address}")

        # Max number of results returned in one query
        if len(res) != 1000:
            return events
        else:
            return get_events(address, last_height, to_block, args, events)
