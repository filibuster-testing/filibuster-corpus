FROM mailchimp:configuration

WORKDIR /application/examples/mailchimp/services/db-primary

COPY . /application/examples/mailchimp/services/db-primary

ENTRYPOINT [ "python3" ]

CMD [ "-m", "db-primary.app" ] 