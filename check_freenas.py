#!/usr/bin/env python

# The MIT License (MIT)
# Copyright (c) 2015 Goran Tornqvist
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import json
import sys
 
import requests
 
class Startup(object):
 
    def __init__(self, hostname, user, secret):
        self._hostname = hostname
        self._user = user
        self._secret = secret
 
        self._ep = 'https://%s/api/v1.0' % hostname
 
    def request(self, resource, method='GET', data=None):
        if data is None:
            data = ''
        try:
            r = requests.request(
                method,
                '%s/%s/' % (self._ep, resource),
                data=json.dumps(data),
		verify=False,
                headers={'Content-Type': "application/json"},
                auth=(self._user, self._secret),
            )
        except:
            print 'UNKNOWN - Error when contacting freenas server: ' + str(sys.exc_info())
            sys.exit(3)
 
        if r.ok:
            try:
                return r.json()
            except:
                print 'UNKNOWN - Error when contacting freenas server: ' + str(sys.exc_info())
                sys.exit(3)
 
    def check_repl(self):
        repls = self.request('storage/replication')
        errors=0
        try:
            for repl in repls:
                if repl['repl_status'] != 'Succeeded':
                    errors = errors + 1
        except:
            print 'UNKNOWN - Error when contacting freenas server: ' + str(sys.exc_info())
            sys.exit(3)
 
        if errors > 0:
            print 'WARNING - There are ' + str(errors) + ' replication errors. Go to Storage > Replication Tasks > View Replication Tasks in FreeNAS for more details.'
            sys.exit(1)
        else:
            print 'OK - No replication errors'
            sys.exit(0)
 
    def check_alerts(self):
        alerts = self.request('system/alert')
        errors=0
        try:
            for alert in alerts:
                if alert['level'] != 'OK':
                    errors = errors + 1
        except:
            print 'UNKNOWN - Error when contacting freenas server: ' + str(sys.exc_info())
            sys.exit(3)
 
        if errors > 0:
            print 'WARNING - There are ' + str(errors) + ' alerts. Click Alert button in FreeNAS for more details.'
            sys.exit(1)
        else:
            print 'OK - No problem alerts'
            sys.exit(0)
 
def main():
    parser = argparse.ArgumentParser(description='Checks a freenas server using the API')
    parser.add_argument('-H', '--hostname', required=True, type=str, help='Hostname or IP address')
    parser.add_argument('-u', '--user', required=True, type=str, help='Normally only root works')
    parser.add_argument('-p', '--passwd', required=True, type=str, help='Password')
    parser.add_argument('-t', '--type', required=True, type=str, help='Type of check, either repl or alerts')
 
    args = parser.parse_args(sys.argv[1:])
 
    startup = Startup(args.hostname, args.user, args.passwd)
 
    if args.type == 'alerts':
        startup.check_alerts()
    elif args.type == 'repl':
        startup.check_repl()
    else:
        print "Unknown type: " + args.type
        sys.exit(3)
 
if __name__ == '__main__':
    main()
    
