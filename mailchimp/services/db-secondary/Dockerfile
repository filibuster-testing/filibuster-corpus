FROM mailchimp:configuration

WORKDIR /application/examples/mailchimp/services/db-secondary

COPY . /application/examples/mailchimp/services/db-secondary

ENTRYPOINT [ "python3" ]

CMD [ "-m", "db-secondary.app" ] 