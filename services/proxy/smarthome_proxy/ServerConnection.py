import socket
import time
import logging

from threading import Thread

from requests import get

from .connection_protocol import parser

IPWAITTIME = 10
from Crypto.Cipher import AES
from Crypto.Util import Counter

key = b'Jimmy ffffffffff'
IV = b'1234567891234567'

def do_encrypt(message):
    iv_int = int.from_bytes(IV, byteorder='big')

    new_counter = Counter.new(128, initial_value=iv_int)
    cipher = AES.new(key, AES.MODE_CTR, counter=new_counter)
    return cipher.encrypt(message)

def do_decrypt(message):
    iv_int = int.from_bytes(IV, byteorder='big')
    new_counter = Counter.new(128, initial_value=iv_int)
    cipher = AES.new(key, AES.MODE_CTR, counter=new_counter)
    return cipher.decrypt(message)

# create the connection and check if something is getting through
class ServerConnection(Thread):
    def __init__(self, host='', port=45321):
        super(ServerConnection, self).__init__()

        self.address = (host, port)
        self.listening_socket = None

        self.connection_socket = socket.socket(
            socket.AF_INET
            , socket.SOCK_STREAM
        )
        self.connection_socket.setsockopt(
            socket.SOL_SOCKET
            , socket.SO_REUSEADDR
            , 1
        )
        self.connection_socket.bind(self.address)
        self.connection_socket.listen(1)

    def send_message(self, message):
        logging.info('ReceiverThread: "%s"' % message)
        self.listening_socket.sendall(do_encrypt(message))

    def run(self):
        logging.info("ReceiveThread Thread - Starting ")
        while 1:
            self.listening_socket, addr = self.connection_socket.accept()
            rcvd_data = self.listening_socket.recv(4096)
            rcvd_data = do_decrypt(rcvd_data)
            logging.info("ReceiveThread - Acepted: " + rcvd_data)
            if rcvd_data:
                parser(rcvd_data, self)
            logging.info("ReceiveThread Thread - Exiting")


class ClientThread(Thread):
    def __init__(self, host="dvalverde.ddns.net", port=54897):
        super(ClientThread, self).__init__()
        self.packet_id = "ip"
        self.check_connection = "ch_palacoulo"
        self.my_address = ""
        self.sender_server = (host, port)
        self.connection_issues = 1
        self.send_ip = 0

    def send_to_host(self, message):
        while True:
            try:
                logging.debug("Connected to %s on port %s " % self.sender_server)

                sender_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sender_sock.connect(self.sender_server)
                logging.debug("Connected to %s on port %s " % self.sender_server)
                logging.debug("Sending {}".format(message))
                sender_sock.sendall(do_encrypt(str(message)))
                time.sleep(1)
                logging.debug("bla")
                received_data = do_decrypt(sender_sock.recv(16)).decode()
                logging.debug("Received: {}".format(received_data))
                #assert ("porto" in received_data)
                logging.debug("Received: {}".format(received_data))
                break
            except socket.error as e:
                self.connection_issues = 1
                logging.error("Cant connect at the time {}".format(e))
                time.sleep(10)
                continue
            except AssertionError as e:
                logging.error("Connection problems: {}".format(e))
                time.sleep(10)
                continue
            finally:
                logging.debug("Exiting")
                sender_sock.close()
                time.sleep(1)

    def run(self):
        logging.info("Starting " + self.name)
        while 1:
            new_address = "get('https://ipapi.co/ip/').text"
            self.send_to_host(self.check_connection)
            logging.debug("my address {}".format(self.my_address))
            logging.debug("new address {}".format(new_address))
            if self.my_address not in new_address or self.connection_issues:
                self.connection_issues = 0
                self.my_address = new_address
                to_send = "{}_{}".format(self.packet_id, new_address)
                self.send_to_host(to_send)
            time.sleep(IPWAITTIME)

