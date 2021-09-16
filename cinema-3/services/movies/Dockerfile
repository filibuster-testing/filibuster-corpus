FROM cinema-3:configuration

COPY ./movies.json /application/examples/cinema-3/services/movies/movies.json

WORKDIR /application/examples/cinema-3/services/movies

COPY . /application/examples/cinema-3/services/movies

ENTRYPOINT [ "python3" ]

CMD [ "-m", "movies.app" ] 