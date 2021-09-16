FROM audible:configuration

WORKDIR /application/examples/audible/services/asset-metadata

COPY . /application/examples/audible/services/asset-metadata

ENTRYPOINT [ "python3" ]

CMD [ "-m", "asset-metadata.app" ]