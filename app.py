# Entry point for web scraping Flask app

from flask import Flask,render_template,request, send_file
import pandas as pd
from scrape_and_aggregate import scrape_and_aggregate
from rq import Queue
from worker import conn
import time
from apscheduler.schedulers.blocking import BlockingScheduler
import IPython
import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

app = Flask(__name__)
q = Queue(connection=conn)
sched = BlockingScheduler()

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
        # dataframe, inaccessible = scrape_and_aggregate(app.vars['domains'])

        def job123():
            q.enqueue(scrape_and_aggregate, [app.vars['domains']])

        # try:
        #
        #     job = q.enqueue(scrape_and_aggregate, [app.vars['domains']])
        #
        #     # job = q.enqueue_call(func=scrape_and_aggregate, args=('http://app.rawgraphs.io/',), result_ttl=5000)
        # except Exception as e:
    	#        return str(e)

        sched.add_job(job123)
        sched.start()
        while job123.is_finished == False:
            time.sleep(20)
            return redirect("https://sharecountscraper.herokuapp.com/", code=302)

        sched.shutdown()

        IPython.embed()

        # while job.is_finished == False:
        #     time.sleep(5)
        #     continue
        # IPython.embed()
        #     time.sleep(25)
        # dataframe = job.result[0]

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
