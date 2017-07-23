# Entry point for web scraping Flask app

from flask import Flask,render_template,request, send_file, redirect, Response
import pandas as pd
from scrape_and_aggregate import scrape_and_aggregate
from rq import Queue
from worker import conn
import time
from flask_socketio import SocketIO
# import threading
# import IPython
# import logging
# import sys
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

app = Flask(__name__)
socketio = SocketIO(app)
q = Queue(connection=conn)
app.vars = {}

@app.route('/', methods=['GET','POST'])
def main():

    # On first opening
    if request.method == 'GET':
        return render_template('domain_enter.html')

    else:
        #request was a POST. Collate the domains
        user_domains = [request.form['domain_1'], request.form['domain_2'], request.form['domain_3'], request.form['domain_4'], request.form['domain_5']]
        app.vars['domains'] = [domain for domain in user_domains if domain != '']

        # Run scraper and aggregate share counts into a dataframe. Inaccessible gives restricted domains
        task = q.enqueue(scrape_and_aggregate, app.vars['domains'])
        # task = scrape_and_aggregate(app.vars['domains'])

        # task = add_jobs(scrape_and_aggregate(app.vars['domains']))

    return redirect('/results?tid=' + task.id)

# @app.route('/load')
# def load():
#     task_id = request.args.get('tid')
#     return render_template('domain_enter.html', task_id=task_id) if task_id else redirect('/')

@app.route('/poll')
def add_poll():
    """Called by the progress page using AJAX to check whether the task is complete."""
    task_id = request.args.get('tid')
    try:
        # task = add.get_task(task_id)
        task = q.fetch_job(task_id)
    except ConnectionError:
        # Return the error message as an HTTP 500 error
        return 'Coult not connect to the task queue. Check to make sure that <strong>redis-server</strong> is running and try again.', 500

    if task.is_finished == False:
        # emit()
        time.sleep(20)
        # continue
    # ready = task.return_value is not None if task else None


    # return jsonify(ready=ready)
    return redirect('/results?tid=' + task.id)

@app.route('/results')
def add_results():
    """When poll_task indicates the task is done, the progress page redirects here using JavaScript."""
    task_id = request.args.get('tid')
    task = q.fetch_job(task_id)
    if not task:
        return redirect('/')

    if task.is_finished==False:
        return redirect('/poll?tid=' + task_id)
    # task.delete()
    # Redis can also be used to cache results
    # return render_template('results.html', value=result)

    # job = session.get(job, None)
    #
    # def emit():
    #     socketio.emit('some event', {'data': 42})
    #
    # while job.is_finished == False:
    #     emit()
    #     time.sleep(10)
    #     continue

    dataframe = task.result[0]
    inaccessible = task.result[1]

    complete_msg = ''
    if inaccessible !=[]:
        complete_msg += 'Unable to parse: %s.\n' %inaccessible

    # Test if dataframe holds any data
    if dataframe.shape[0] > 0:

        dataframe.to_csv('test.csv', index=False)
        complete_msg += '\nFile ready'
        return render_template('done_screen.html', complete_msg=complete_msg)

    else:
        complete_msg += '\nNo data to save'
        return render_template('done_screen_no_data.html', complete_msg=complete_msg)

# Define the route when download button is clicked
@app.route('/test.csv')
def files_tut():
	try:
		return send_file('test.csv', attachment_filename='test.csv')
	except Exception as e:
		return str(e)

if __name__ == "__main__":
    app.run(port=33507)
