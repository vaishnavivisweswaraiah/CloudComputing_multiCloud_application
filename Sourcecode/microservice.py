from flask import Flask,redirect,url_for,request
from werkzeug.exceptions import NotFound
from flask import make_response, request
import json
import os
import time
import decimal
import dynamo_DB # the code you finished for Part I


app = Flask(__name__)

# code here to open the DynamoDB table. If the table is not there, create it
dynamo_table=dynamo_DB.create_table('Greetings')

#variables related to specific Greetings table in dynamo DB where pe=ProjectionExpression and ean=ExpressionAttributeNames
pe = " gid,#date,content"
ean = {"#date": "date"}
pk_name='gid'


def root_dir():
    """ Returns root director for this project """
    return os.path.dirname(os.path.realpath(__file__ + '/..'))

#helper class to convert dynamoDB items to json
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def nice_json(arg):
    response = make_response(json.dumps(arg,sort_keys = True, indent=4,cls=DecimalEncoder))
    response.headers['Content-type'] = "application/json"
    return response


@app.route("/", methods=['GET'])
def hello():
    return nice_json({
        "uri": "/",
        "subresource_uris": {
            "greetings": "/greetings",
            "add_greeting": "/addgreeting/<id>/<date>/<content>",
        }
    })

@app.route("/greetings", methods=['GET'])
def greetings():
    # return all greetings records in json format
    # to do
    greetings_data = dynamo_DB.read_table(table=dynamo_table,filter_name="None",filter_value="None",pe=pe,ean=ean)

    return nice_json(greetings_data['Items'])


@app.route("/addgreeting/<gid>/<date>/<content>", methods=['POST', 'PUT'])
def add_greeting(gid,date,content):
    # add a greeting to DynamoDB and return success message if HttpStatus code has success response 200.
    # to do
    #greeting = request.get_json()
    #print(greeting)
    #Parameteres of greeting table.
    greeting = {'gid': int(gid), 'date': str(date), 'content': str(content)}
    #greetings_data=dynamo_DB.read_table(table=dynamo_table,filter_name=pk_name,filter_value=greeting["gid"],pe=pe,ean=ean)
    greetings_data = dynamo_DB.read_table(table=dynamo_table, filter_name=pk_name, filter_value=gid, pe=pe, ean=ean)
    #Update an Item if item already exist.
    if len(greetings_data['Items'])!=0:
        response=dynamo_DB.update_item(table=dynamo_table,col_dict=greeting,table_key=pk_name)
    #Add item if item didnot exist in table
    else:
        response=dynamo_DB.add_item(table=dynamo_table, col_dict=greeting)

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return nice_json("sucessfully added/updated greeting values to DynamoDB")


if __name__ == "__main__":
    #Run on below port on local host
    app.run(port=5001, debug=True)

    #Run on this port on EC2 instance
    #app.run(port=80, host="0.0.0.0", debug=False)