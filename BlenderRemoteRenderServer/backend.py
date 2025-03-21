import subprocess

class Backend():
    def get_blender_command(self, blend_file, render_device):
        return "blender -b {} -o //output_ -f 17  -- --cycles-device {}".format(blend_file, render_device)


class BackendCLI(Backend):
    def __init__(self):
        self.render_config = {}

        self.default_config = {}
        self.default_config['backend'] = "CLI"
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
        self.render_config = {}

        self.default_config = {}
        self.default_config['backend'] = "Slurm"
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
        with open(jobfile_name, 'w') as jobfile:
            jobfile.write("#!/bin/bash\n")

            for key in self.render_config:
                if key == 'max-nb-jobs':
                    continue

                jobfile.write("#SBATCH --{}={}\n".format(key, self.render_config[key]))
            
            jobfile.write("#SBATCH --nodes=1\n")
            jobfile.write("module load blender\n")
            jobfile.write("{}\n".format(super().get_blender_command(blend_file, "CPU")))

        # Submit jobfile
        job_id_list = []
        for i in range(self.render_config['max-nb-jobs']):

            result = subprocess.run(['sbatch', jobfile_name],
                                    capture_output = True,
                                    text = True)
            if result.returncode != 0 or result.stderr or not result.stdout.startswith("Submitted batch job"):
                # error with submition
                return result.returncode, result.stderr
            else:
                job_id_list.append(int(result.stdout.split(" ")[-1]))

        with open('job_id.log', 'a') as job_id_file:
            for job_id in job_id_list:
                job_id_file.write(str(job_id) + "\n")

        return 0, ""


    def get_status(self):
        return

    def cancel_render(self):
        return

    def get_server_config(self):
        return self.default_config
