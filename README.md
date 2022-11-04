# Generative_design_cross_section

A implementation of a generative design framework for generating soft bending actuators based on cross-section design. This forms part of a final year mechanical engineering project at Stellenbosch University.

Take note, a Abaqus CAE teachers' license is required. Ensure that this license is available to use on the current network before launching program. 

To launch the program
1) Open main.py 
2) Set program parameters
3) Run main.py

----------------------------
After program has finished
----------------------------

To view generated data
4) View resultant angles of population in log.txt in the data folder
5) View generetaed coordinates in Cross_sections and view generated coordinate data in Coordinate_storage

To generate a 3D model of your chosen individual
6) Copy the Abaqus.py script to your Abaqus CAE working directory 
7) Copy your selected design from Coordinate_storage to your Abaqus CAE working directory and rename to input_data.json
8) Launch Abaqus CAE (with GUI)
9) Run script from Abaqus interface 
10) After job completion, export model to your chosen CAD/3D format



