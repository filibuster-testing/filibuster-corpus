FROM cinema-5:configuration

COPY ./movies.json /application/examples/cinema-5/services/movies/movies.json

WORKDIR /application/examples/cinema-5/services/movies

COPY . /application/examples/cinema-5/services/movies

ENTRYPOINT [ "python3" ]

CMD [ "-m", "movies.app" ] 