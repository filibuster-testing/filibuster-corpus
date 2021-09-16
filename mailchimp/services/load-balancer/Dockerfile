FROM mailchimp:configuration

WORKDIR /application/examples/mailchimp/services/load-balancer

COPY . /application/examples/mailchimp/services/load-balancer

ENTRYPOINT [ "python3" ]

CMD [ "-m", "load-balancer.app" ] 