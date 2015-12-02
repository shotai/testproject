FROM python:latest

COPY *.py ./registersrc/
RUN pip install requests
CMD python3 ./registersrc/main.py