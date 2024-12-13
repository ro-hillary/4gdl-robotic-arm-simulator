# Robotic Arm Simulator

## Project Description

A comprehensive Python-based robotic arm simulation toolkit with advanced database management, user authentication, and interactive GUI for patient and configuration tracking.

## Features

- Robotic Arm Kinematics Simulation
- User Authentication System
- Patient Management
- Configuration Tracking
- Database Backup Mechanism
- Secure Password Handling

## Prerequisites

- Python 3.8+
- NumPy
- Robotics Toolbox
- SpatialMath
- Matplotlib
- SQLite
- Werkzeug (for password security)
- Tkinter

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/robotic-arm-simulator.git
cd robotic-arm-simulator
```

2. Install required dependencies:
```bash
pip install numpy roboticstoolbox-python spatialmath-python matplotlib werkzeug
```

## Project Structure

- `robot.py`: Robotic arm simulation core class
- `controller.py`: Application entry point
- `model.py`: Database management and user authentication
- `GUI.py`: Graphical user interface
- `setup.py`: Executable configuration

## Database Schema

The application uses SQLite with the following tables:
- Users
- Roles
- Patients
- Configuration
- Initial Position (PI)
- Final Position (PF)

## Usage

### Running the Application
```bash
python controller.py
```

## Key Components

### Database Management
- Secure user authentication
- Patient record management
- Configuration tracking
- Automatic database backup

### Security Features
- Password hashing
- Role-based access control
- Automatic database backups

## Configuration

Default admin credentials:
- Username: admin
- Password: admin

## Building Executable

```bash
python setup.py build
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## License

Distributed under the MIT License.

## Contact

Your Name - robertandy2001@example.com

Project Link: https://github.com/ro-hillary/4gdl-robotic-arm-simulator
