
class Backend():
    def get_blender_command(self, blend_file):
        return "blender {}".format(blend_file)


class BackendCLI(Backend):
    def __init__(self):
        self.render_config = {}

        self.default_config = {}
        self.default_config['backend'] = "CLI"
        self.default_config['max-nb-jobs'] = {'type': 'int', 'default': '6', 'label': 'Simultaneous renders'}
        self.default_config['render-backend'] = {'type': 'string', 'default': 'GPU', 'label': 'Render backend (CPU/GPU)'}
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

    def start_render(self):

        # Write slurm jobfile
        jobfile_name = 'jobfile.slurm'
        with open(jobfile_name, 'w') as jobfile:
            jobfile.write("#!/bin/bash")

            for key in self.render_config:
                if key == 'max-nb-jobs':
                    continue

                jobfile.write("#SBATCH --{}={}".format(key, self.render_config[key]))
            
            jobfile.write("#SBATCH --nodes=1")
            jobfile.write("module load blender")
            jobfile.write("{} {}".format(self.blender_path, super().get_blender_command(self.blend_file)))


        # Submit jobfile
        #for i in range(self.render_config['max-nb-jobs']):
        #   popen.stuff(['sbatch', jobfile_name])


    def get_status(self):
        return

    def cancel_render(self):
        return

    def get_server_config(self):
        return self.default_config
