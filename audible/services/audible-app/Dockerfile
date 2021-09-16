FROM audible:configuration

WORKDIR /application/examples/audible/services/audible-app

COPY . /application/examples/audible/services/audible-app

ENTRYPOINT [ "python3" ]

CMD [ "-m", "audible-app.app" ]