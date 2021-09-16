FROM mailchimp:configuration

WORKDIR /application/examples/mailchimp/services/requestmapper

COPY . /application/examples/mailchimp/services/requestmapper

ENTRYPOINT [ "python3" ]

CMD [ "-m", "requestmapper.app" ] 