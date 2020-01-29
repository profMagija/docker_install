FROM python:3-alpine

WORKDIR /root
COPY docker_install.py /root/docker_install.py
ENTRYPOINT [ "python", "/root/docker_install.py" ]