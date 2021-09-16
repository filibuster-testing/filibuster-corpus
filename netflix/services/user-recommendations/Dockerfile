FROM netflix:configuration

WORKDIR /application/examples/netflix/services/user-recommendations

COPY . /application/examples/netflix/services/user-recommendations

ENTRYPOINT [ "python3" ]

CMD [ "-m", "user-recommendations.app" ] 