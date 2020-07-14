# Installation Guide

This guide will help you install and run Lego 3.

The purpose of this guide is so you will be able to run the example tests successfully, on your machine.  

## Requirements

Linux machine with:

* Internet connection.
* `python 3.8.2` installed.

> **Note:** This guide tested on *Ubuntu 18.04.4 LTS*.

## Installation

### Docker

> **Note:** The Docker environment used just for testing Lego 3 at home. In real life, we can use the real setup for testing.  

Docker is easy to install using the [docker installation guide](https://docs.docker.com/install/linux/docker-ce/ubuntu/).

For easy setup of the docker containers, we also use the `docker-compose` tool, which you can install using [docker-compose installation guide](https://docs.docker.com/compose/install/).

> **Note:** On some Linux machines, the `dns-docker` doesn't work. It can be fixed by the following command:
>
>  ```bash
>  sudo apt-get install resolvconf
>  ```

### Repository

For installing Lego 3 itself, follow the next steps.

Clone Lego 3 repository and checkout to `master` branch:

```bash
git clone git@github.com:Steven17D/Octavius.git
git checkout master
```

Install the relevant PyTest plugins (include Lego 3 plugin):

```bash
python3.8 -m pip install -e lego
python3.8 -m pip install -r requirements.txt
```

## Running

First, we will start the docker containers by the following commands:  

```bash
cd docker
docker-compose up --build
```

> **Note:** Notice you can monitor the docker containers using the command:  
>
>```bash
>cd docker
>watch docker-compose ps
>```

Now, we can run the tests. Just run the following command:

```bash
python3.8 -m pytest tests/test_tetanus.py
```

All of the tests should pass successfully in about a minute :)
