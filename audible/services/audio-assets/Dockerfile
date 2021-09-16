FROM audible:configuration

WORKDIR /application/examples/audible/services/audio-assets

COPY . /application/examples/audible/services/audio-assets

ENTRYPOINT [ "python3" ]

CMD [ "-m", "audio-assets.app" ]