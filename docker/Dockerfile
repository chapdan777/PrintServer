FROM debian:13-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends  cups  cups-client  cups-filters  ghostscript  ca-certificates  iputils-ping  netcat-openbsd  avahi-daemon  avahi-utils  dbus  && rm -rf /var/lib/apt/lists/*

# Слушаем сеть, но разрешаем доступ только из вашей LAN.
RUN sed -ri 's#^Listen localhost:631#Port 631#' /etc/cups/cupsd.conf  && sed -ri '/<Location \/>/,/<\/Location>/ s#Order allow,deny#Order allow,deny\n  Allow from 192.168.2.0/24#' /etc/cups/cupsd.conf  && sed -ri 's/^Browsing No/Browsing Yes/' /etc/cups/cupsd.conf

COPY start.sh /usr/local/bin/start-printserver
RUN chmod 755 /usr/local/bin/start-printserver

CMD ["/usr/local/bin/start-printserver"]
