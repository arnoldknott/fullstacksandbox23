FROM alpine:3.18.5
WORKDIR /var/lib/postgresql/data
RUN pwd
RUN addgroup -S postgres && adduser -S postgres -G postgres
RUN echo -e '#!/bin/sh\nls -la /var/lib/postgresql/data' > /entrypoint.sh && chmod +x /entrypoint.sh
RUN chown -R postgres:postgres /var/lib/postgresql/data
ENTRYPOINT ["/entrypoint.sh"]
# CMD [ "/bin/ls", "-la" ]
