FROM python:latest

COPY . /registersrc
RUN pip install requests
CMD python3 /registersrc/main.py