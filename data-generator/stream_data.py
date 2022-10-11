from websocket import create_connection
import json
import click
import requests

#post JSON data to Tinybird Events API
def send_event(ds: str, token: str, messages: list, host: str):
  params = {
    'name': ds,
    'token': token,
    'wait': 'false',
    'host': host,
  }
  data = '\n'.join(json.dumps(m) for m in messages)
  r = requests.post(f'{host}/v0/events', params=params, data=data)
  #uncomment the following two lines in case you don't see your data in the datasource
  #print(r.status_code)
  #print(r.text)

@click.command()
@click.option('--datasource', help = 'the destination datasource. Default = stocks_stream', default='stocks_stream')
@click.option('--symbols', help = "The comma-separated symbols to query for. Default = AAPL", default='AAPL')
@click.option('--events', help = 'number of events per request. Sent as NDJSON in the body. Default = 50', type=int, default=50)
@click.option('--sample', help = 'number of messages simulated in each repetition. Default = 100000000', type=int, default=100000000)

def send_hfi(datasource,
             symbols,
             events,
             sample
             ):

    #token and host from Tinybird workspace
    with open ("./.tinyb") as tinyb:
        tb = json.load(tinyb)
        token = tb['token']
        host = tb['host']
    
    #key and secret from Alpaca account
    with open ("./.alpaca") as alpaca:
        al = json.load(alpaca)
        key = al['key']
        secret = al['secret']

    #connect to Alpaca Websocket
    url = 'wss://stream.data.alpaca.markets/v2/iex'
    ws = create_connection(url)
    print(json.loads(ws.recv()))

    #authorize
    auth_message = {"action": "auth", "key": key, "secret": secret}
    ws.send(json.dumps(auth_message))

    #subscribe to quotes
    subscription = {"action":"subscribe","quotes":symbols.split(',')}
    ws.send(json.dumps(subscription))
    print(json.loads(ws.recv()))

    for _ in range(sample):

        nd = []

        while len(nd) < (events + 1):
            data = json.loads(ws.recv())
            nd.append(data[0])

        nd.pop(0)
        print(nd)

        send_event(datasource, token, nd, host)
        nd = []

if __name__ == '__main__':
    send_hfi()