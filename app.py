from flask import Flask,render_template,request
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
        # return render_template('wait_screen.html')
        user_domains = [request.form['domain_1'], request.form['domain_2'], request.form['domain_3'], request.form['domain_4'], request.form['domain_5']]
        app.vars['domains'] = [domain for domain in user_domains if domain != '']
        app.vars['path'] = request.form['path']


        dataframe, unaccessible = scrape_and_aggregate(app.vars['domains'])
        complete_msg = ''
        if unaccessible !=[]:
            complete_msg += 'Unable to parse: %s.\n' %unaccessible

        if dataframe.shape[0] > 0:
            try:
                dataframe.to_csv(app.vars['path'], index=False)
                complete_msg += '\nFile saved to \"%s\"' % app.vars['path']
            except:
                complete_msg += 'Could not save to %s' % app.vars['path']
        else:
            complete_msg += '\nNo data to save'


        return render_template('done_screen.html', complete_msg=complete_msg)

if __name__ == "__main__":
    app.run(port=33507)
