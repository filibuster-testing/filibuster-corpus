FROM cinema-9:configuration

WORKDIR /application/examples/cinema-9/services/showtimes

COPY . /application/examples/cinema-9/services/showtimes

ENTRYPOINT [ "python3" ]

CMD [ "-m", "showtimes.app" ]