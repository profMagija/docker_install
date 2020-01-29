# Docker install

"Install" a docker image into the current machine.

Useful in a case where you have an application in a docker container, and want to "unpack" it into a VM.

## Usage

**WARNING: THIS WILL DESTROY THE MACHINE THIS IS RUN ON! ALWAYS USE A CHROOT/VM/CONTAINER FOR RUNNING!**

**THIS TOOL ERASES ALL DATA ON THE MACHINE!**

Run the tool as root.

```sh
./docker_install.py image_name[:tag]
```

for example:

```sh
./docker_install.py mariadb:latest
```

## Testing

The repo contains a Dockerfile that will create a container for development purposes.
Just build & run a container from this directory. It should simulate a machine this will actually be run on.

```sh
docker built . -t docker_install:latest
docker run --rm -it docker_install mariadb:latest
```

## TODO

- [ ] ENV (on boot?)
- [ ] ENTRYPOINT (?)
