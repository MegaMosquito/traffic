#
# A convenience Makefile with commonly used commands for the traffic monitor
#
# A traffic monitor daemon container that uses tshark, the CLI component
# of WireShark to monit traffic that is either tapped or mirrored in transit.
# (Note that this requires specialized hardware and careful placement of
# that hardware within your network. For more details on this, see:
#   https://github.com/MegaMosquito/trafficmon/blob/master//README.md
#
# Note that this monitor may not be completely reliable. My naivete about
# tshark may mean that I have not configured my streaming query very well.
# Also, in my own network setup I am using a managed swutch to mirror all
# ingress and egress traffic to the monitor host. I think it is likely that
# traffic bursts at least could overwhelm the monitor, resulting in it
# missing some of the traffic. This is a potential problem in any setup.
#
# Having said all of that, this is still pretty cool, I think. I discovered
# many surprising things about various kinds of network-capablie devices in
# my home network because of this tool. I never would have had visibility
# into these activities without this tool.
#
# Written by Glen Darling (mosquito@darlingevil.com), July 2019.
#


# Some bits from https://github.com/MegaMosquito/netstuff/blob/master/Makefile
LOCAL_DEFAULT_ROUTE     := $(shell sh -c "ip route | grep default")
LOCAL_ROUTER_ADDRESS    := $(word 3, $(LOCAL_DEFAULT_ROUTE))
LOCAL_DEFAULT_INTERFACE := $(word 5, $(LOCAL_DEFAULT_ROUTE))
LOCAL_IP_ADDRESS        := $(word 7, $(LOCAL_DEFAULT_ROUTE))
LOCAL_MAC_ADDRESS       := $(shell sh -c "ip link show | sed 'N;s/\n/ /' | grep $(LOCAL_DEFAULT_INTERFACE) | sed 's/.*ether //;s/ .*//;'")
LOCAL_SUBNET_CIDR       := $(shell sh -c "echo $(wordlist 1, 3, $(subst ., ,$(LOCAL_IP_ADDRESS))) | sed 's/ /./g;s|.*|&.0/24|'")


# Configure all of these "MY_" variables for your personal situation

MY_SUBNET_CIDR            := $(LOCAL_SUBNET_CIDR)

MY_COUCHDB_ADDRESS        := $(LOCAL_IP_ADDRESS)
MY_COUCHDB_PORT           := 5984
MY_COUCHDB_USER           := 'admin'
MY_COUCHDB_PASSWORD       := 'p4ssw0rd'
MY_COUCHDB_TRAFFIC_DB     := 'traffic'
MY_COUCHDB_TIME_FORMAT    := '%Y-%m-%d %H:%M:%S'

# The host interface that `tshark` wil bind onto to receive mirrored traffic
MY_MIRROR_INTERFACE       := 'eth0'


# Running `make` with no target builds and runs traffic as a restarting daemon
all: build run

# Build the container and tag it, "netmon".
build:
	docker build -t traffic .

# Running `make dev` will setup a working environment, just the way I like it.
# On entry to the container's bash shell, run `cd /outside/src` to work here.
dev: build
	-docker rm -f traffic 2> /dev/null || :
	docker run -it --net=host \
	    --name traffic \
	    -e MY_SUBNET_CIDR=$(MY_SUBNET_CIDR) \
	    -e MY_COUCHDB_ADDRESS=$(MY_COUCHDB_ADDRESS) \
	    -e MY_COUCHDB_PORT=$(MY_COUCHDB_PORT) \
	    -e MY_COUCHDB_USER=$(MY_COUCHDB_USER) \
	    -e MY_COUCHDB_PASSWORD=$(MY_COUCHDB_PASSWORD) \
	    -e MY_COUCHDB_TRAFFIC_DB=$(MY_COUCHDB_TRAFFIC_DB) \
	    -e MY_COUCHDB_TIME_FORMAT=$(MY_COUCHDB_TIME_FORMAT) \
	    -e MY_MIRROR_INTERFACE=$(MY_MIRROR_INTERFACE) \
	    --volume `pwd`:/outside traffic /bin/sh

# Run the container as a daemon (build not forecd here, sp must build it first)
run:
	-docker rm -f traffic 2>/dev/null || :
	docker run -d --net=host \
	    --name traffic --restart unless-stopped \
	    -e MY_SUBNET_CIDR=$(MY_SUBNET_CIDR) \
	    -e MY_COUCHDB_ADDRESS=$(MY_COUCHDB_ADDRESS) \
	    -e MY_COUCHDB_PORT=$(MY_COUCHDB_PORT) \
	    -e MY_COUCHDB_USER=$(MY_COUCHDB_USER) \
	    -e MY_COUCHDB_PASSWORD=$(MY_COUCHDB_PASSWORD) \
	    -e MY_COUCHDB_TRAFFIC_DB=$(MY_COUCHDB_TRAFFIC_DB) \
	    -e MY_COUCHDB_TIME_FORMAT=$(MY_COUCHDB_TIME_FORMAT) \
	    -e MY_MIRROR_INTERFACE=$(MY_MIRROR_INTERFACE) \
	    traffic

# Enter the context of the daemon container
exec:
	docker exec -it traffic /bin/sh

# Stop the daemon container
stop:
	-docker rm -f traffic 2>/dev/null || :

# Stop the daemon container, and cleanup
clean: stop
	-docker rmi traffic 2>/dev/null || :

# Declare all non-file-system targets as .PHONY
.PHONY: all build dev run exec stop clean

