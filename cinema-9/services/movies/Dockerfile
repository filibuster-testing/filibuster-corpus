FROM cinema-9:configuration

COPY ./movies.json /application/examples/cinema-9/services/movies/movies.json

WORKDIR /application/examples/cinema-9/services/movies

COPY . /application/examples/cinema-9/services/movies

ENTRYPOINT [ "python3" ]

CMD [ "-m", "movies.app" ]