import logging
import serial
import serial.tools.list_ports
import warnings
import socket
from threading import Thread
from enum import Enum

import smarthome_proxy.config as config

class CommandType(Enum):
    """ Received Command """

    SET       = 0
    GET       = 1
    CONFIG    = 2
    MEM_DEBUG = 3
    Unknown   = -1

class HouseholdConnection(Thread):
    def __init__(self):
        super(HouseholdConnection, self).__init__()
        arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if 'Arduino' in p.description  # may need tweaking to match new arduinos
        ]
        if not arduino_ports:
            ## TODO: check if not Debug/ CICD Mode
            raise IOError("No Arduino found")
        if len(arduino_ports) > 1:
            warnings.warn('Multiple Arduinos found - using the first')

        self.arduino_ser = serial.Serial(arduino_ports[0],
                                    baudrate=9600,
                                    parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE,
                                    bytesize=serial.EIGHTBITS,
                                    timeout=1)

    def run(self):
        logging.info("Starting Arduino Connection")
        while True:
            serial.time.sleep(0.01)
            while self.arduino_ser.in_waiting:
                data = self.arduino_ser.readline().decode("utf-8")
                try:
                    self.decode(data)
                    if len(config.HOUSEHOLDE_QUEUE)>0:
                        pkg = config.HOUSEHOLDE_QUEUE.pop()
                        self.write(pkg)
                    pass
                except Exception as e:
                    print ('HouseHoulde: ', e)

    def write(self,message):
        self.arduino_ser.write(message)

    def send_message(self, message):
        print(message)

    def set(self, value):
        self.pong = value

    def create_decoded_json(self, data_list):
        """ Should datalist be already parsed? """

        print(data_list)
        #TODO error detection
        decoded_json = {
            "from" : data_list[0],
            "to" : data_list[1],
            "command" : CommandType(data_list[2]),
            "GPIO" : data_list[3],
            #"available" : data_list[4],
            "value" : data_list[4]
        }

        return decoded_json

    #from_to_command_gpio_value
    def decode(self, data):

        #gpios = {
        #    "13": self.h_door_state,
        #}
        try:
            data_list = list(filter(None, data.rstrip().split('_')))
            data_list = [int(i) for i in data_list]
            json = self.create_decoded_json(data_list)
            print(json)
            config.SERVER_QUEUE.append(json)
            print(config.SERVER_QUEUE)
        except Exception as e:
            print(e)
        #Todo Change this a suttlibe function
        #if not data_list[1]:
        #    if data_list[3] == 13:
        #        if data_list[2]:
        #            message = "st_"+str(data_list[4])
        #            logging.debug("Sending {}".format(message))
        #            try: 
        #                self.sender_server = ("EXAMPLE", 4662)
        #                sender_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #                sender_sock.connect(self.sender_server)
        #                logging.debug("Connected to %s on port %s " % self.sender_server)
        #                sender_sock.sendall(str(message).encode('utf-8'))
        #            except ConnectionRefusedError:
        #                logging.debug("conection failed")
                        

