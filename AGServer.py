from AGControl import *

import socket
import time


# Function for manual controlling by client
def server():
    while controls.get_working_flag():
        try:
            sock = socket.socket()
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', 14880))
            sock.listen(2)
            while controls.get_working_flag():
                try:
                    conn, addr = sock.accept()
                    conn.settimeout(30)
                    print('Address connected:', addr)
                    logging.info('Address connected: %s', addr)
                    while controls.get_working_flag():
                        conn.send(form_status_string().encode())

                        command = conn.recv(4096)
                        print(command)
                        if command.decode() == '2':
                            manual_switch('light')
                            logging.info('Lights switched by: %s', addr)
                        elif command.decode() == '3':
                            manual_switch('fan')
                            logging.info('Fan switched by: %s', addr)
                        elif command.decode() == '4':
                            controls.set_autocontrol_flag(True)
                            print('Automatical control ON')
                            logging.info('Automatical control ON by: %s', addr)
                        elif command.decode() == '9':
                            controls.set_working_flag(False)
                            print('Shutdown by', addr)
                            logging.info('Shutdown by %s', addr)
                        else:
                            logging.warning('Invalid income command.')
                            break

                    conn.close()
                except socket.error as error:
                    print(error)
                    logging.error(error)

            sock.close()

        except socket.error as error:
            print(error)
            logging.error(error)
            time.sleep(10)


def form_status_string():
    status_string = str(status.get_humidity()) + ',' + str(status.get_temperature()) + ',' + str(
        controls.get_light_status()) + ',' + str(controls.get_fan_status()) + ',' + str(controls.get_autocontrol_flag())
    return status_string


# Function for switching mechs by server
def manual_switch(func):
    controls.set_autocontrol_flag(False)
    print('Automatical Control OFF')

    if func == 'light':
        switching_light(not controls.get_light_status())

    if func == 'fan':
        switching_fan(not controls.get_fan_status())
