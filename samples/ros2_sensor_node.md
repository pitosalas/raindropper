# Project Specification: ros2-sensor-node

## What
A ROS2 Python package containing a sensor node that reads simulated IMU data and publishes it on a standard topic.

## Who
ROS2 developers building robot perception pipelines who need a working sensor node as a starting point.

## Problem
Writing a correctly structured ROS2 Python package from scratch is tedious and error-prone. This provides a clean, tested template.

## Key Features
- ROS2 Python package (`ament_python`) with proper `setup.py` and `package.xml`
- `ImuPublisher` node that publishes `sensor_msgs/Imu` messages at a configurable rate (default 10 Hz)
- IMU data is simulated (random values within realistic ranges)
- Rate and topic name configurable via ROS2 parameters
- Launch file to start the node
- Unit tests using `pytest` and `rclpy` mocking

## Constraints
- ROS2 Humble or later
- Python 3.10+
- `rclpy`, `sensor_msgs`, `geometry_msgs` — no additional dependencies
- Follow ROS2 Python package conventions exactly
- No C++ components

## Out of Scope
- Real hardware integration
- Sensor fusion or filtering
- Visualization (no RViz config)
- CI/CD pipeline
