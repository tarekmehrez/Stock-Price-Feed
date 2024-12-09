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
