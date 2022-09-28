FROM cinema-11:configuration

COPY ./movies.json /application/examples/cinema-11/services/movies/movies.json

WORKDIR /application/examples/cinema-11/services/movies

COPY . /application/examples/cinema-11/services/movies

ENTRYPOINT [ "python3" ]

CMD [ "-m", "movies.app" ] 