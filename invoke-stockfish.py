stockfish_location = ''


########### CODE BEGINS HERE ###########
import websocket,json,requests,re,time,sys,random,threading,stockfish,argparse
print('[=] loading stockfish')
try:sf=stockfish.Stockfish(path=stockfish_location,depth=15,parameters={"Threads":3})
except:print('[-] stockfish failed to load'); quit()

p = argparse.ArgumentParser()
p.add_argument('-u',help='username')
p.add_argument('-g',help='game id/url')
args = p.parse_args()

if not (args.u or args.g): print('[-] need either username or game id'); quit()

if args.u:
    print('[=] fetching %s\'s ongoing game'%args.u)
    try:r=requests.get('https://lichess.org/api/user/%s/current-game'%args.u).text;u=re.findall('https://lichess.org/.{8}',r)[0]
    except:print('[-] no current game or invalid user');quit()
    print('[+] obtained game url: %s'%u)
else: 
    args.g=args.g.split('/')[-1]
    u='https://lichess.org/%s'%args.g
    print('[=] looking up game url: %s'%u)
    try:r=requests.get(u);assert r.status_code==200;u=args.g[:8]
    except:print('[-] game not found');quit()
    print('[+] game found')
    
def az(p,s,f):
    sf.set_fen_position(f)
    e,b=sf.get_evaluation(),sf.get_best_move()
    if e['type']=='mate' and not e['value']:eg()
    c,n=sf.will_move_be_a_capture(b),str(sf.get_what_is_on_square(b[:2])).split('_')[-1]
    print('{:13s}\teval: {:s}\tbest: {:s}'.format('%s%s. %s%s'%('' if p%2 else '\t\t\t\t\t\t',(p+1)//2,'' if p%2 else '...',s),('+' if e['value']>0 else '-')+('M' if e['type']=='mate' else '')+str(e['value'] if e['type']=='mate' else e['value']/100).lstrip('-'),(('' if c==sf.Capture.NO_CAPTURE else b[0]) if n == 'PAWN' else 'N' if n == 'KNIGHT' else n[0])+('' if c==sf.Capture.NO_CAPTURE else 'x')+b[2:]))
def om(ws,m):
    try:assert m!="0";j=json.loads(m)
    except:return
    if j['t']=='endData':eg()
    elif j['t']=='move':p=j['d']['ply'];az(p,j['d']['san'],j['d']['fen']+' '+('b' if p%2 else 'w'))
def o(ws):print('[+] connected\n');threading.Thread(target=h).start()
def eg():print('\n[=] game ended');quit()
def h():
    try:
        while 1:ws.send('null');time.sleep(10)
    except websocket._exceptions.WebSocketConnectionClosedException:return        

ws=websocket.WebSocketApp('wss://socket1.lichess.org/watch/%s/white/v6?sri=%s&v=4'%(u[-8:],''.join(random.choices('poiuytrewqlkjhgfdsamnbvcxzPOIUYTREWQLKJHGFDSAMNBVCXZ0987654321',k=12))),on_message=om,on_error=lambda a,b:None,on_close=lambda a,b,c:print('[=] closing connection\n'),on_open=o)
ws.run_forever(origin='https://lichess.org')

