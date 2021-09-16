FROM audible:configuration

WORKDIR /application/examples/audible/services/content-delivery-engine

COPY . /application/examples/audible/services/content-delivery-engine

ENTRYPOINT [ "python3" ]

CMD [ "-m", "content-delivery-engine.app" ]