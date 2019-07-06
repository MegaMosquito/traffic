FROM arm32v6/python:3-alpine
WORKDIR /usr/src/app

# Install useful development tools
RUN apk --no-cache --update add jq vim

# Install tshark, the CLI-based analyzer from the Wireshark distribution
# (For details see https://www.wireshark.org/docs/man-pages/tshark.html)
# also: https://hackertarget.com/tshark-tutorial-and-filter-examples/
RUN apk --no-cache --update add tshark

# Install couchdb interface
RUN pip install couchdb

# Copy over the source
COPY *.py ./

# Start the daemon
CMD python3 sniffer.py

