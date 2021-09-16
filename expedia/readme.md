# Services

### API Gateway
port 5000  
`GET /review/hotels/<hotel_id>`  
return JSON object containing list of hotel reviews  
or 503 ServiceUnavailable  
or 404 NotFound (if hotel_id not found)  
or 500 InternalServerError

### Review ML
port 5001  
`GET /hotels/<hotel_id>`  
return JSON object containing list of hotel reviews sorted by ML algorithm  
or 404 NotFound (if hotel_id not found) 

### Review Time
port 5002  
`GET /hotels/<hotel_id>`  
return JSON object containing list of hotel reviews sorted by time (called when the Review ML is unavailable)  
or 404 NotFound (if hotel_id not found)


