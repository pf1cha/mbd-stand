# MBD-Stand: Distributed LLM Training Simulator

![alt text](https://img.shields.io/badge/python-3.12%2B-blue)
![alt text](https://img.shields.io/badge/status-research_prototype-orange)


This repository contains the source code for the prototype of the educational demo-stand for the model-based development used as a training demo to allow for hands-on testing of student's research hypotheses only for educational purposes.

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Output Format](#output-format)
- [Project Structure](#project-structure)
- [Contact](#contact)

---

## About
Training modern LLMs like GPT-5, Gemini, and DeepSeek requires massive computing clusters where network communication 
often becomes the thing that engineers try to diminish.
MBD-Stand is a simulator that allows to test different parallelism strategies and 
communication algorithms in a distributed training of LLMs without the necessity to train cumbersome models in real life.
As a result, engineers can test their research hypotheses and make informed decisions about the design of their training clusters,
which can lead to significant improvements in training efficiency and cost-effectiveness.

It is designed for:
* Educational purposes
* Research purposes
* System design and optimization

---

## Features

- Discrete Event Simulation (DES) core for modeling distributed training processes, which allows for accurate 
representation of the complex interactions between different components of the training system.
- Support for various parallelism strategies, including data parallelism, model parallelism, and pipeline parallelism, 
which enables users to explore different approaches to distributed training and their impact on performance.
- Collective Algorithms. The simulator includes implementation of standard MPI/NCCL algorithms, like Ring and Halving-Doubling.
- Network configuration. Users can configure network parameters such as latency and bandwidth.
- Structured output. JSON-based logs, which trace the process of training and allow users to visualise and analyse the results.
---


## Installation

### Prerequisites

- Python >= 3.12
- Standard libraries (`json`, `heapq`, `uuid`)

### Steps

```bash
# Clone the repository
git clone <project-link-here>
cd mbd-stand

# Create a virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

To run a simulation, provide a configuration file and an output path for the logs.

```bash
python main.py -o <output file> -c <config file>.json
```
Arguments:
* -c, --config: Path to the configuration file (YAML or JSON).
* -o, --output: Path to the output file where the simulation logs will be saved in JSON format.

---

## Configuration
Create a `.yaml` or `.json` file in the root directory or provide 
a full path to the configuration file. Here is the example of yaml configuration.

```yaml
parallelism:
  TP: 1    # Tensor Parallelism
  PP: 4    # Pipeline Parallelism
  DP: 4    # Data Parallelism

data:
  size: 400

network:
  latency: 0.0005
  bandwidth: 100.0

collective_communication:
  - type: P2P

  - type: AllReduce
    algorithm: Ring

  - type: ReduceScatter
    algorithm: HD

  - type: AllGather
    algorithm: Ring

  - type: P2P
```
---

## Output Format

The simulation logs are saved in JSON format, which contains the timeline of events.

```JSON
{
    "engine_id": "7c8d63e6-ab6d-4a1a-b4bc-aebe36644d1a",
    "events": [
        {
            "uuid": "fec9b75d-20ce-4115-b4e2-ae03a62b5e57",
            "event_type": "AllReduceStepEvent",
            "handler_type": "AllReduceStepHandler",
            "method": "RING",
            "applying_time": 0.0,
            "data_size": 100
        },
        {
            "uuid": "4359cdd5-cce7-45f0-a4d2-80e8e41790e6",
            "event_type": "DataTransferEvent",
            "handler_type": "DataTransferHandler",
            "applying_time": 0.0,
            "transfer_time": 0.0044062500000000004,
            "gpu_source": "4050b52c-e328-4294-8452-d00acedd0560",
            "gpu_destination": "d8e24d4a-7c62-43f5-b41a-1ca9029fedfb",
            "data_size": 0.390625
        } 
    ]
}
```

---

## Project Structure

```
mbd-stand/
├── docs/
|   
├── lib/
│   ├── results/ -examples of simulation
│   ├── src/
|   |   ├── core/ - a core for DES
|   |   └── network_lib/ - a library for network simulation
│   └── test/ - folder with tests
|   
│
├── soft/
├── public/
├── template.json
├── template.yaml
└── README.md
```
---

## Contact

Project Link: <link-for-project>
