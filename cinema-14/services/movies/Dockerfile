FROM cinema-14:configuration

COPY ./movies.json /application/examples/cinema-14/services/movies/movies.json

WORKDIR /application/examples/cinema-14/services/movies

COPY . /application/examples/cinema-14/services/movies

ENTRYPOINT [ "python3" ]

CMD [ "-m", "movies.app" ] 