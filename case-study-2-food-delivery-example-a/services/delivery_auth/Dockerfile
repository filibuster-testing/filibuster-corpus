FROM case-study-2-food-delivery-example-a:configuration

WORKDIR /application/examples/filibuster-corpus/case-study-2-food-delivery-example-a/services/delivery_auth

COPY . /application/examples/filibuster-corpus/case-study-1-food-delivery-example-1/services/delivery_auth

ENTRYPOINT [ "python3" ]

CMD [ "-m", "delivery_auth.app" ] 