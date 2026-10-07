FROM debian:13-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    samba \
    samba-common-bin \
    smbclient \
    cups-client \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN useradd -M -s /usr/sbin/nologin printadmin

COPY smb.conf /etc/samba/smb.conf
COPY client.conf /etc/cups/client.conf
COPY start.sh /usr/local/bin/start-samba

RUN chmod 755 /usr/local/bin/start-samba

CMD ["/usr/local/bin/start-samba"]
