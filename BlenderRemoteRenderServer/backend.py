import subprocess
import json
from datetime import datetime
import os.path
from os import walk

class Backend():
    def __init__(self):
        self.render_extension = 'png'

    def get_blender_command(self, blend_file, export_path, render_device, frame_start, frame_end):
        return "blender -b {} -o //{}/output_ -f {}..{}  -- --cycles-device {}".format(blend_file, 
                                                                                      export_path,
                                                                                      frame_start, 
                                                                                      frame_end,
                                                                                      render_device)

    def get_new_export_path(self, name):
        return "{}-{}".format(datetime.now().strftime("%Y%m%d-%H%M%S"), name.replace(" ", "_"))

    def get_rendered_filelist(self, export_path):
        filenames = next(walk(export_path), (None, None, []))[2]
        return [ os.join(export_path, filename) for filename in filenames 
                if (filename.endswith(self.render_extension) and 
                    filename.startswith('output_')) ]

    def get_nb_rendered(self, export_path):
        return len(self.get_rendered_filelist(export_path))

    def write_batch_render_script(self, path):


        """
        
        
        
        """


class BackendCLI(Backend):
    def __init__(self):
        self.name = "CLI"
        self.render_config = {}

        self.default_config = {}
        self.default_config['backend'] = self.name
        self.default_config['job-name'] = {'type': 'string', 'default': 'Blender_render', 'label': 'Job name'}
        self.default_config['max-nb-jobs'] = {'type': 'int', 'default': '6', 'label': 'Simultaneous renders'}
        self.default_config['render-backend'] = {'type': 'string', 'default': 'GPU', 'label': 'Render backend (CPU CUDA OPTIX HIP ONEAPI METAL)'}
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
        return self.default_config


class BackendSlurm(Backend):
    def __init__(self):
        self.name = "Slurm"
        self.log_filename = 'job_status_log.json'
        self.render_config = {}

        self.default_config = {}
        self.default_config['backend'] = self.name
        self.default_config['job-name'] = {'type': 'string', 'default': 'Blender_render', 'label': 'Job name'}
        self.default_config['time'] = {'type': 'string', 'default': '00:20:00', 'label': 'Run time'}
        self.default_config['account'] = {'type': 'string', 'default': '', 'label': 'Account'}
        self.default_config['partition'] = {'type': 'string', 'default': 'standard', 'label': 'Partition'}
        self.default_config['qos'] = {'type': 'string', 'default': 'standard', 'label': 'QOS'}
        self.default_config['max-nb-jobs'] = {'type': 'int', 'default': '4', 'label': 'Max nb Jobs'}

    def setup_run(self):
        return

    def start_render(self, blend_file):

        # Write slurm jobfile
        jobfile_name = 'jobfile.slurm'
        export_path = self.get_new_export_path(self.render_config['job-name'])

        frame_start = self.render_config['frame-start']
        frame_end = self.render_config['frame-end']

        with open(jobfile_name, 'w') as jobfile:
            jobfile.write("#!/bin/bash\n")

            for key in self.render_config[self.name]:
                jobfile.write("#SBATCH --{}={}\n".format(key, self.render_config[self.name][key]))
            
            jobfile.write("#SBATCH --nodes=1\n")
            jobfile.write("module load blender\n")
            jobfile.write("{}\n".format(super().get_blender_command(blend_file, export_path, "CPU", frame_start, frame_end)))

        # Submit jobfile
        job_id_list = []
        for i in range(min(self.render_config['max-nb-jobs'], frame_end - frame_start+1)):

            result = subprocess.run(['sbatch', jobfile_name],
                                    capture_output = True,
                                    text = True)
            if result.returncode != 0 or result.stderr or not result.stdout.startswith("Submitted batch job"):
                # error with submition
                return result.returncode, result.stderr
            else:
                job_id_list.append(int(result.stdout.split(" ")[-1]))

        self.export_job_log(export_path, job_ids=job_id_list)

        return 0, ""
    
    def export_job_log(self, export_path, job_ids):
        filename = self.log_filename
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
        else:
            data = {}
        
        data[export_path] = {}
        if job_ids:
            for jobid in job_ids:
                data[export_path][str(jobid)] = {'status': 'SUBMITTED'}

        with open(filename, 'w') as f:
            json.dump(data, f)


    def get_status(self, export_path):
        filename = self.log_filename
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
        

        result = subprocess.run(['squeue', '-u', '$USER', '-o', '"%A %T"', '-h'],
                                capture_output = True,
                                text = True)
        output = [ job.split(" ") for job in result.stdout.split('\n') ]
        status_list = []
        for job in output:
            jobid = job[0]
            status = job[1]
            if jobid in data[export_path]:
                data[export_path][jobid]['status'] = status
                status_list.append(status)
        
        render_status = 'In progress'
        if any([ a == 'PENDING' for a in status_list]):
            render_status = 'Pending'
        if all([ a == 'COMPLETED' for a in status_list]):
            render_status = 'Completed'
        
        progress = self.get_nb_exported(export_path)
        
        return render_status, progress

    def cancel_render(self):
        return

    def get_server_config(self):
        return self.default_config
