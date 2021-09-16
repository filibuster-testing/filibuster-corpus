FROM cinema-1:configuration

COPY ./movies.json /application/examples/cinema-1/services/movies/movies.json

WORKDIR /application/examples/cinema-1/services/movies

COPY . /application/examples/cinema-1/services/movies

ENTRYPOINT [ "python3" ]

CMD [ "-m", "movies.app" ] 