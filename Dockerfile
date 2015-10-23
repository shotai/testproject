FROM python:3.4.3

COPY *.py ./registersrc/
RUN pip install requests
CMD python3 ./registersrc/test.py