import bpy
import zmq
import json
from .messages import msg


class RemoteConnect(bpy.types.Operator):
    """Connect to a remote render server"""
    bl_idname = "remote.connect"
    bl_label = "Connect"

    def execute(self, context):
        context.scene.remote_render.connect_remote()
        return {"FINISHED"}

class RemoteClose(bpy.types.Operator):
    """Close connection to a remote render server"""
    bl_idname = "remote.close"
    bl_label = "Disconnect"

    def execute(self, context):
        context.scene.remote_render.close_remote()
        return {"FINISHED"}

class RemoteRenderFrame(bpy.types.Operator):
    """Render current project on remote server"""
    bl_idname = "remote.render"
    bl_label = "Render"
    bl_icon = 'RENDER'

    def execute(self, context):
        rr = context.scene.remote_render
        config = {}
        # Save current project
        blender_project_filename = "remote.blend"
        bpy.ops.wm.save_as_mainfile(filepath=blender_project_filename, compress=True, copy=True, relative_remap=True) 

        # Send Blender file
        rr.send_file(blender_project_filename)
        config["blender_file"] = blender_project_filename

        # Send backend config
        for item in rr.backend_config:
            match item.type:
                case 'string':
                    config[item.key] = item.string
                case 'int':
                    config[item.key] = item.int
                case 'bool':
                    config[item.key] = item.bool
        
        rr.send_backend_config(config)

        rr.send_strings([msg.START_RENDER, blender_project_filename])

        return {"FINISHED"}


class BackendConfig(bpy.types.PropertyGroup):
    """ Data structure containing user editable server backend properties """
    label: bpy.props.StringProperty(name="label")
    key: bpy.props.StringProperty(name="key")
    type: bpy.props.StringProperty(name="type")
    string: bpy.props.StringProperty(name="string_value")
    int: bpy.props.IntProperty(name="int_value")
    bool: bpy.props.BoolProperty(name="bool_value")


class RemoteRender(bpy.types.PropertyGroup):
    """ 
        Class handling client-server communications
    """
    # Server connection
    server_hostname: bpy.props.StringProperty(name="Hostname", default="172.30.17.231")
    server_port: bpy.props.IntProperty(name="Port", default=31415)
    server_connected: bpy.props.BoolProperty(name="Connected", default=False)

    # Server settings
    backend_config: bpy.props.CollectionProperty(type=BackendConfig)
    backend_name: bpy.props.StringProperty(name="Backend name")
    render_export_dir: bpy.props.StringProperty(name="Export directory name")

    status_log: bpy.props.StringProperty(name="Status log", default="")


    def log(self, comment):
        """ Add comment to the connection log """
        print(comment)
        self.status_log +=";" + comment

    def connect_remote(self):
        """ Connect to a remote server """
        if not self.server_connected:
            if not bpy.types.WindowManager.zmq_context:
                bpy.types.WindowManager.zmq_context = zmq.Context()

            self.status_log = ""
            self.log("Connecting to {}:{} ...".format(self.server_hostname, self.server_port))
            bpy.types.WindowManager.socket = bpy.types.WindowManager.zmq_context.socket(zmq.DEALER)
            bpy.types.WindowManager.socket.connect("tcp://{}:{}".format(self.server_hostname, self.server_port))
            bpy.types.WindowManager.socket.send_string(msg.PING, zmq.NOBLOCK)

            # Register timer for message polling
            if not bpy.app.timers.is_registered(self.timer_poller):
                bpy.app.timers.register(self.timer_poller)
            
    def init_server_config(self, config):
        """ 
            Initialise backend server configuration 
            The server sends a dictionary containing user editable fields 
        """
        self.log("Get backend config")

        self.backend_config.clear()

        for key in config.keys():
            if key == 'backend':
                self.backend_name = config[key]
                continue

            self.backend_config.add()
            self.backend_config[-1].key = key
            self.backend_config[-1].label = config[key]['label']
            self.backend_config[-1].type = config[key]['type']
            match config[key]['type']:
                case "string":
                    self.backend_config[-1].string = config[key]['default']
                case "int":
                    self.backend_config[-1].int = int(config[key]['default'])
                case "bool":
                    self.backend_config[-1].bool = bool(int(config[key]['default']))


    def close_remote(self):
        """ Close remote connection """
        if self.server_connected:
            self.log("Disconnecting...")
            self.server_connected = False
            bpy.types.WindowManager.socket.send_string(msg.CLOSE_CONNECTION)

            # Unregister message poller
            if bpy.app.timers.is_registered(self.timer_poller):
                bpy.app.timers.unregister(self.timer_poller)

            bpy.types.WindowManager.socket.close()
            self.log("Disconnected")

    def send_strings(self, string_list):
        """ Sends a list of strings as a multipart message """
        for string in string_list[:-1]:
            bpy.types.WindowManager.socket.send_string(string, zmq.SNDMORE)
        bpy.types.WindowManager.socket.send_string(string_list[-1])


    def send_file(self, path):
        """ Send file to remote server """
        bpy.types.WindowManager.socket.send_string(msg.FILE, zmq.SNDMORE)
        bpy.types.WindowManager.socket.send_string(path, zmq.SNDMORE)
        with open(path, 'rb') as f:
            bpy.types.WindowManager.socket.send(f.read())
        self.log("Sending file...")

    def send_backend_config(self, config):
        """ Helper function to send the user edited backend configuration """
        bpy.types.WindowManager.socket.send_string(msg.BACKEND_CONFIG, zmq.SNDMORE)
        bpy.types.WindowManager.socket.send_json(config)
 


    def timer_poller(self):
        """ Timer receiving and acting on zmq received messages """
        try:
            message = bpy.types.WindowManager.socket.recv_multipart(zmq.NOBLOCK)
        except zmq.Again as e: # Error raised when no message is in the queue
            return 0.1

        header = message[0].decode("utf-8")

        match header:
            case msg.PONG:
                self.log("Connected")
                self.server_connected = True
            case msg.FILE_ACK:
                self.log("File sent")
            case msg.BACKEND_CONFIG:
                # Reception of the backend configuration
                self.init_server_config(json.loads(message[1]))
            case _:
                self.log("Command not recognised: {}".format(header))

        return 0.1


