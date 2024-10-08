FROM python:3.8
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install \
    gcc nano \
    ffmpeg libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 \
    postgresql postgresql-contrib -y

RUN pip install --upgrade pip
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
