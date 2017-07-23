# Entry point for web scraping Flask app

from flask import Flask,render_template,request, send_file, redirect
import pandas as pd
from scrape_and_aggregate import scrape_and_aggregate
from rq import Queue
from worker import conn
import time
# import logging
# import sys
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

app = Flask(__name__)
q = Queue(connection=conn)

@app.route('/', methods=['GET','POST'])
def main():

    # On first opening
    if request.method == 'GET':
        return render_template('domain_enter.html')

    else:
        #request was a POST. Collate the domains
        user_domains = [request.form['domain_1'], request.form['domain_2'], request.form['domain_3'], request.form['domain_4'], request.form['domain_5']]
        domains = [domain for domain in user_domains if domain != '']


        # Run scraper and aggregate share counts into a dataframe. Enqueue the function for a background process
        task = q.enqueue(scrape_and_aggregate, domains, timeout=1800)

        # Sleep to limit redirects
        time.sleep(10)

    # Redirect to avoid server timeout
    return redirect('/results?tid=' + task.id)


@app.route('/poll')
def add_poll():

    # Called by the results page using AJAX to check whether the task is complete
    task_id = request.args.get('tid')
    try:
        task = q.fetch_job(task_id)

    except ConnectionError:
        # Return the error message as an HTTP 500 error
        return 'Coult not connect to the task queue. Please try again', 500

    # If not done, sleep and redirect to avoid timeout
    if task.is_finished == False:
        time.sleep(20)

    return redirect('/results?tid=' + task.id)


@app.route('/results')
def add_results():

    # Get the job
    task_id = request.args.get('tid')
    task = q.fetch_job(task_id)

    # If none, redirect home
    if not task:
        return redirect('/')

    # If not done, sleep and redirect to avoid timeout
    if task.is_finished==False:
        time.sleep(20)
        return redirect('/poll?tid=' + task_id)

    # When the job's finished:
    dataframe = task.result[0]
    inaccessible = task.result[1]
    task.delete()

    complete_msg = ''

    # Test if dataframe holds any data
    if dataframe.shape[0] > 0:

        dataframe.to_csv('share_counts.csv', index=False)
        complete_msg += '\nFile ready.'
        if inaccessible !=[]:
            complete_msg += '\nUnable to parse: %s' %inaccessible
        return render_template('done_screen.html', complete_msg=complete_msg)

    else:
        complete_msg += '\nNo data to save.'
        if inaccessible !=[]:
            complete_msg += '\nUnable to parse: %s' %inaccessible
        return render_template('done_screen_no_data.html', complete_msg=complete_msg)

# When download button is clicked
@app.route('/share_counts.csv')
def files_tut():
	try:
		return send_file('share_counts.csv', attachment_filename='share_counts.csv')
	except Exception as e:
		return str(e)

if __name__ == "__main__":
    app.run(port=33507)
