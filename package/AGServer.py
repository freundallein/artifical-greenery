import socket

from package.AGControl import *


# Function for manual controlling by client
def server():
    while controls.get_working_flag():
        try:
            sock = socket.socket()
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', config.server_port))
            sock.listen(2)
            while controls.get_working_flag():
                try:
                    conn, addr = sock.accept()
                    conn.settimeout(30)
                    print('Address connected:', addr)
                    logging.info('Address connected: %s', addr)
                    while controls.get_working_flag():
                        conn.send(get_status().encode())
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
                            print('Automatic control ON')
                            logging.info('Automatic control ON by: %s', addr)
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
