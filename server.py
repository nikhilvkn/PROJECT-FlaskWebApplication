from flask import Flask, render_template, request, jsonify
from inception import Server, Service, InceptionTools
from pathlib import Path

import pandas as pd
import datetime
import json



app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/<string:url_path>')
def path(url_path):
    return render_template(url_path)


@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
	if request.method == 'POST':
		data = request.form.to_dict()
		return json.dumps(data)


@app.route('/service_lessthan', methods=['POST', 'GET'])
def service_lessthan():
	if request.method == 'POST':
		datacenter = request.form['Datacenter']
		environment = request.form['Environment']
		d_data = inception.Service(datacenter)
		full_data = d_data.all_service()
		return render_template('service_lessthan.html', data=full_data)


@app.route('/server-check', methods=['POST','GET'])
def server_check():
   if request.method == 'POST':
      datacenter = request.form['Datacenter']
      environment = request.form['Environment']
      inception_service = request.form['Service']

   if inception_service:
      service_data = inception_service.split(',')
      inception_request = Service(datacenter, environment)
      all_service = inception_request.specific_service()
      for content in service_data:
         if content not in all_service:
            return render_template('server-exception.html',data = f'''FileNotFound Exception: Service {content} not found in {environment} environment.
   Please re-check service name''')
            sys.exit()
      inception_request = Server(datacenter, environment, service_data)
      return render_template('service-check-result.html', data = inception_request.specific_service())

   if datacenter:
      if bool(datacenter) ^ bool(environment):
         inception_request = Server(datacenter)
         return render_template('service-check-result.html', data = inception_request.all_server())
      else:
         inception_request = Server(datacenter, environment)
         return render_template('service-check-result.html', data = inception_request.specific_server())

home = str(Path.home())
today = datetime.date.today()
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_cifile():
   if request.method == 'POST':
      f = request.files['file']
      dataframe = pd.read_excel(f)
      dataframe = dataframe[['Approval for','Short description']]
      dataframe = dataframe.drop_duplicates()
      dataframe["Status"] = pd.Series([])
      dataframe.to_excel(f'{home}/Downloads/ci-approval{today}.xlsx', index = False)
      return render_template('render-out.html')

      
@app.route('/cruploader', methods = ['GET', 'POST'])
def upload_crfile():
   if request.method == 'POST':
      f = request.files['file']
      df = pd.read_excel(f)
      df = df[ df['State'] == 'Ready for Implementation' ]
      df.sort_values(by=['Scheduled start date'], inplace=True)
      df = df[['Change request','Subject','Scheduled start date','Scheduled end date']]
      df = df.drop_duplicates()
      df["Status"] = pd.Series([])
      df.to_excel(f'{home}/Downloads/changetask{today}.xlsx', index = False)
      return render_template('render-out.html')


@app.route('/service-check', methods = ['POST', 'GET'])
def service():
   if request.method == 'POST':
      datacenter = request.form['Datacenter']
      environment = request.form['Environment']
   if datacenter:
      if bool(datacenter) ^ bool(environment):
         inception_request = Service(datacenter)
         return render_template('service-check-result.html', data = inception_request.all_service())
      else:
         inception_request = Service(datacenter, environment)
         return render_template('service-check-result.html', data = inception_request.specific_service())

