FROM python:3.10.4-slim-buster

RUN apt-get update && apt-get install -y gnupg
RUN apt-get install -y wget
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1 apt-key add -
RUN sh -c 'echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable
RUN wget -q --continue -P /tmp https://chromedriver.storage.googleapis.com/101.0.4951.41/chromedriver_linux64.zip
RUN apt-get install -yqq unzip
RUN unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin/
RUN chown root:root /usr/local/bin/chromedriver
RUN chmod +x /usr/local/bin/chromedriver
RUN apt install -y git
RUN apt-get update -y
RUN apt-get install -y libpq-dev
RUN apt-get install -y gcc
ENV PATH="/usr/local/bin:${PATH}"
COPY ./ /pipeline/
# COPY /source/ /user/home/pipeline/source/

RUN ls -la /pipeline/*

RUN python3 -m pip install --upgrade pip
RUN pip install -e /pipeline/.
RUN pip install -r /pipeline/requirements.txt
WORKDIR "/pipeline/source"
RUN python3 config.py

ENTRYPOINT ["python", "dcp_aws.py"]