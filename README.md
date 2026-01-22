# Classical-Mechanics-Simulator-in-2D

The aim of this project is to develop a system for simulating and visualizing classical mechanics phenomena in a two-dimensional space.
The application allows users to define initial conditions — such as force and velocity vectors acting on objects — and then observe the changes in their values and trajectories over time.


The system is designed to:

- enable interactive exploration of physical phenomena,
- provide clear and intuitive visualization of simulations,
- support easy extension with new models and experimental conditions.

## Installation Guide

This guide explains how to install and run the **Classical Mechanics Simulator in 2D** written in Python.
The project is hosted on GitHub and can be installed either using **Git** or by **manually downloading** the source code.

## Requirements

#### Required
- **Python 3.9+** (or compatible version)
- **pip** (comes bundled with Python)

#### Optional
- **Git** (recommended for cloning the repository)

You can verify your Python and pip installation with:

```bash
python --version
pip --version
```

## Installation Options

### Option 1: Clone the Repository Using Git (Recommended)

1. Clone the repository:

```bash
git clone https://github.com/FranciszekCieslik/Classical-Mechanics-Simulator-in-2D.git
```

2. Navigate to the project directory:

```bash
cd Classical-Mechanics-Simulator-in-2D
```

---

### Option 2: Manual Download (Without Git)

1. Go to the GitHub repository page.
2. Click **Code → Download ZIP**.
3. Extract the archive.
4. Navigate into the extracted folder:

```bash
cd Classical-Mechanics-Simulator-in-2D
```

## Create a Virtual Environment

It is strongly recommended to use a virtual environment.

### 1. Create the virtual environment:

```bash
python -m venv .venv
```

### 2. Activate the virtual environment:

**Windows (PowerShell / CMD):**

```bash
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

After activation, your terminal prompt should indicate that `.venv` is active.

## Install Dependencies

Install all required Python packages using the provided `requirements.txt` file:

```bash
pip install -r .\Classical-Mechanics-Simulator-in-2D\requirements.txt
```

> Make sure the virtual environment is activated before running this command.

## Run the Application

From the project root directory (`Classical-Mechanics-Simulator-in-2D`), run:

```bash
python .\app\main.py
```

The simulator should now start.


## Troubleshooting

* If `python` is not recognized, try `python3`.
* If activation scripts are blocked on Windows, run PowerShell as Administrator and execute:

```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Notes

* Always activate the virtual environment before running the application.
* To exit the virtual environment, use:

```bash
deactivate
```
