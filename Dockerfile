FROM python:latest

COPY . /registersrc
RUN pip install requests
ENTRYPOINT ["python3", "/registersrc/main.py"]
