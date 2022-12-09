# Robotic Configurator

Code and documentation for the semester long project live here.

## Packages/Services

This project is split between four packages/services (how they are deployed is not a concern at the moment). Their purpose is documented here.

### Dummy

Named after Tony Stark's Dummy.

Contains core code for basic robot functions, such as forward & inverse kinematics, a Robot class, understanding a robot workspace, and more. This operates as a standalone python package. It is designed so it can be used in other projects.

Written in Python.

In the future, this package would contain more powerful robot control operations.

- Account for the force of gravity, target endpoint torque, payload size, weight, etc.
- More advanced inverse kinematic solvers

### Rolly

Contains the source code for the robot configurator. Generates and searches through the robot space. This codebase relies on the Dummy package to perform any per-robot operation. The code in Rolly is soley responsible for searching through the robot space and finding a robot that matches specified search parameters.

Written in Python.

This package currently implements the bare-minimum to get search working. It will need to be optimized and the search strategies explored in full to provide a usable package to users.

### Api

Contains a simple Flask python application for communicating with the frontend. Simply wraps the Rolly package into a web API.

Written in Python.

This is not critical to the crux of this project.

### Frontend

A React web app that allows users to type in basic information about a robot. In the near future, this should create a visualization for the user using a library like ThreeJS.

In the far future, this service would be responsible for:

- Collecting all information pertaining to the problem requirements
- Allow the user to specify certain configuration parameters, like maximum motor power, maximum joints, etc.
  - This would be optional
  - May include a 3D enviroment for more powerful configuration
- Simulate multiple robot solutions against the problem requirements in 3D for the user to see.

Written in React + Typescript.

## How to get it running

It's best to get the project running with Anaconda. Create a new conda environment and install `numpy`, `scipy`, and `flask`. You can look at the `requirements.txt` in each project folder.

Both `/dummy` and `/rolly` are python packages and must be installed with `pip install -e {path-to-project}\RoboticConfigurator\{rolly or dummy}\`

The `/api` project is the only python project you actually run (at the moment). Run it with `python -m flask run` inside the `/api` folder. The server will start listening on port 5000.

To start the `/frontend`, navigate into the folder and run `npm install` (you must have node and npm installed). After that, run `npm run start`. The server will serve the frontend files on port 3000 by default.

## Problem Statement

Manufacturers need robots for various tasks. To acquire robots, most companies have three options:

1. Design their own from scratch (or hire someone to design a custom robot)
2. Purchase from a large robotic company and customize it to their liking
3. Higher a contractor to choose an existing robot and make it work for the company

The first option is very expensive but highly customizable. Small to medium sized manufacturers cannot afford to design, test, and optimize their own robot. Instead, they (or contracted teams on their behalf) look for an existing robot that comes close to the use case required, and tweak it to make it work. Option 2 and 3 (from the list above) are usually less expensive (relatively) however may fall short of the required operating parameters.

The company wants something cheap (option 2) but perfectly built to solve their problem - a happy medium between 1 & 2. Vention.io is a company that offers a suite of design tools to help solve this problem. The company built a software solution that fulfills option 3 from above, without the need to hire a full team. However, their platform falls short. Their design tool treats robots as discrete parts supplied by a robot manufacturer.

Many robotic companies offer customization packages for their robot platforms. Usually, the customizable options are limited to a small series of add-ons for a fairly static, predesigned robot. Customers first have to know they want an articulated robot and second, how many degrees of freedom the robot should have. From there, they need to know how fast the robot should move, the payload capacity, and much more. Most companies do not offer a robot simulator before purchasing.

## Solution to Problem Statement

A program that takes in human understandable descriptors (not human language) and outputs a specific robot design that belongs to one of the robot groupings. The program would attempt to find a solution to the problem described by the input while minimizing cost.

Examples of human understandable descriptors:
What is the task (perhaps described by having the user demonstrate how a human would solve it in a 3D environment?)
How fast the robot must accomplish its task
What is the max/min payload weight

Robot groupings:

- Articulated
- SCARA
- Delta
- Cartesian

Examples of output:

- An articulated 4 DOF robot CAD file with a pinch grasper using A type electric motors with B type speed controllers, C materials (3D printed metals and plastics in the joints), and a D joint configuration (joint 1 & 2 are placed on top of each other, joint 3 is 1000mm from joint 2, etc.).
- A delta robot with A reach, using B materials, a C type motor, with a D type speed controller.

Extra features:

- A way to simulate the generated robot to verify its design
- Environment configurator (allow the solver to include a robot mount, or maybe a linear robot dolly, etc.)
- Scaled motors and motor controllers included in the solution (programmably designable motors and motor controllers)
- Computer vision tools for object manipulation
- Open source software for controlling the produced robot
- Reconfigure an existing robot designed with the configurator (given a new set of problems, an existing robot configuration, make the smallest amount of changes to the current configuration to solve the new problem)

A complete end to end example might look like this:

- A team describes their problem in the software
- The software produces a robot design with various components (motors, motor controllers, the brain, joint design, mount design, end actuator design and subcomponents)
- The team verifies the design with a simulation environment
- The components made from metal or plastic are 3D printed, the remaining components are sourced.
- From the output design, assembly instructions are created.
- All the individual parts and assembly instructions are packaged and sent to the team.
- The team receives the parts and assembles the robot themselves according to the instructions.
- Open source software allows the team to program the robot. Perhaps the robot configurator could also help configure the control software to make it easier to get started.

## Reasoning

A program that makes it easy for employees of a manufacturing company to describe their problem and produce a robot to solve that problem should maximize customizability and minimize cost. Robots become cheaper but more specialized - currently an oxymoron.

Underlying assumptions made:

- Robots are hard to build from scratch
- Purchasing an existing robot is cheaper, but harder to customize. Users are also locked into the original manufacturer's ecosystem unless a user is willing to engineer very custom hardware and software.
- There is a happy medium of user input that can successfully describe a robot without getting too technical.
  “Solving” for a robot is a discrete graph search problem. There exists a set of bounded solutions that minimize cost and maximize usability according to the described problem.

## The MVP

### A fully realized system

- An easy to use interface to provide non-technical understandable descriptors to the program that parameterize how the robot should interact with its environment
- An algorithm to search the possible robot solution space and choose a configuration that best solves the described problem (including robots of all four types)
- A program to translate the configuration to CAD or other set of manufacturable design files
- A simulator to test the outputted model against user defined scenarios
- Fabrication of the robot using traditional or new manufacturing techniques (3D printing)
- Generated, human-readable, and highly detailed assembly instructions for the robot and associated hardware
- Custom developed (but open sourced) robot controller hardware and software
  Robot actuators and the corresponding controllers. These could potentially be parameterized and included in the output of the programs mentioned above.

### A less capable MVP

- An interface that takes non-technical descriptors that parameterize how the robot should interact with its environment
- An algorithm to search the possible articulated robot space only and choose a configuration that best solves the described problem
- An algorithm that outputs the parameters need to design a CAD model of the robot from scratch, perhaps with the use of CAD automation software

Even the final robotic configurator MVP requires a decent understanding of various disciplines. A successfully implemented solution might require deep knowledge in:

- Robot physics (articulated, SCARA, delta, and cartesian)
- Mechanical engineering (physical design of the robot) and programmatically driven design
- Material science (perhaps 3D printing to effectively produce the physical parts of the robot)
- Motor and motor controller inner workings and capabilities
- Computer science, specifically graph theory and graph search algorithms
- General programming and application modeling
- Physics simulators
- Graphic design (for easy user input collection)
- Web software (for user input)

Narrowing the scope of the robotic configurator for an MVP is necessary.

### Within a couple months

For the purpose of limiting scope for this project, a good system to work towards could:

- Focus on articulated robots
- Take in a small amount of technical parameters
- The minimum set of positions the robot must be able to reach with the last joint
- Only output simple manipulator kinematics
- CAD files are not the output, instead, provide link offsets and joint angles
- Remove some variables
- Rotary joints only (no prismatic)
- Weightless or constant weighted joints
- No manipulator mechanisms
- Assume straight joints only

## Research

### Robots on the market

These companies provide their own homegrown robot solution. Most provide a series of discrete robot designs with specific use cases.

Flexiv

- 3 robot arms with high precision
- Control box with various modules - camera. End tools, AMR (autonomous mobile robot)
- 7 DOFs
- Payload: 4kg, 3.5kg, 10kg
- https://www.flexiv.com/en/

Symbio

- Software manager for robots on the workfloor
- Not much information
- http://symb.io/

Rapid robots

- Fast deployable robots, setup in under than 24 hours
- Subscription based / rent a robot
- Single robot for all uses
- https://www.rapidrobotics.com/solution

RIOS solutions

- Robots as a service
- Specific robot for a specific use case
- https://www.rios.ai/

Kuka robotics

- Dozens of robots
- Sort the robots based on use case and industry
- Sort robots based on payload and reach
- Collaborative and caged
- https://www.kuka.com/en-us/products/robotics-systems/industrial-robots

FANUC

- Dozens of robots
- Sort based on payload, DOF, and reach
- Collaborative and caged
- Custom project development
- These companies usually build custom solutions for specific problems. They are usually contracted.

Summit Engineered Automation

- Project based engineering
- Source hardware and software and implement into a factory
- Various industries, life sciences, food, etc.
- https://www.summitengineeredautomation.com/

SuperDroid Robots

- Work with clients to build custom robots for specific problems
- Highly custom robots, various rovers (for mining operations, agriculture, inspection)
- Offer some prebuilt robot designs
- https://www.superdroidrobots.com/

Pretech

- Custom multi-axis robot end effectors and conveyor systems
- Utilize existing robot designs from existing robotic manufacturers
- http://www.pre-tec.com/
- Software first solutions
- These companies provide software to help configure a custom manufacturing environment. This project (Robotic Configurator) would fit in this category.

Vention

- Drag and drop machine builder
- Code free programming
- Modular hardware (extrusions, linear actuators)
- Design and build a full assembly line or manufacturing station using the drag and drop editor and part library. Open ended design
- Robotic arms are discrete parts provided by Doosan (the robots are not designed in the design editor).
  https://vention.io/

Carnegie Mellon DIY Robot Design

- Drag and drop interface
- 3D printed parts and off the shelf actuators
- Design simulation
- Mostly for legged or wheeled robots
- https://www.cmu.edu/news/stories/archives/2017/june/diy-robot-design.html

Hebi Robotics

- Robot design for subject matter experts
- 3D robot builder (currently in beta)
- Actuators, plates, and links are combined to build and verify a robot
  APIs in common languages for controlling the robot
- https://www.hebirobotics.com/

### Design Automation

Design automation software enables engineers to reuse past design logic to construct new highly-custom instances of a particular object. While not necessarily a robotic configurator, this family of software could help construct custom robots from a shared set of designs. Design automation spans several industries, from graphic design and structural engineering, to PCB development.

Autodesk and SolidWorks both offer mature platforms for automating existing designs. First, an engineer constructs a model. As the model is designed, the engineer creates “variables” and uses these in the design construction. Later, these variables can be changed, and the entire model will adopt the new parameters. These tools are designed to save engineers time. Rather than having to rework an entire model to meet new specifications, users of the software change the corresponding inputs to the system and the design updates accordingly.

Solidworks DriveWorks

- Autodesk Inventor iLogic
- Robot Libraries
- Robotics Library is a C++ library for “robot kinematics, motion planning and control.” https://www.roboticslibrary.org/

IKPY is a robotic library for calculating inverse kinematics and forward kinematics of general robots.
https://github.com/Phylliade/ikpy

### General Robotic Information

Much of the time spent on this project involved heavy research into how robots work, understanding the best methods to performing inverse kinematics, best ways to represent robots, etc.

I pulled concepts from several sources. However, all the code in this repo is my own.

Books:

- “Introduction to Robotics Mechanics and Control”
- "Robotics, Vision and Control"
- "Modern Robotics"

Web resources:

- https://homes.cs.washington.edu/~todorov/courses/cseP590/06_JacobianMethods.pdf
- http://boris-belousov.net/2016/07/29/jacobians
- https://cseweb.ucsd.edu/classes/wi17/cse169-a/slides/CSE169_09.pdf
- https://robotics.stackexchange.com/questions/4610/forward-kinematics-d-h-parameters-for-perpendicular-joint-axes
- https://blog.paperspace.com/intro-to-optimization-in-deep-learning-gradient-descent/
- https://www.slideserve.com/antonia/inverting-the-jacobian-and-manipulability
- https://motion.cs.illinois.edu/RoboticSystems/InverseKinematics.html
- https://www.geometrictools.com/Documentation/EulerAngles.pdf
- https://modernrobotics.northwestern.edu/nu-gm-book-resource/introduction-autoplay/#department

## Common Questions

Why build the inverse kinematics yourself (as opposed to using existing libraries)

- I wanted to gain a deep understanding of how robots work, this included a deep dive into IK specifics.
- Many of the implmentations are written in MatLab, which I am not accustomed to.

Why is so slow?

- There were a couple iterations on how to design the "rolly" package or search solver. I originally wanted to represent this problem as a graph search problem. Robots would be represented as nodes and edges from one Robot to the next would represent one single discrete change. This idea wasn't entirely abandoned, it just didn't work at first. In order to get something working in a timely manner, I decided to abandon (for now) this solution.
- IK is expensive. I need to do better at preventing the search algorithm from ever running the IK solver.
- I need to better represent the workspace of a robot. I investigated interval trees to help search through the workspace, but I abandoned that since most robots operate within the same intervals. The better solution would be to preproccess each robot's workspace with a sampling of points for that best represent the robot workspace. This is a work in progress.
- Overall, this first version is extremely slow since it is very niave.

What's next

- Better IK solver. Jacobian transpose works, but the current implementation is too slow. It has a hard time solving for orientation as well. I switched to a jacobian psuedoinverse, but still has issues solving for orientation.
- More important: A better preprocessor. Lots of the calculation should be performed before the search algorithm is actually ran. Generating a easily searchable workspace that can better narrow down robots is very important.
