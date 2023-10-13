import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"

def run_web_server():
    port = int(os.environ.get('PORT', 5000))
    try:
        app.run(host='0.0.0.0', port=port)
        print("Web server started successfully!")
    except Exception as e:
        print(f"Error starting web server: {e}")

if __name__ == '__main__':
    run_web_server()  # 별도의 스레드 사용 없이 웹서버 시작