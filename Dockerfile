FROM rxymx/odamusic:nodejs
RUN apt-get update && apt-get upgrade -y
RUN pip3 install -U pip
RUN pip3 install -U -r requirements.txt
CMD python3 -m oda
