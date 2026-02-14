# EMEC Micromouse – UQMARS 2026

This repository contains the code, hardware files, and documentation for the EM Engineering Club (EMEC) Micromouse robot developed for the 2026 UQMARS Micromouse Competition.

The repository was actively used during development and competition for testing, iteration, and file management. This README provides an overview of the robot design, hardware modifications, and software architecture.

🎥 Test Day Video
(May update with official competition footage)
https://www.youtube.com/watch?v=nQMq9lbTZGA

# Hardware

Our design is heavily based on the UQMARS starter Micromouse platform:

🔗 https://github.com/uqmars/starter-micromouse

The original repository contains:
- PCB design files
- Chassis CAD files
- Starter parts list

**Modifications We Made**

We modified the following subsystems:
- Wall detection sensors
- Battery configuration

**Wall Detection Sensors
**
We replaced the original wall detection system with three PiicoDev VL53L1X Time-of-Flight (ToF) distance sensors:

🔗 https://core-electronics.com.au/piicodev-laser-distance-sensor-vl53l1x.html

Three sensors were used (front, left, right).

To mount them, we designed and 3D-printed custom holders:

🔗 05 custom hardware/tof_holder_v01.stl

To connect the sensors to the starter kit PCB, the following components were used:
- PiicoDev Breadboard Adapter, https://core-electronics.com.au/piicodev-breadboard-adapter.html
- Adafruit PCA9546 4-Channel I2C Multiplexer (TCA9546A compatible), https://core-electronics.com.au/adafruit-pca9546-4-channel-stemma-qt-qwiic-i2c-multiplexer-tca9546a-compatible.html

**I2C Configuration
**
GPIO 4 and GPIO 5 were used for I2C communication. Refer to the source code for exact pin mapping and sensor indexing.

**Battery
**
The lighter, lower-capacity LiPo battery was replaced with the higher-capacity battery included in the starter kit to improve runtime and reliability during competition runs.

# Software
The software was rewritten from the original starter kit code.

**Goals of the Rewrite
**
- Enable compatibility with the Micromouse simulator
- Allow algorithm testing without hardware
- Enable parallel development within the team
- Maintain a shared logic structure between simulation and hardware

Micromouse simulator used:
🔗 https://github.com/mackorone/mms

The implementation was completed under competition time constraints, so the structure is functional but not optimised for readability.

Main hardware testing branch:
🔗 02 test hardware code/09 MM DRIVERS/0208_bot1test02

**Maze Strategy
**
Our robot performed:
- Exploration phase only
- No optimized speed run using a known maze
Unlike the winning team, our robot did not perform a second optimized run after mapping the maze.
Between runs, we tuned motion parameters using a “bonk” maneuver to refine wall alignment and increase maze-solving speed.

**Code Architecture
**
Below is an overview of the main files:
- main.py - Entry point of the system.Handles integration of all classes and execution flow.
- PIDMotor.py - Motor control module. Motor initialization, Encoder reading, PID control loops, Distance and angle movement functions
- API.py - Hardware abstraction layer (apologies for the poor file name). Responsible for real-world robot interaction. In theory, replacing this file with the Micromouse simulator API should allow the same logic to run in simulation (not fully tested).
- Maze.py - Defines the Maze object. Stores discovered walls and maze structure during exploration.
- Mouse.py - Tracks current position, orientation, movement decisions
- Direction.py - Utility class for handling directional logic and conversions.
- TOFSensors.py - Handles ToF sensor configuration, I2C multiplexer interaction, sensor helper functions.
- Other Files - Additional drivers for sensors and hardware components.

# Acknowledgements
Much of the foundational work is based on:
- Micromouse Simulator by Mackorone, https://github.com/mackorone
- PiicoDev drivers by Core Electronics, https://github.com/CoreElectronics
Our contribution primarily involved integrating these systems and adapting them to work cohesively for our hardware and competition requirements.

# Final Notes
We hope this repository is helpful for anyone attempting the Micromouse challenge, competing in UQMARS, or building their own autonomous maze-solving robot.

---
# EMEC-micromouse
EscapeManorEngineeringClub. Micrmouse team
Micrmouse team documents, code, and files

Report: https://github.com/riku-ohyea/EMEC-micromouse/blob/main/06%20Submission%20Documents/EMEC%20Micromouse%20Documentation%202026.pdf

Video: https://youtu.be/1biOx0Q3veI

Team Google Drive: https://drive.google.com/drive/folders/1eSfBlvatloG3tSRXEPzZx30s3_RQ47VF?usp=drive_link (Only accessible to team members)
