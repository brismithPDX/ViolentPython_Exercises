import nmap
import optparse

# Global Vars Definition
global_verbose = False


def print_verbose(message):
    if global_verbose is True:
        print('[VERBOSE] ' + message)
    else:
        pass


def nmap_scan(target_host, target_port):

    print_verbose('nmap_scan(): target_host is : ' + target_host)
    print_verbose('nmap_scan(): target_port is : ' + target_port)

    # set up and perform scan
    nm_scan = nmap.PortScanner()
    nm_scan.scan(target_host, target_port)

    # try to save result of scan to state and print state to screen
    try:
        state = nm_scan[target_host]['tcp'][int(target_port)]['state']
        print(" [*] " + target_host + " tcp/" + target_port + " " + state)
    except KeyError:
        print(" [-] " + target_host + " tcp/" + target_port + " Could NOT be Scanned")


def main():
    parser = optparse.OptionParser('usage: ' + '-H <target host IP> -p <target port>')
    parser.add_option('-v', '--verbose', dest='verbose', help='enables verbose output', default=False,
                      action="store_true")
    parser.add_option('-H', dest='target_host', type='string', help='specify target host IP')
    parser.add_option('-p', dest='target_ports', type='string',
                      help='specify target port[s] separated by comma like "80, 443"')

    # parse the invocation args into options and args
    (options, args) = parser.parse_args()

    # enable global verbose operator
    global global_verbose
    global_verbose = options.verbose
    print_verbose('main(): Verbosity is enabled')

    # setup target_host and target_ports from invocation args
    target_host = options.target_host
    target_ports = str(options.target_ports).split(', ')

    # test for missing required invocation args
    if (target_host is None) | (target_ports[0] is None):
        print(parser.usage)
        exit(0)

    # run scan on each supplied port
    for port in target_ports:
        nmap_scan(target_host, port)


if __name__ == '__main__':
    main()

