FROM alpine:3.20

# Sett korrekt locale/tidssone hvis du vil (valgfritt)
RUN apk add --no-cache bash tzdata

# Kopier kjøre-script
COPY run.sh /run.sh
RUN chmod +x /run.sh

# Standard kommando
CMD ["/run.sh"]
