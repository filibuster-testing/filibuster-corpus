FROM cinema-12:configuration

COPY ./movies.json /application/examples/cinema-12/services/movies/movies.json

WORKDIR /application/examples/cinema-12/services/movies

COPY . /application/examples/cinema-12/services/movies

ENTRYPOINT [ "python3" ]

CMD [ "-m", "movies.app" ] 