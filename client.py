#!/usr/bin/env python3

import os
import sys
import csv
import time
import json
import pprint
import socket
import argparse

HOSTNAME = "api.vndb.org"
PORT = 19534
BUFFER_SIZE = 2**14



class TCPSession:
    def __init__(self, hostname, port, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.sock.connect((hostname, port))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def send(self, msg):
        totalsent = 0
        while totalsent < len(msg):
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError('socket connection broken')
            totalsent = totalsent + sent

    def recv(self, delim=b'\x04', buf_size=BUFFER_SIZE):
        chunks = [b'']
        bytes_recd = 0
        while not chunks[-1].endswith(delim):
            chunk = self.sock.recv(buf_size)
            if chunk == b'':
                raise RuntimeError('socket connection broken')
            chunks.append(chunk)
        return b''.join(chunks).rstrip(delim)

    def query(self, cmd):
        self.send(cmd.encode())
        res = self.recv().decode()
        return res

    def login(self):
        cfg = {"protocol": 1, "client": "test", "clientver": 0.1}
        cmd = f'login {json.dumps(cfg).replace(" ", "")}\x04'
        return self.query(cmd)

    def dbstats(self):
        cmd = f'dbstats\x04'
        buf = self.query(cmd)
        res = json.loads(' '.join(buf.split(' ')[1:]))
        return res

    def get(self, typ, flags, filters, options):
        cmd = f'get {typ} {flags} {filters} {options}\x04'
        buf = self.query(cmd)
        res = json.loads(' '.join(buf.split(' ')[1:]))
        return res

    def set(self, typ, ids, fields):
        cmd = f'set {typ} {ids} {fields}\x04'
        return self.query(cmd)



def parse_opt():
    parser = argparse.ArgumentParser()

    parser.add_argument('typ',
                        help='the type of data to fetch')
    parser.add_argument('flags', nargs='?', default='basic',
                        help='what part of that data to fetch')
    parser.add_argument('--dir', '-d', default='data',
                        help='the target dir to output')
    parser.add_argument('--csv', '-c', action='store_true',
                        help='output the result as csv')

    return parser.parse_args()



def fetch_vndb(typ, flags):
    attr = {
        "vn": ('id', 'vn'),
        "release": ('id', 'releases'),
        "producer": ('id', 'producers'),
        "character": ('id', 'chars'),
        "staff": ('id', 'staff'),
        "user": ('id', 'users'),
        "votelist": ('uid', 'users'),
        "vnlist": ('uid', 'users'),
        "wishlist": ('uid', 'users'),
    }
    attr_name, attr_src = attr[typ]

    items = list()
    with TCPSession(HOSTNAME, PORT) as s:
        print(s.login(), flush=True, file=sys.stderr)
        stats = s.dbstats()

        count = 0
        index = 1
        page = 1
        results = 25 if "list" not in typ else 100
        while count < stats[attr_src]:
            fltr = f'({attr_name} = {repr(list(range(index, index+results)))})'
            cfg = {"page": page, "results": results, "sort": attr_name}
            res = s.get(typ, flags, fltr, json.dumps(cfg).replace(" ", ""))

            if 'id' in res:
                print(pprint.pformat(res), flush=True, file=sys.stderr)
                if res['id'] == 'throttled':
                    time.sleep(res['fullwait'])
                    continue
                raise RuntimeError("Invalid query was posted to VNDB")

            print(pprint.pformat(res), flush=True)
            items.extend(res['items'])
            count += res['num']
            if res['more']:
                page += 1
            else:
                index += results
                page = 1

    return items



def main():
    args = parse_opt()
    if not os.path.exists(args.dir):
        os.makedirs(args.dir)

    if args.typ == "dbstats":
        with TCPSession(HOSTNAME, PORT) as s:
            print(s.login(), flush=True, file=sys.stderr)
            stats = s.dbstats()
            print(pprint.pformat(stats), flush=True)
        if args.csv:
            with open(f"{args.dir}/dbstats.csv", "w") as f:
                writer = csv.DictWriter(f, stats.keys())
                writer.writeheader()
                writer.writerow(stats)
        else:
            with open(f"{args.dir}/dbstats.json", "w") as f:
                json.dump(stats, f)
    else:
        items = fetch_vndb(args.typ, args.flags)
        if args.csv:
            with open(f"{args.dir}/{args.typ}_{args.flags}.csv", "w") as f:
                writer = csv.DictWriter(f, items[0].keys())
                writer.writeheader()
                for item in items:
                    writer.writerow(item)
        else:
            with open(f"{args.dir}/{args.typ}_{args.flags}.json", "w") as f:
                json.dump(items, f)



if __name__ == "__main__":
    main()
