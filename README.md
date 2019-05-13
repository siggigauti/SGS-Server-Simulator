# SGS-Server-Simulator
Simulator for small to large scale server farms

To run a sample simulation, open a command line and naviage to the simulation_scripts folder.
Once located in the simulation_scripts folder, there is a single sim.py file that can be run.
  Sim.py uses an argument parser to set up a simulation, you can add servers and dispatchers, set the simulation time and random seeds.
  Type "python sim.py -h" for help with the arguments.
  Can also use argument 'type' to run a preset simulation. For example "python sim.py -type 5" will run a simulation with parameters:
      5 million time units, 2 servers with service rates of 1, arrival rate of 1.75, job size of exponential of 1, and a single dispatcher using JSQ
  
You are free to fork this project and create your own simulation setups, develop scheduling or policy algorithms and run a simulation with them (Take care to use the interface).
