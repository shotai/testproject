FROM python:3.4.3

COPY *.py ./testsrc/
RUN pip install requests
CMD python3 ./testsrc/test.py