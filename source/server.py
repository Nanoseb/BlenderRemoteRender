import json
import zmq
from messages import msg


class BackendSlurm():
    def __init__(self):
        self.render_config = {}
        return

    def setup_run(self):
        return

    def start_render(self):
        return

    def get_status(self):
        return

    def cancel_render(self):
        return

    def get_server_config(self):
        config = {}
        config['backend'] = "Slurm"
        config['Job Name'] = {'type': 'string', 'default': 'Blender_render'}
        config['Time'] = {'type': 'string', 'default': '00:20:00'}
        config['Account'] = {'type': 'string', 'default': ''}
        config['Partition'] = {'type': 'string', 'default': 'standard'}
        config['QOS'] = {'type': 'string', 'default': 'standard'}
        config['Max nb Jobs'] = {'type': 'int', 'default': '4'}
        return config


class Server():
    """
        Class handling the communication with the client addon. Render actions are delagated to the Backend class.
        This class only handles the communication and IO.
    """

    def __init__(self, listen_port, backend):
        self.backend = backend
        self.listen_port = listen_port

        self.client_connected = False

    def log(self, text, type="status"):
        """ Prints log to terminal """
        print(text)

    def send_string(self, text):
        """ Wrapper function to send string to client """

        self.socket.send(self.identity, zmq.SNDMORE)
        self.socket.send_string(text)

    def send_backend_config(self, dict):
        """ Sends dictionarry serialised using json """
        self.socket.send(self.identity, zmq.SNDMORE)
        self.socket.send_string(msg.BACKEND_CONFIG, zmq.SNDMORE)
        self.socket.send_json(dict)

    def save_file(self, path, file):
        """ Saves file to disk and sends acknoledgement to client """
        with open(path, "wb") as f:
            f.write(file)
        self.log("File {} written".format(path))
        self.send_string(msg.FILE_ACK)

    def run(self):
        """
            Run the server
        """
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind("tcp://*:{}".format(self.listen_port))
        self.log("listening to *:{}".format(self.listen_port))

        while True:
            identity = self.socket.recv()

            if not self.client_connected:
                self.identity = identity
            elif self.identity != identity:
                self.log("Rejecting connection from new client", type="error")
                message = self.socket.recv_multipart()
                continue

            message = self.socket.recv_multipart()

            header = message[0].decode("utf-8")

            match header:
                case msg.PING:
                    self.send_string(msg.PONG)
                    if not self.client_connected:
                        self.log("Connected")
                        # Sends default server backend configuration
                        self.send_backend_config(self.backend.get_server_config())
                        self.client_connected = True

                case msg.CLOSE_CONNECTION:
                    self.log("Disconnected")
                    self.client_connected = False

                case msg.FILE:
                    path = message[1].decode("utf-8")
                    self.save_file(path, message[2])

                case msg.BACKEND_CONFIG:
                    self.backend.render_config = json.loads(message[1])

                case _:
                    self.log("Command not recognised: {}".format(header))


if __name__ == '__main__':
    port = 31416
    backend = BackendSlurm()
    server = Server(port, backend)
    server.run()
