FROM node:16-alpine3.12 as build-stage
WORKDIR /app
COPY ./frontend/ .
RUN npm install -g npm@7.20.6
RUN npm install
RUN npm run build
RUN cp /app/dist/favicon.ico /app/dist/static/img/favicon.ico
RUN cp /app/src/assets/img/white_bg.png /app/dist/static/img/white_bg.png
RUN cp /app/src/assets/img/TLAppLogo_Baseline.svg /app/dist/static/img/TLAppLogo_Baseline.svg
RUN cp /app/src/assets/img/TLAppLogo_Baseline.png /app/dist/static/img/TLAppLogo_Baseline.png

FROM python:3.10
ARG VERSION
COPY ./backend/ /app
WORKDIR /app
ENV VERSION=$VERSION
COPY --from=build-stage /app/dist /app/templates

RUN apt update && apt -y install python3-venv
RUN python3 -m venv /env
RUN /env/bin/pip3 install -U pip
RUN /env/bin/pip3 install -r requirements.txt
RUN mkdir -p /var/log/teamlock/
EXPOSE 8000
CMD ["/env/bin/python", "main.py"]
