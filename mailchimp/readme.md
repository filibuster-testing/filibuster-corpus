# Services

### Load Balancer
port 5000    
`GET /urls/<url>`    
talks to app-server.    
Gracefully handles 500 by returning the original URL back, but cannot handle 503.

### App Server    
port 5001    
`GET /urls/<url>`    
talks to Requestmapper and then reads & writes data to primary database (fallback to secondary DB) and returns JSON content containing internal URL.    
If RequestMapper is down, should throw 500 (buggy impl throws 503).    
If cannot write to DB, throw alert (buggy impl crashes)

### Requestmapper
port 5002    
`GET /urls/<url>`    
maps URLS from a pretty format to the internal format
return original URL if mapping cannot be found

### DB Primary
port 5003    
`GET /read`    
return json (reading from the DB)    

`POST /write/urls/<url>`    
return 200 if write to the DB is successful, 403 if DB is read-only (by setting the env variable 'DB_READ_ONLY' to "1")

### DB Secondary
port 5004    
`GET /read`    
return json (reading from the DB)    

`POST /write/urls/<url>`    
return 200 if write to the DB is successful, 403 if DB is read-only (by setting the env variable 'DB_READ_ONLY' to "1")