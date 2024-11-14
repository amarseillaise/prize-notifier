from app.api import app
import init_service

def run():
    init_service.init_env_vars('api.env')
    app.run_uvicorn()

if __name__ == '__main__':
    run()