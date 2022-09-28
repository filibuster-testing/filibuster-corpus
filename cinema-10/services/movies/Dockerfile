FROM cinema-10:configuration

COPY ./movies.json /application/examples/cinema-10/services/movies/movies.json

WORKDIR /application/examples/cinema-10/services/movies

COPY . /application/examples/cinema-10/services/movies

ENTRYPOINT [ "python3" ]

CMD [ "-m", "movies.app" ] 