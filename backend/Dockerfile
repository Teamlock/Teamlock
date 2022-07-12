FROM python:3.10
ARG VERSION
COPY . /app
WORKDIR /app

ENV VERSION=$VERSION
RUN apt update && apt -y install python3-venv
RUN python3 -m venv /env
RUN /env/bin/pip3 install -U pip
RUN /env/bin/pip3 install -r requirements.txt
RUN mkdir -p /var/log/teamlock
EXPOSE 8000

CMD ["/env/bin/python", "main.py"]