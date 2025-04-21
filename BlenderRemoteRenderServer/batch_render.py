
import bpy
import os
import sys
import argparse


def render_frame(frame):
    """
    Render a single frame
    """
    Scene = bpy.context.scene
    Scene.frame_current = frame
    bpy.ops.render.render()
    bpy.data.images['Render Result'].save_render(filepath=Scene.render.frame_path(frame=frame))


def parse_arguments():
    """
    Parse command line arguments meant for sequence data and overwrite some of the 
    """
    parser = argparse.ArgumentParser(description="Render set of frames, allows running multiple instances concurently")
    parser.add_argument("--frames", help="Range of frames to render, should be in format '1..17'. If absent, using the frame range inside the .blend file.")

    # Parse arguments after "--"
    if not "--" in sys.argv:
        Scene = bpy.context.scene
        return Scene.frame_start, Scene.frame_end

    args = parser.parse_args(args=sys.argv[sys.argv.index("--") + 1:])

    frame_start = int(args.frames.split("..")[0])
    frame_end = int(args.frames.split("..")[1])

    return frame_start, frame_end


def render_frames(frame_start, frame_end):
    """
    Render frames from frame_start to frame_end
    Render isn't triggered for frames that are already present in the folder
    """
    Scene = bpy.context.scene
    # Create export folder
    export_folder = os.path.dirname(Scene.render.frame_path(frame=0))
    if not os.path.exists(export_folder):
        os.makedirs(export_folder)

    # Render each frame
    for frame in range(frame_start, frame_end+1):
        export_path = Scene.render.frame_path(frame=frame)
        export_path_tmp = export_path + ".tmp"

        # Check if render has already been done
        if os.path.exists(export_path) or os.path.exists(export_path_tmp):
            continue

        # Create empty temporary file
        with open(export_path_tmp, 'w') as fp:
            pass

        render_frame(frame)
        try:
            os.remove(export_path_tmp)
        except:
            pass


if __name__ == '__main__':
    frame_start, frame_end = parse_arguments()
    render_frames(frame_start, frame_end)