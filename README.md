# Price Feed
An implementation of a web service to get prices feed for tradable instruments

## Setup

### To start the service

```
docker-compose up --build -d
```
- You can reach the API at `localhost:8000`
- You can find the swagger docs at `localhost:8000/docs`
- You can find the prometheus metrics at `localhost:8000/metrics`
- You can reach the socket web UI at `localhost:8080`

### To run the tests
Assumes you ran the docker-compose command above
```
docker exec -t feed_service pytest
```

### To test the APIs
- Please check `price_feed.postman_collection.json.` which contains a postman collection that could be used for testing

## Design decisions

### Fast API
- Utilizes python's asyncio
- Super neat in terms of defining the routes, similar to flask
- Supports pydantic which eases the entire validation process


### Redis
- To cache instrument isins

#### Pros
- Fast retrieval and easy to query

#### Cons
- Wont be suitable once we want to add more fields to insruments, mongo would have been a better idea

### Arctic
- To store pricing data

#### Pros
- Fast time series interface to mongo, yet to be properly load tested though
- Natively supports python's pandas, which is great for in-memory transformations and eased the whole agggregation task

#### Cons
- New, very weak documentation and community support, had to check the source docs several times
- Doesn't actually support advanced querying apart from range of prices, had to do the rest in pandas

## Future Work
- Do some profiling, especially with more data coming
- Figure out a way to scale socket listeners, right now they are part of fast api's event loop
- Start using mongo for saving instrument data as well
- Consider using websockets to push latest prices
- Add charts based on vwap to the feed object (in addition to candlesticks), this requires volume data to come through though
