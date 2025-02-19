import bpy
from .client_core import RemoteRenderStill, RemoteRender, RemoteClose, RemoteConnect

class RemoteRenderUI(bpy.types.Panel):
    """Defines remote render panel"""
    bl_label = "Remote Render"
    bl_idname = "RENDER_PT_RemoteRender"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        rr = scene.remote_render
 
        # Server settings
        header, panel = layout.panel("Connection settings")
        header.label(text="Connection settings")
        if panel:
            panel.prop(rr, "server_hostname")
            panel.prop(rr, "server_port")
            row = panel.row(align=True)
            if rr.server_connected:
                row.operator("remote.close", text="Disconnect", icon='INTERNET')
                row.enabled = True
            else:
                row.operator("remote.connect", text="Connect", icon='INTERNET')
                row.enabled = bool(rr.server_hostname)


        # Scheduler
        header, panel = layout.panel("Scheduler settings")
        header.label(text="Scheduler settings - {}".format(rr.backend_name))
        if panel:
            for item in rr.backend_config:
                panel.prop(item, item.type, text=item.label)

        # Render
        header, panel = layout.panel("Render")
        header.label(text="Render")
        if panel:
            row = panel.row(align=True)
            row.prop(scene, "frame_start")
            row.prop(scene, "frame_end")

            row = panel.row(align=True)
            row.operator("remote.render", text="Render", icon='RENDER_STILL')
            row.enabled = rr.server_connected

        # Status
        header, panel = layout.panel("Status")
        header.label(text="Status")
        if panel:
            box = panel.box()
            logs = rr.status_log.split(";")[-5:]
            for line in logs:
                box.label(text=line, )
