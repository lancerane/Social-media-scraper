from flask import Flask,render_template,request, send_file
import pandas as pd
from scrape_and_aggregate import scrape_and_aggregate


app = Flask(__name__)

app.vars = {}

@app.route('/', methods=['GET','POST'])
def main():

    if request.method == 'GET':
        return render_template('domain_enter.html')

    else:
        #request was a POST
        user_domains = [request.form['domain_1'], request.form['domain_2'], request.form['domain_3'], request.form['domain_4'], request.form['domain_5']]
        app.vars['domains'] = [domain for domain in user_domains if domain != '']

        dataframe, unaccessible = scrape_and_aggregate(app.vars['domains'])
        complete_msg = ''
        if unaccessible !=[]:
            complete_msg += 'Unable to parse: %s.\n' %unaccessible

        if dataframe.shape[0] > 0:

            dataframe.to_csv('test.csv', index=False)
            complete_msg += '\nFile ready'

        else:
            complete_msg += '\nNo data to save'


        return render_template('done_screen.html', complete_msg=complete_msg)

@app.route('/test.csv')
def files_tut():
	try:
		return send_file('test.csv', attachment_filename='test.csv')
	except Exception as e:
		return str(e)

if __name__ == "__main__":
    app.run(port=33507)
