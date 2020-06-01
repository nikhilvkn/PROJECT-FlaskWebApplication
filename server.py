from flask import Flask, render_template, request, jsonify
from inception import Server, Service, InceptionTools
from pathlib import Path
import pandas as pd
import datetime
import json

app = Flask(__name__)

# Home Page route
@app.route('/')
def hello_world():
    return render_template('index.html')

# Route that can route any strings
@app.route('/<string:url_path>')
def path(url_path):
    return render_template(url_path)

# What will happen if I want to check what happens
# when I submit the code. To know that.for testing
# prupose, created this route
@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
	if request.method == 'POST':
		data = request.form.to_dict()
		return json.dumps(data)


# There is a service to check Inception microservices
# which are running in less than 3 servers/instaces
# in aws. This route logic helps perform that
@app.route('/service_lessthan', methods=['POST', 'GET'])
def service_lessthan():
	if request.method == 'POST':
		datacenter = request.form['Datacenter']
		environment = request.form['Environment']
		d_data = inception.Service(datacenter)
		full_data = d_data.all_service()
		return render_template('service_lessthan.html', data=full_data)


# This route handles 3 different operations which I have
# given to a user, 
# 1) To list all servers in an inception datacenter [AWS]
# 2) To list all servers specific to an environment in a dc
# 3) To list servers based on the microservices given
# There is option to add more than 1 microservices seperat-
# ed by comma
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


# Defining the home directory and data time object
# This route helps run the logic to create an excel
# sheet with specific colums
# Used Pandas module to manipulate the data frames
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


# Everyday, I need to gather and populate the change
# request from service now. Used Pandas and modified
# the dataframe to give the result as an excel sheet
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


# Based on the option added by the user, we can choose
# 2 option. Either, we can list out all services in a 
# datacenter in AWS, or can list out all servcers which
# are specific to a particular environment like production
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

