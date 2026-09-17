import json
import os
from flask import Flask, Response, jsonify, render_template, request, stream_with_context
from dotenv import load_dotenv
from agent import run_agent

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8192

@app.get('/')
def index():
    return render_template('index.html')

@app.get('/api/health')
def health():
    load_dotenv(override=True)
    return jsonify(status='ok', key_configured=bool(os.getenv('OPENAI_API_KEY')), model=os.getenv('OPENAI_MODEL','gpt-5.4-mini'))

@app.post('/api/run')
def run():
    body = request.get_json(silent=True) or {}
    goal = body.get('goal')
    if not isinstance(goal,str) or not 10 <= len(goal.strip()) <= 2000:
        return jsonify(error='Enter a travel goal between 10 and 2,000 characters.'),400
    @stream_with_context
    def events():
        try:
            for event in run_agent(goal):
                yield json.dumps(event,ensure_ascii=False)+'\n'
        except Exception as exc:
            # Never send API exception bodies or credentials to the browser.
            code = getattr(exc,'status_code',None)
            message = {401:'API authentication failed. Check the key in .env.',429:'API quota or rate limit reached. Check API billing and retry.',404:'Model unavailable. Check OPENAI_MODEL in .env.'}.get(code,'API request failed or timed out. Check network and API configuration, then retry.')
            yield json.dumps(dict(type='error',message=message))+'\n'
    return Response(events(),mimetype='application/x-ndjson', headers={'Cache-Control':'no-cache','X-Accel-Buffering':'no'})

if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5000,debug=False,threaded=True)
