#!/usr/bin/env python
# tested on python 2.7.4
from __future__ import print_function
# Goal: query an OF device to find its name and supported version(s)
# pyopenflow does most of this, but the code is not great.
# TODO: abstract socket calls (who still does sockets programming)?

import socket # refactor; use scapy
import random
from struct import *

def sock_send(sock,msg):
  sent = 0
  while sent < len(msg):
    sent += sock.send(msg[sent:])
    # catch the exception here


# make this command line option
of_host = "192.168.1.131"
#of_host = "127.0.0.1"

of_port = 6633 # supposed to be 6653. Opendaylight hydrogen still uses old port?
# catch the Connection refused exception here

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# TODO: error handling
s.connect((of_host, of_port))

# This is done with a bit of reverse engineering. I've read the spec, but
# I'd like to see how the messages go out on the wire.
# wireshark 1.11.2 is still missing an openflow dissector
# http://wiki.wireshark.org/OpenFlow and WOW, 1.11.2 native on mac is no bueno!

msg = s.recv(1024)
# 1 byte OF version
# 1 byte type OFPT_HELLO
# 2 byte network byte order length
# 4 byte network byte order tx id
# optional OFPHET_VERSIONBITMAP, but we can ignore
#vals = unpack("bbH!I!",msg)
# python unpack requires a fixed length. Can't get the remainder with s* ?
# however, if length >8, we can infer that there was more.
vals = unpack(">bbHI",msg)
of_version = vals[0]
print("version=",of_version,sep="")
print("type=",vals[1],sep="")
print("length=",vals[2],sep="")
print("tx id=",vals[3],sep="")

# now we send an OFPT_HELLO (modularize this whole thing and use constants)
cli_txid = random.getrandbits(16) # gives us room to increment
# wow, i forgot python doesn't offer a fast list flatten
#ofpt_hello = [of_version,0,8,cli_txid]
msg = pack(">bbHI",of_version,0,8,cli_txid)
sock_send(s,msg)

## send OFPT_FEATURES_REQUEST (5)
#cli_txid += 1
#msg = pack(">bbHI",of_version,5,8,cli_txid)
#sock_send(s,msg)

# send OFPT_VENDOR (4)
cli_txid += 1
msg = pack(">bbHI",of_version,4,8,cli_txid)
sock_send(s,msg)

msg = s.recv(4096)

# send OFPT_FEATURES_REQUEST (5)
cli_txid += 1
msg = pack(">bbHI",of_version,5,8,cli_txid)
sock_send(s,msg)

## must we send OFPT_SET_CONFIG (9)?
#msg = pack(">bbHIHH",of_version,9,12,cli_txid,0,0x0800)
#sock_send(s,msg)

## recv OFPT_FEATURES_REPLY 
## magic goes here
#msg = s.recv(4096)
#vals = unpack(">bbHI",msg)
#msg_type = vals[1]
#msg_len = vals[2]
#print("type=",vals[1],sep="")
#print("length=",vals[2],sep="")
#print("tx id=",vals[3],sep="")
#
##rem = 0
#if msg_type == 6: # OFPT_FEATURES_REPLY
#  rem = unpack(">QII",msg[8:])

#print("remlen=",len(rem))
#print("remlen=",msg_len - 8)




s.close

