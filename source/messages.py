

class Messages():
    """
        Structure to hold possible message headers for communication
    """

    def __init__(self):
        self.PING = "ping"
        self.PONG = "pong"
        self.CLOSE_CONNECTION = "close_connection"
        self.FILE = "file"
        self.FILE_ACK = "file_ack"
        self.BACKEND_CONFIG = "backend_config"
        self.START_RENDER = "start_render"
        self.GET_RENDER_OUTPUT = "get_render_output"

msg = Messages()
