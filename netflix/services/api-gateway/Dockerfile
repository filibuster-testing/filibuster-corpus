FROM netflix:configuration

WORKDIR /application/examples/netflix/services/api-gateway

COPY . /application/examples/netflix/services/api-gateway

ENTRYPOINT [ "python3" ]

CMD [ "-m", "api-gateway.app" ] 