# Blender remote render (Brr)

Brr offers a client-server approach to Blender rendering. The client side is an addon that handles connecting to the server and sending files and configurations while the server is tasked to receiving files and performing the rendering. On the server side, multiples backend can be implemented to access hardware. For now, only Slurm scheduler interface is implemented as it is commonly found on HPC systems.

Communication between the client and server is handled by ØMQ messages usually going through an ssh tunnel, it is using a DEALER-ROUTER design for two way communications.  

On the server side, jobs are running Blender with a specific python script that dynamically decides which frame to render next based on what has already been rendered by other jobs.


Current feature list and progress:
- [x] Connect to remote server
- [x] Send Blender file to remote server
- [x] Send configuration to remote server
- [x] Remote server write Slurm job file
- [x] Remote server launch slurm job
- [x] Remote server handles parallelisation of animation rendering
- [ ] Remote server sends progress back to client
- [ ] Client sends other assets to server
- [ ] Server sends back rendered images


## Funding
Funding provided by EPCC, University of Edinburgh.