FROM python:3.8
WORKDIR /ihome
COPY 爱家租房 .
RUN pip install -y requirements.txt
EXPOSE 5000
ENTRYPOINT ["entrypoint.sh"]

