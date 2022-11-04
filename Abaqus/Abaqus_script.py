# Jacques Terblanche
# 22548602

from abaqus import *
from math import *
import testUtils
testUtils.setBackwardCompatibility()
from abaqusConstants import *
import sketch
import part
import mesh
import json
import odbAccess
import os
import step


# Clear generated files from previous jobs
job_name = 'Job-1'
files_ext = ['.jnl','.inp','.res','.lck','.dat','.msg','.sta','.fil','.sim',
              '.stt','.mdl','.prt','.ipm','.log','.com','.odb_f','.odb',]
for file_ex in files_ext:
    file_path = job_name + file_ex
    if os.path.exists(file_path):
        os.remove(file_path)


if os.path.exists("angle.txt"):
    os.remove("angle.txt")


# Parameters 
p = open('input_parameters.json')
input_parameters  = json.load(p)

cavity_total_depth = input_parameters[0]/2 # mm
thickness = input_parameters[1] # mm
num_cells = input_parameters[2] # Number of cells
bottom_cavity_height = input_parameters[3] # mm
bottom_thickness = input_parameters[4] # mm

pressure_load = input_parameters[5] # MPa
Gravity_load = input_parameters[6] # mm/s^2

mesh_size = 3
mesh_min = 0.5


# Create shorter variable names for commonly used attributes
myModel = mdb.Model(name='Model A')
myModels = mdb.models['Model A']
myAssembly = myModels.rootAssembly



#######
# Create sketch A 
#######
bottom_height = bottom_cavity_height + bottom_thickness
mySketch = myModel.ConstrainedSketch(name='Sketch A', sheetSize=200.0)

f = open('input_data.json')
xyCoordsInner  = json.load(f)

start = []
top_connectors = []
end = []
distance_from_cell_to_bc = xyCoordsInner[-1][0] - xyCoordsInner[0][0] + thickness/2
for j in range(num_cells):
    if j == 0:
        start = [[xyCoordsInner[0][0]+(j*distance_from_cell_to_bc),xyCoordsInner[0][1]],[xyCoordsInner[0][0]+(j*distance_from_cell_to_bc),xyCoordsInner[0][1]-bottom_height]]
        
    if j == num_cells-1:
        end = [[xyCoordsInner[0][0]+distance_from_cell_to_bc+(j*distance_from_cell_to_bc),xyCoordsInner[0][1]-bottom_height],[xyCoordsInner[0][0]+distance_from_cell_to_bc+(j*distance_from_cell_to_bc),xyCoordsInner[0][1]]]
    
        
    one_cell_coords = [[xyCoordsInner[0][0]+distance_from_cell_to_bc+(j*distance_from_cell_to_bc),xyCoordsInner[0][1]-bottom_height]]
    connector_end = [[xyCoordsInner[-1][0] + thickness/2+(j*distance_from_cell_to_bc),xyCoordsInner[-1][1]]]
    top_connectors = [[xyCoordsInner[0][0]+distance_from_cell_to_bc+(j*distance_from_cell_to_bc)-thickness/2,xyCoordsInner[-1][1]],[xyCoordsInner[0][0]+distance_from_cell_to_bc+(j*distance_from_cell_to_bc),xyCoordsInner[-1][1]]]
    bottom_coords = start + one_cell_coords+  end   

    xyCoordsInner_new = []

    for k in range(len(xyCoordsInner)):
        xyCoordsInner_new.append([xyCoordsInner[k][0]+(j*distance_from_cell_to_bc),xyCoordsInner[k][1]])
    mySketch.Spline(xyCoordsInner_new)  # spline

    
    for i in range(len(top_connectors)-1):
        mySketch.Line(point1 = top_connectors[i],
        point2=top_connectors[i+1])
        
for i in range(len(bottom_coords)-1):
    mySketch.Line(point1 = bottom_coords[i],
    point2=bottom_coords[i+1])



myPart = myModel.Part(name = 'Part A', dimensionality = THREE_D,
    type=DEFORMABLE_BODY)

#######
# Extrude sketch A 
#######


myPart.BaseSolidExtrude(sketch = mySketch, depth = cavity_total_depth)
myPart.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset =thickness+thickness/2)

#######
# Create sketch B 
#######


e1, d2 = myPart.edges, myPart.datums
t = myPart.MakeSketchTransform(sketchPlane=d2[2], 
    sketchPlaneSide=SIDE1, sketchOrientation=LEFT, origin=(0, 0, 0))
mySketch2 = myModel.ConstrainedSketch(name='Sketch B', sheetSize=600, transform=t)

mySketch2.setPrimaryObject(option=SUPERIMPOSE)



# Produce transformed sketch (for internal cavity cutout extrusion)

xy_transform_1 = []
for j in range(num_cells):
    xy_transform = []
    bottom_coords = []
    temp_counter = 0
    middle = int(round(len(xyCoordsInner)/2))
    for x in range(middle):
        if xyCoordsInner[x][0] + thickness < xyCoordsInner[middle][0]:
            xy_transform.append([xyCoordsInner[x][0] + thickness+(distance_from_cell_to_bc*j),xyCoordsInner[x][1] -thickness])
            temp_counter +=1

    xyCoordsInner_ext = xyCoordsInner[int(round(len(xyCoordsInner)/2)+(middle-temp_counter+1)):]
    dist = (xyCoordsInner[-1][0]-xyCoordsInner[0][0])/2
    xy_transform.append([dist+(distance_from_cell_to_bc*j),xy_transform[-1][1]])

    for x in range(len(xyCoordsInner_ext)):
        xy_transform.append([xyCoordsInner_ext[x][0] - thickness+(distance_from_cell_to_bc*j),xyCoordsInner_ext[x][1] -thickness])
    
    mySketch2.Spline(xy_transform)
    
    if j== 0:
        xy_transform_1 = xy_transform
    
    bottom_coords = [[xy_transform_1[0][0]+(distance_from_cell_to_bc*j),xy_transform_1[0][1]], [xy_transform_1[0][0] +(distance_from_cell_to_bc*j),xyCoordsInner[0][1] -bottom_height +bottom_thickness],[xy_transform_1[-1][0] + (distance_from_cell_to_bc*j),xyCoordsInner[-1][1] -bottom_height+bottom_thickness], [xy_transform_1[-1][0]+(distance_from_cell_to_bc*j),xy_transform_1[-1][1]]]
    for i in range(len(bottom_coords)-1):
        mySketch2.Line(point1 = bottom_coords[i],point2=bottom_coords[i+1])
        
middle = int(round(len(xy_transform_1)/2))

direction_edge = myPart.edges.findAt(((xyCoordsInner[0][0],xyCoordsInner[0][1]-bottom_cavity_height,cavity_total_depth)),)

#######
# Extrude sketch B 
#######


mySketch2.unsetPrimaryObject()
myPart.CutExtrude(sketchPlane=d2[2],sketchUpEdge= direction_edge,sketch = mySketch2, depth = cavity_total_depth,flipExtrudeDirection=ON)


#######
# Create surfaces for boundary conditions, loads 
#######

# Create set for boundary condition
# The following code was based on a youtube video from Dr.-Ing. Ronald Wagner (https://www.youtube.com/channel/UCU3dmUB40wf5RCEGp9UMtbA) 
face = ()
f = myPart.faces
myFace = f.findAt(((xyCoordsInner[0][0],xyCoordsInner[0][1],cavity_total_depth/2)),)
face = face + (f[myFace.index:myFace.index+1], )
myPart.Set(faces=face, name='BC_set')

face = ()
f = myPart.faces
myFace = f.findAt(((xy_transform[middle][0],xy_transform[0][1]-bottom_cavity_height,cavity_total_depth)),)
face = face + (f[myFace.index:myFace.index+1], )
myPart.Set(faces=face, name='Sym_plane_set')

# The youtube modified code ends here


# Create surfaces for pressure loading and self-contact
list_of_coords = []
for j in range(num_cells):

    #For outer irregular roof
    outer_irr_roof=myPart.faces.getClosest(coordinates=(((xy_transform_1[middle][0]+(distance_from_cell_to_bc*j),xy_transform_1[middle][1]+thickness,cavity_total_depth/2)),))
    #For inner floor
    inner_floor=myPart.faces.getClosest(coordinates=(((xy_transform_1[middle][0]+(distance_from_cell_to_bc*j),xy_transform_1[0][1]-bottom_cavity_height,cavity_total_depth/2)),))
    #For inner irregular roof
    inner_irr_roof=myPart.faces.getClosest(coordinates=(((xy_transform_1[middle][0]+(distance_from_cell_to_bc*j),xy_transform_1[middle][1],cavity_total_depth/2)),))  
    #For inner regular wall 1
    inner_reg_wall_1=myPart.faces.getClosest(coordinates=(((xy_transform_1[0][0]+(distance_from_cell_to_bc*j),xy_transform_1[0][1]-1,cavity_total_depth/2)),))
    #For inner regular wall1 2
    inner_reg_wall_2=myPart.faces.getClosest(coordinates=(((xy_transform_1[-1][0]+(distance_from_cell_to_bc*j),xy_transform_1[-1][1],cavity_total_depth/2)),))
    #For inner back wall
    inner_back_wall=myPart.faces.getClosest(coordinates=(((xy_transform_1[middle][0]+(distance_from_cell_to_bc*j),xy_transform_1[middle][1]-thickness,thickness)),))

    list_of_coords = list_of_coords + [outer_irr_roof,inner_floor,inner_irr_roof,inner_reg_wall_1,inner_reg_wall_2,inner_back_wall]
    


def assign_surface(coordinates,number):
    v=myPart.faces.findAt((((coordinates[0][1])),))
    myPart.Surface(name= 'Surface_'+str(number), side1Faces=v)
    
    

j = 0
outer_surfaces = []
inner_surfaces = []
for k in range(len(list_of_coords)):
    
    assign_surface(list_of_coords[k],k)
    
    if j == 0:
        outer_surfaces = outer_surfaces + [myPart.surfaces['Surface_'+str(k)]]
        
    if j > 0 and j < 6:
        inner_surfaces = inner_surfaces + [myPart.surfaces['Surface_'+str(k)]]
   
    j += 1
    if j == 6:
        j = 0
    
        
#Combine outer surfaces into single surface
myPart.Surface(name='Outer', side1Faces=myPart.faces.findAt((((list_of_coords[0][0][1])),)))
for x in range(len(outer_surfaces)-1):
    myPart.SurfaceByBoolean(name='Outer', surfaces=(outer_surfaces[x+1],myPart.surfaces['Outer'],))

#Combine inner surfaces into single surface
myPart.Surface(name='Inner', side1Faces=myPart.faces.findAt((((list_of_coords[1][0][1])),)))
for x in range(len(inner_surfaces)-1):
    myPart.SurfaceByBoolean(name='Inner', surfaces=(inner_surfaces[x+1],myPart.surfaces['Inner'],))

#Remove uncombined inner surfaces 

for y in range(len(list_of_coords)):
    del (myPart.surfaces['Surface_'+str(y)],)

      
#######
# Assign mesh and element type  
#######  

# Chosen element type = Tetrahedral elements with quadratic order and hybrid formulation (ref: Finite Element Modeling of Soft Fluidic Actuators:Overview and Recent Developments (Xavier et al,2021))
pickedRegions =(myPart.cells, )
elemType1 = mesh.ElemType(elemCode=C3D20R)
elemType2 = mesh.ElemType(elemCode=C3D15)
elemType3 = mesh.ElemType(elemCode=C3D10H)
myPart.setMeshControls(regions=myPart.cells, elemShape=TET, technique=FREE)

myPart.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2, elemType3))
myPart.seedPart(size=mesh_size, deviationFactor=0.1, minSizeFactor=mesh_min)
myPart.generateMesh()

myAssembly.DatumCsysByDefault(CARTESIAN)
myAssembly.Instance(name='Assembly A', part=myPart, dependent=ON)
myInstances = myAssembly.instances['Assembly A']

#######
# Assign boundary conditions, loads, contact properties and material
#######


# Create boundary conditions and loads

region = myInstances.sets['BC_set']
myModels.EncastreBC(name='BC-1', createStepName='Initial', region=region, localCsys=None)

region = myInstances.sets['Sym_plane_set']
myModels.ZsymmBC(name='BC-sym', createStepName='Initial', region=region, localCsys=None)



#Create gravity step and loads

myModels.StaticStep(name='Gravity', previous='Initial', maxNumInc=1000, initialInc=0.01, minInc=1e-08, nlgeom=ON)
myModels.Gravity(name='Gravity_load', createStepName='Gravity', comp1=Gravity_load, distributionType=UNIFORM, field='')
myModels.steps['Gravity'].control.setValues(allowPropagation=OFF, 
        resetDefaultValues=OFF, discontinuous=ON)
        

#Create pressure step and loads

myModels.StaticStep(name='Pressure', previous='Gravity', maxNumInc=1000, initialInc=0.001, minInc=1e-08, nlgeom=ON)
 
region = myInstances.surfaces['Inner']
myModels.Pressure(name='Pressure_load', createStepName='Pressure', region=region, distributionType=UNIFORM, field='', magnitude=pressure_load, amplitude=UNSET)


#Create material

myModels.Material(name='Moldstar_15')
myModels.materials['Moldstar_15'].Density(table=((1.139e-09, ), ))
myModels.materials['Moldstar_15'].Hyperelastic(materialType=ISOTROPIC, testData=OFF, type=OGDEN, n=3, volumetricResponse=VOLUMETRIC_DATA, table=((-6.50266e-06, -21.322, 0.216863, 1.1797, 0.00137158, 4.88396, 0.0, 0.0, 0.0), ))

#Create section and assign it


myModels.HomogeneousSolidSection(name='Section-1', material='Moldstar_15', thickness=None)

pickedRegions =(myPart.cells, )
myPart.SectionAssignment(region=pickedRegions, sectionName='Section-1', offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)


#Create tangential contact properties and assign contact
myModels.ContactProperty('Contact')
myModels.interactionProperties['Contact'].TangentialBehavior(formulation=FRICTIONLESS)

region=myInstances.surfaces['Outer']
myModels.SelfContactStd(name='Wall_contact', createStepName='Initial', surface=region, interactionProperty='Contact', thickness=ON)


#######
# Create node sets to track displacement
#######


allNodes = myModels.parts['Part A'].nodes
box_delta = mesh_min/10

def create_node_set(x,y,z,delta,name):
    myNode = allNodes.getByBoundingBox(x-delta, y - delta, z-delta, x + delta, y+ delta, z+ delta)
    myPart.Set(nodes=myNode, name=name)


# Create the fixed node point 
create_node_set(0,xyCoordsInner[0][1]-bottom_height,cavity_total_depth,box_delta,'Fixed_node')
fixed_label = myPart.sets["Fixed_node"].nodes[0].label 

# Create the free end node point 
create_node_set(distance_from_cell_to_bc*num_cells,xyCoordsInner[0][1]-bottom_height,cavity_total_depth,box_delta,'End_node')
free_label = myPart.sets["End_node"].nodes[0].label

important_nodes = [fixed_label,free_label]

# Set output fields
myModels.fieldOutputRequests['F-Output-1'].setValues(variables=(
    'S', 'U','COORD'), frequency=10)
myModels.historyOutputRequests['H-Output-1'].setValues(variables=(
    'IRA1', 'IRA2', 'IRA3', 'IRAR1', 'IRAR2', 'IRAR3'), frequency=10)

# Write 0 to text file (placeholder angle)
with open('angle.txt', 'w') as f:
    f.write("0")


#######
# Submit job
#######


# Create and submit the job
myJob = mdb.Job(name='Job-1', model='Model A', description='', type=ANALYSIS, 
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=99, 
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=4, 
        numDomains=4, numGPUs=0)
        

myJob.submit(consistencyChecking=OFF)
fileName = 'Job-1.odb'
myJob.waitForCompletion()


#######
# Extract results
#######

odbFile = odbAccess.openOdb(path = fileName)
p = odbFile.rootAssembly.instances['Assembly A']
n1 = p.nodes
pickedNodes =(n1, )
all_nodes = odbFile.rootAssembly.NodeSet(name = 'Whole_model', nodes = pickedNodes)
output_array = []
 
# Get x data of the free and fixed point 
free_disp_x = odbFile.steps['Pressure'].frames[-1].fieldOutputs['COORD'].getSubset(region=all_nodes).values[free_label-1].data[0]
fixed_disp_x = odbFile.steps['Pressure'].frames[-1].fieldOutputs['COORD'].getSubset(region=all_nodes).values[fixed_label-1].data[0]

# Get y data of the free and fixed point 
free_disp_y = odbFile.steps['Pressure'].frames[-1].fieldOutputs['COORD'].getSubset(region=all_nodes).values[free_label-1].data[1]
fixed_disp_y = odbFile.steps['Pressure'].frames[-1].fieldOutputs['COORD'].getSubset(region=all_nodes).values[fixed_label-1].data[1]

# Determine the difference in displacement
x_dif = abs(fixed_disp_x - free_disp_x)
y_diff = abs(fixed_disp_y - free_disp_y)
# Calculate the angle from this difference
angle = atan(y_diff/x_dif) * 180 /pi  
    
# Write this angle to the angle.txt file (to be read by evolve script)
with open('angle.txt', 'w') as f:
    f.write(str(angle))
    
# Close results file
odbFile.close()

# Remove Abaqus's recorded steps for backups (this tends to fill up the folder)
if os.path.exists("abaqus.rpy.1"):
    os.remove("abaqus.rpy.1")
