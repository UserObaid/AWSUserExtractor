# AWSIAMExtractor

<h1> Starting locally</h1>
   
1. Install the required dependencies by executing  <b>"pip install -r requirements.txt"</b><br />
2. Start the server by executing <b>"flask --app app  run"</b><br />
    Navigate to <b>http://127.0.0.1:5000/users</b>


<h1> Starting on Docker</h1>
1. build image cmd  <b>docker build -t aws-extractor .</b>  <br />
2. start contianer cmd <b>docker run -p 5000:5000 aws-extractor</b>  <br />
3. Navigate to <b>http://localhost:5000/users</b>
