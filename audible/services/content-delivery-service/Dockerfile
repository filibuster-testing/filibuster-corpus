FROM audible:configuration

WORKDIR /application/examples/audible/services/content-delivery-service

COPY . /application/examples/audible/services/content-delivery-service

ENTRYPOINT [ "python3" ]

CMD [ "-m", "content-delivery-service.app" ]