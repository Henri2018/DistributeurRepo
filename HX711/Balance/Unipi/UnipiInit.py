#!/usr/bin/python
from jsonrpclib import Server


def initialisationUnipi(ip):
    s=Server(ip)
    return s

#if __init__=="__main__":
ip="http://localhost:8080/rpc"
s=initialisationUnipi(ip)
print(s)
s.relay_set(1,1)
print(s.relay_get(1))
s.relay_set(1,0)
print(s.relay_get(1))
print(s.ai_get(1))
