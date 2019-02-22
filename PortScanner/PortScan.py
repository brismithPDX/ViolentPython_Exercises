import optparse
from socket import *
from threading import *

screen_lock = Semaphore(value=1)


def connect_port_scan(target_host, target_port):
    try:

        # Set up socket connection for port interrogation
        connection_socket = socket(AF_INET, SOCK_STREAM)
        connection_socket.connect((target_host, target_port))

        # Set banner message used in connection
        banner = 'Violent Python - Fault Tolerant Port Scanner \r\n'

        # Send utf-8 encoded banner string to target port
        connection_socket.send(str.encode(banner, encoding="utf-8"))

        # get results from the port interrogation
        results = connection_socket.recv(100)

        # Get screen lock and print results of port interrogation
        screen_lock.acquire()

        print('[+]%d/tcp open'% target_port)
        print('[+] ' + str(results))

        screen_lock.release()

        connection_socket.close()

    except Exception as e:

        screen_lock.acquire()
        print('[-] {0} tcp closed - {1}'.format(str(target_port), str(e)))
        screen_lock.release()


def get_host_ip_from_host_name(target_host_name):
    try:
        target_ip = gethostbyname(target_host_name)

        return target_ip

    except Exception as e:
        print('ERROR: Could not Resolve Host Name: ' + target_host_name)


def port_scan_host(target_host, target_ports):
    target_ip = get_host_ip_from_host_name(target_host)

    try:
        target_name = gethostbyaddr(target_ip)

        print('\n[+] Scan Results for: ' + target_name[0])
    except Exception as e:
        print('\n[-] Could not resolve target name - Exception: ' + str(e))
        print('\n[+] Scan Results for: ' + target_ip)

    setdefaulttimeout(1)

    for ports in target_ports:
        t = Thread(target=connect_port_scan, args=(target_ip, int(ports)))
        t.start()


def main():
    parser = optparse.OptionParser('usage:program ' + '-H <target host> -p <target port>')

    parser.add_option('-H', '--host', dest='target_host', type='string', help='specify target host')
    parser.add_option('-p', '--ports', dest='target_ports', type='string',
                      help='specify target port[s] separated by comma')

    options, args = parser.parse_args()

    target_host = options.target_host

    target_ports = str(options.target_ports).split(',')

    if (target_host is None) | (target_ports[0] is None):
        print(parser.usage)
        exit(0)

    port_scan_host(target_host, target_ports)


if __name__ == '__main__':
    main()
