FROM audible:configuration

WORKDIR /application/examples/audible/services/audible-download-service

COPY . /application/examples/audible/services/audible-download-service

ENTRYPOINT [ "python3" ]

CMD [ "-m", "audible-download-service.app" ]