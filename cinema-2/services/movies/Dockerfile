FROM cinema-2:configuration

COPY ./movies.json /application/examples/cinema-2/services/movies/movies.json

WORKDIR /application/examples/cinema-2/services/movies

COPY . /application/examples/cinema-2/services/movies

ENTRYPOINT [ "python3" ]

CMD [ "-m", "movies.app" ] 