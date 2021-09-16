FROM mailchimp:configuration

WORKDIR /application/examples/mailchimp/services/app-server

COPY . /application/examples/mailchimp/services/app-server

ENTRYPOINT [ "python3" ]

CMD [ "-m", "app-server.app" ] 