# Stage 1
FROM golang:1.23-alpine AS build

RUN apk add --no-cache git

ENV GOOS=linux
ENV GO111MODULE=on

RUN go install github.com/fogleman/primitive@latest


# Stage 2
FROM alpine:3.20

COPY --from=build /go/bin/primitive /usr/bin/primitive

RUN mkdir /var/flask
WORKDIR /var/flask
COPY . /var/flask/
RUN apk add --no-cache python3 py3-virtualenv
RUN python3 -m venv .env
RUN source .env/bin/activate
RUN .env/bin/pip install -r requirements.txt
CMD ["/var/flask/.env/bin/python", "app.py"]
EXPOSE 8000
