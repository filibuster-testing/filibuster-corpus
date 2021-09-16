FROM cinema-4:configuration

COPY ./movies.json /application/examples/cinema-4/services/movies/movies.json

WORKDIR /application/examples/cinema-4/services/movies

COPY . /application/examples/cinema-4/services/movies

ENTRYPOINT [ "python3" ]

CMD [ "-m", "movies.app" ] 