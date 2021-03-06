import logging
import smarthome_relay.config as config

#Global Logging
logger = logging.getLogger(__name__)

def h_noop(data, self):
    logger.error("[Connection Parser] Not Implemented Received: {}".format(data))


def h_webserver_trigger_ip(data, self):
    logger.info("[Connection Parser] Received h_trigger_ip: : {}".format(data))
    # TODO: Arduino connection
    # if ok
    self.send_message("received")
    return '_'.join(data)


def h_arduino_door_belt(data, self):
    # TODO
    logger.info("[Connection Parser] Received h_arduino_door_belt: : {}".format(data))
    self.send_message("received")
    return '_'.join(data)

def h_arduino_gpio(data, self ):
    logger.info("[Connection Parser] Received h_arduino_door_belt: : {}".format(data))
    to_send = "<1_{}>".format('_'.join(data)).encode()
    config.HOUSEHOLDE_QUEUE.append(to_send)
    logger.debug("[Connection Parser] QUEUE: "+ str(config.HOUSEHOLDE_QUEUE))
    self.send_message("received")
    return '_'.join(data[4:0])

def h_check(data, self ):
    logger.info("[Connection Parser] Received h_check: : {}".format(data))
    return '_'.join(data)



handlers = {
    "tr": h_webserver_trigger_ip,
    "dt": h_arduino_door_belt,
    "ag": h_arduino_gpio,
    "ch": h_check
}


def parser(data, self):
    while len(data) >= 2:
        packet_id = data[0:2]

        if packet_id not in handlers:
            data = data[1:]
        else:
            data_list = list(filter(None, data[2:].split('_')))
            data = handlers.get(packet_id, h_noop)(data_list, self)
