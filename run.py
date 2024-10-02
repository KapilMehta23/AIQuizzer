from app import create_app
from flask_caching import Cache



app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
    
    
from flask_caching import Cache

# Initialize Cache with Redis
cache = Cache(config={'CACHE_TYPE': 'RedisCache', 'CACHE_REDIS_URL': 'redis://localhost:6379/0'})
cache.init_app(app)
