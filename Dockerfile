FROM node:20 as frontend-stage
WORKDIR /app
COPY ./frontend/ .
RUN export NODE_OPTIONS=--openssl-legacy-provider
RUN npm install -g npm
RUN npm install -g electron-builder
RUN npm install
RUN npm run build
RUN cp /app/dist/favicon.ico /app/dist/static/img/favicon.ico
RUN cp /app/src/assets/img/white_bg.png /app/dist/static/img/white_bg.png
RUN cp /app/src/assets/img/TLAppLogo_Baseline.svg /app/dist/static/img/TLAppLogo_Baseline.svg
RUN cp /app/src/assets/img/TLAppLogo_Baseline.png /app/dist/static/img/TLAppLogo_Baseline.png


FROM python:3.11 as python-stage
COPY ./backend/requirements.txt /requirements.txt
RUN apt update && apt -y install python3-venv
RUN python3 -m venv /env
RUN /env/bin/pip3 install -U pip
RUN /env/bin/pip3 install -r requirements.txt


FROM python:3.11-slim
ARG VERSION
ENV VERSION=$VERSION

COPY --from=python-stage /env /env
COPY --from=frontend-stage /app/dist /app/templates

COPY ./backend/ /app
WORKDIR /app

RUN mkdir -p /var/log/teamlock/
EXPOSE 8000

CMD ["/env/bin/python", "main.py"]
