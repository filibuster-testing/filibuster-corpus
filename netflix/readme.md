# Services

### Client
port 5000  
`GET /netflix/homepage/users/<user_id>`  
return JSON object from the API gateway containing the concatenated homepage content  
or 503 ServiceUnavailable  
or 404 NotFound (if user_id not found) 
or 500 InternalServerError

### API Gateway
port 5001  
`GET /homepage/users/<user_id>`  
return JSON object containing the concatenated homepage content  
or 503 ServiceUnavailable  
or 404 NotFound (if user_id not found) 
or 500 InternalServerError

### Bookmarks
port 5003  
`GET /users/<user_id>`  
return JSON object containing in progress movies and the timecode of the location last watched  
or 404 NotFound (if user_id not found) 

### Telemetry
port 5004  
`POST /` with JSON payload containing current time  
receives JSON object to log telemetry and returns 200 OK with no body  
or 500 InternalServerError

### Trending
port 5005  
`GET /`  
return JSON object containing list of movies that are trending  

### My List
port 5006  
`GET /users/<user_id>`  
return JSON object with a list of movies that the user has on their list  
or 404 NotFound (if user_id not found) 

### User Recommendations
port 5007  
`GET /users/<user_id>`  
return JSON object containing list of movie recommendations that are specific to the user  
or 404 NotFound (if user_id not found) 

### Global Recommendations
port 5008  
`GET /`  
return JSON object containing list of movie recommendations that are for all Netflix users (called when the user-specific recommendations are unavailable)

### Ratings
port 5009  
`GET /users/<user_id>`  
return JSON object with user's ratings of movies  
or 404 NotFound (if user_id not found) 

### User Profile
port 5010  
`GET /users/<user_id>`  
return user profile information as JSON object given a user identifier  
or 404 NotFound (if user_id not found) 