import simplejson as json 

def list_all_repeat_entrys(traces: list):
    repeats = list()
    for trace in traces:
        event_trace = trace["event_trace"]
        entry_method = event_trace[0]["methodName"]
        if len(event_trace) >= 2:
            second_method = event_trace[1]["methodName"]
            if entry_method == second_method:
                repeats.append(trace)
        # for index in range(1, len(event_trace)):
        #     _trace = event_trace[index]
        #     if entry_method == _trace["methodName"]:
        #         repeats.append(trace)
        #         break
    return repeats

def list_all_non_entrys(traces: list, entrys: list):
    results = list()
    for trace in traces:
        event_trace = trace["event_trace"]
        entry_method = event_trace[0]["methodName"].split("(")[0]
        if entry_method not in entrys:
            results.append(trace)
    return results

def list_all_null_entry_poststate(traces: list):
    results = list()
    for trace in traces:
        event_trace = trace["event_trace"]
        entry_method = event_trace[0]["methodName"].split("(")[0]
        state_trace = trace["state_trace"]
        post_state = state_trace[1]
        if all([item["value"] is None for item in post_state]):
            results.append(trace)
    return results


def list_all_repeat_serverEndGame(traces: list):
    repeats = list()
    for trace in traces:
        event_trace = trace["event_trace"]
        methods: list = []
        for index in range(0, len(event_trace)):
            _trace = event_trace[index]
            method = _trace["methodName"].split("(")[0]
            methods.append(method)
        
        if methods.count("serverEndGame")>1:
            repeats.append(trace)
               
    return repeats

def list_all_repeat_txs(contract_artifact: dict):
    repeats = list()
    transactions = contract_artifact["transactions"]
    transaction_hash = None 
    for transaction in transactions:
        first_item  = transaction[0]
        if transaction_hash ==  first_item["transactionHash"]:
            repeats.append(transaction_hash)
        transaction_hash = first_item["transactionHash"]
    return repeats


if __name__ == "__main__":
    # traces_file = "Dapp-Automata-data/result/0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb-CryptoPunksMarket-trace_slices.json"
    # traces = json.load(open(traces_file))
    # repeats = list_all_repeat_entrys(traces)
    # print(json.dumps(repeats, indent=4))

    # contract_artifact_file = "tmp/0xeb6f4ec38a347110941e86e691c2ca03e271df3b.json"
    # contract_artifact = json.load(open(contract_artifact_file))
    # repeats = list_all_repeat_txs(contract_artifact)
    # print(json.dumps(repeats, indent=4))

    # traces_file = "Dapp-Automata-data/result/0x1f52b87c3503e537853e160adbf7e330ea0be7c4-SaleClockAuction-trace_slices.json"
    # traces = json.load(open(traces_file))
    # repeats = list_all_repeat_entrys(traces)
    # print(json.dumps(repeats, indent=4))

    # contract_artifact_file = "tmp/0x1f52b87c3503e537853e160adbf7e330ea0be7c4.json"
    # contract_artifact = json.load(open(contract_artifact_file))
    # repeats = list_all_repeat_txs(contract_artifact)
    # print(json.dumps(repeats, indent=4))


    # traces_file = "Dapp-Automata-data/result/0xeb6f4ec38a347110941e86e691c2ca03e271df3b-GameChannel-trace_slices.json"
    # traces = json.load(open(traces_file))
    # repeats = list_all_repeat_serverEndGame(traces)
    # print(json.dumps(repeats, indent=4))


    traces_files = ["Dapp-Automata-data/result/0x41a322b28d0ff354040e2cbc676f0320d8c8850d-SupeRare-trace_slices.json", "Dapp-Automata-data/result/0x1f52b87c3503e537853e160adbf7e330ea0be7c4-SaleClockAuction-trace_slices.json", "Dapp-Automata-data/result/0x60cd862c9c687a9de49aecdc3a99b74a4fc54ab6-MoonCatRescue-trace_slices.json", "Dapp-Automata-data/result/0xa8f9c7ff9f605f401bde6659fd18d9a0d0a802c5-RpsGame-trace_slices.json", "Dapp-Automata-data/result/0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb-CryptoPunksMarket-trace_slices.json"]
    for traces_file in traces_files:
        # traces_file = "Dapp-Automata-data/result/0x41a322b28d0ff354040e2cbc676f0320d8c8850d-SupeRare-trace_slices.json"
        print(traces_file)
        traces: list = json.load(open(traces_file))
        print("total traces number:", len(traces))
        repeats = list_all_repeat_entrys(traces)
        print(len(repeats), " traces starting with repated entry method")
        print(json.dumps(repeats, indent=4))

        results = list_all_null_entry_poststate(traces)
        print(len(results), " traces starting with null post state")
        # print(json.dumps(results, indent=4))
        for null_trace in results:
            traces.remove(null_trace)
        json.dump(traces, open(traces_file.replace(".json", ".clean.json"), "w"), indent=4)
