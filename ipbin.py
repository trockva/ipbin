#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ipbin.py - A library by Abe Usher to help compute variable precision ipv4 address intervals,
for use in Big Data analysis, ipbin|ipbin computation, and other quantitative data analysis.
Copyright (C) 2013  Abe Usher abe.usher@gmail.com
All rights reserved.

This software is subject to the BSD 3-clause license:
http://opensource.org/licenses/BSD-3-Clause

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of HumanGeo Group LLC nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import time
import datetime
import socket
import random

__base32 = '01abcdef'
__decodemap = { }
for i in range(len(__base32)):
    __decodemap[__base32[i]] = i
del i

"""
This module creates a fuzzy precision representation of an IPv4 address interval.

It makes calculations based on an IPv4 address space of 4,294,967,296 possible values.

Each character added to the ipbin reduces the IPv4 space interval ambiguity by a factor of 8.
Note: future versions will allow a tunable jump of ambiguity reduction, not hard coded to 8.
Valid characters for encoding the floating point time into ASCII characters include {01abcdef}

0 +/- 4.2 billion IP addresses
1 +/- 268,435,456 IP addresses
2 +/- 33,554,432 IP addresses
3 +/- 4,194,304 IP addresses
4 +/- 524,288 IP addresses
5 +/- 65,536 IP addresses
6 +/- 8,292 IP addresses
7 +/- 1,024 IP addresses
8 +/- 128 IP addresses
9 +/- 16 IP addresses
10 +/- 2 IP addresses"""


def iptoint(ip):
    """
    Convert an ip address to an integer.
    Adopted from http://goo.gl/AnSFV
    """
    return int(socket.inet_aton(ip).encode('hex'),16)

def inttoip(ip):
    """
    Convert an integer into an IPv4 address.
    Adopted from http://goo.gl/AnSFV
    """
    return socket.inet_ntoa(hex(ip)[2:].zfill(8).decode('hex'))

def decode_exactly(ipbin):
    """
    Decode the ipbin to its exact values, including the error
    margins of the result.  Returns two float values: ipbin
    and the plus/minus error for epoch seconds.
    """
    ip_interval = (0.0, 4294967295.0)#from 0.0.0.0 to 256.256.256.256
    ip_range = (ip_interval[0] + ip_interval[1])/2  #this constant is used to calculate the potential time error defined by a particular number of characters
    for c in ipbin:
        cd = __decodemap[c]
        for mask in [4, 2, 1]:
            ip_range /=2
            mid = (ip_interval[0] + ip_interval[1])/2
            if cd & mask:
                ip_interval = (mid, ip_interval[1])
            else:
                ip_interval = (ip_interval[0], mid)
    ip_value = (ip_interval[0] + ip_interval[1])/2
    return (ip_value, ip_range)

def decode(ipbin):
    """
    Decode ipbin, returning a single floating point value for epoch seconds.
    """
    ip_value, ip_range = decode_exactly(ipbin)
    #drop the time_error for now
    return ip_value

def encode(ip_integer, precision=10):
    """
    Encode an IPv4 address given as a floating point number (dotted quad notation turned into an integer, the intger turned into a floating point)
    and return an IPv4 address as an integer, plus a range.
    """
    if precision > 10:
        #wtf? we can't subdivide to less than one IP address.
        precision = 10
    ip_interval = (0.0, 4294967295.0)#from 0.0.0.0 to 256.256.256.256
    ipbin = []
    bits = [4, 2, 1]
    bit = 0
    ch = 0
    while len(ipbin) < precision:
        mid = (ip_interval[0] + ip_interval[1])/2
        if ip_integer > mid:
            ch |= bits[bit]
            ip_interval = (mid, ip_interval[1])
        else:
            ip_interval = (ip_interval[0], mid)
        if bit < 2:
            bit += 1
        else:
            ipbin += __base32[ch]
            bit = 0
            ch = 0
    return ''.join(ipbin)

def test():
# Examples of encoding
    humangeo_ip_quad = '66.96.160.133'
    humangeo_ip_integer = iptoint(humangeo_ip_quad)
    for i in range (1,11):
        print '-----'
        print 'precision =', i
        precision = i
        ipbin_humangeo = encode(humangeo_ip_integer, precision=precision)
        print ipbin_humangeo
        print decode_exactly(ipbin_humangeo)

def random_range():
    """
    Test 100 values and put them into ipbin.
    """
    numbers_to_test = 100
    integer_space = 4294967295.0
    list_of_bins = []
    for i in range(100):
        multiple = random.random()
        value = multiple * 4294967295.0
        ipbin = encode(value)
        list_of_bins.append(ipbin)
    list_of_bins.sort()
    for bin in list_of_bins:
        print bin

    print
    another = '10.86.41.92'
    number = iptoint(another)
    another_bin = encode(number)
    print another_bin

if __name__ == "__main__":
    """
    Main function - entry point into script.  Used for examples and testing.
    """
    random_range()
