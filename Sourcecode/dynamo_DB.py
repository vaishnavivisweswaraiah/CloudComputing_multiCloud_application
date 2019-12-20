import boto3
from boto3.dynamodb.conditions import Key
import time,datetime
import decimal
import json


ACCESS_KEY=""
SECRET_KEY=""

def create_table(table_name):
    """
    create a table and return the table object
    :param table_name: name of the table
    :return: dynamo db table instance
    """
    dynamodb_resource = boto3.client('dynamodb', aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,region_name="us-east-1")
    # to do
    # check the sample code https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.01.html
    # create the greetings table with attributes (gid, date, content).(1) create a table "greetings" that has the three fields "gid", "date", and "content".
    # The method "create_table" is (2) Make sure you can read/insert/delete greetings. (3) Post your code snippets for (1) and (2) here.
    try:
        table=dynamodb_resource.create_table(TableName=table_name,
                           KeySchema=[
                               {
                                   'AttributeName':'gid',
                                   'KeyType':'HASH'
                                }
                               ],
                           AttributeDefinitions=[
                               {
                                   'AttributeName': 'gid',
                                   'AttributeType': 'N'
                               }
                           ],
                           ProvisionedThroughput={
                               'ReadCapacityUnits': 10,
                               'WriteCapacityUnits': 10
                           }
                           )
        table_status=dynamodb_resource.describe_table(TableName=table_name)['Table']['TableStatus']
        #print("Table status:", table_status)
        while True:
            if table_status=='CREATING':
                time.sleep(10)
                table_status=dynamodb_resource.describe_table(TableName=table_name)['Table']['TableStatus']
            else:
                break
    except dynamodb_resource.exceptions.ResourceInUseException as e:
        #print('Table already exists')
        pass

    # return the table object
    return get_table(table_name)



def get_table(table_name):
    """
    return the table object, when the table is already created
    :param table_name: name of the table
    :return: dynamo db table instance
    """
    dynamodb_resource = boto3.resource('dynamodb', aws_access_key_id=ACCESS_KEY,
                                       aws_secret_access_key=SECRET_KEY, region_name="us-east-1")
    table = None
    try:
        table = dynamodb_resource.Table(table_name)
    except:
        print("unable to fetch table", table_name)
    finally:
        return table


def read_table_item(table, pk_name, pk_value):
    """
    table is the object returned by get_table
    Return item read by primary key.
    """
    response = table.get_item(Key={pk_name: pk_value})

    return response

def read_table(table,filter_name,filter_value,pe,ean):
    #response meta data is returned which is read by primary key
    pe = pe
    ean = ean
    #read all values from dynamodb"
    #since date is a reserved keyword ,using projection expressions such that Expression attribute names doesnot throw reserve keyword exception
    if filter_name=="None":
        response = table.scan( \
            ProjectionExpression=pe, \
            ExpressionAttributeNames=ean
        )
    else:
        fe = Key(filter_name).eq(filter_value)

        # read values from dynamodb with filter
        response = table.scan( FilterExpression=fe,
                               ProjectionExpression=pe, \
                               ExpressionAttributeNames=ean
    )

    return response



def add_item(table, col_dict):
    """
    Add one item (row) to table. col_dict is a dictionary {col_name: value}.
    """
    response = table.put_item(Item=col_dict)

    return response



def update_item(table, col_dict,table_key):
    """
    Add one item (row) to table. col_dict is a dictionary {col_name: value}.
    """
    for items in col_dict:
        if items==table_key:
            pk_name=table_key
            pk_value=col_dict[items]

    response = table.update_item(Key={pk_name:pk_value},\
                                 UpdateExpression="set #date = :new_date, content= :content",
                                 ExpressionAttributeValues={':new_date':col_dict['date'],
                                                            ':content':col_dict['content']} , \
                                 ExpressionAttributeNames={'#date':'date'},\
                                 ReturnValues='UPDATED_NEW')

    return response


def delete_item(table, pk_name, pk_value):
    """
    Delete an item (row) in table from its primary key.
    """
    response = table.delete_item(Key={pk_name: pk_value})

    return response

#DecimalEncoder For test purpose
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

if __name__=="__main__":
        tableobj=create_table('Greetings')

        #date=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        greetingmsg=[{'gid':1,'date':time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),'content':'greeting 1'},\
                     {'gid': 2, 'date': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), 'content': 'greeting 2'},\
                     {'gid': 3, 'date': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), 'content': 'greeting 3'}, \
                     {'gid': 4, 'date': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), 'content': 'greeting 4'}]

        #adding msgs
        for msgs in greetingmsg:
            write_response=add_item(tableobj,msgs)
            print(write_response['ResponseMetadata']['HTTPStatusCode'])

        #read messages with keys
        read_id=[1,3,4]
        for gid in read_id:
            read_reponse=read_table_item(tableobj,'gid',gid)
            print(read_reponse['Item'])

        #delete messages using key
        delete_id=[1,4]

        for gid in delete_id:
            delete_response=delete_item(tableobj,'gid',gid)
            print(delete_response)

        read_reponse = read_table_item(tableobj, 'gid', 3)
        print("rad_table_item",read_reponse['Item'])

        #update the values in dynamo db"
        update={'gid': 3, 'date': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), 'content': 'greeting upated'}
        update_item(tableobj,update,'gid')

        pe = " gid,#date,content"
        ean = {"#date": "date"}
        #Read all contents from a table
        read_table_response=read_table(table=tableobj,filter_name="None",filter_value="None",pe=pe,ean=ean)

        #print content post decimal encoder
        print("Read Entire Table Values")
        for i in read_table_response['Items']:
            print(json.dumps(i,cls=DecimalEncoder))
        # Read  content  from a table with required filter value
        read_table_response = read_table(table=tableobj,filter_name="gid",filter_value=2,pe=pe,ean=ean)

        # print content post decimal encoder
        for i in read_table_response['Items']:
            print(json.dumps(i, cls=DecimalEncoder))




