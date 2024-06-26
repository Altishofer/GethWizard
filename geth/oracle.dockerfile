FROM python:3.11

COPY ./oracle/flask-requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./oracle/app.py app.py
COPY ./chaincode/chaincode.sol chaincode.sol

EXPOSE 8081
CMD ["python3", "-u", "app.py"]