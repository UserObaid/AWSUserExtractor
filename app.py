from tokenize import group
from flask import Flask, jsonify, request
from services.azureDbClient import  AzureDbClient
from services.awsClient import AWSClient
from flask import render_template
import logging
import json
from datetime import datetime

app = Flask(__name__)
#app.debug = True
#logging.basicConfig(level=logging.DEBUG)

MAXITEMS = 100

azureDbClient = AzureDbClient()
awsClient = AWSClient()

@app.route('/status', methods=['GET'])
def api_status():
    return jsonify('Flask API Running')
 
@app.route('/users', methods=['GET'])
def get_users():
    groups = []
    attach_policies = []
    users = azureDbClient.fetch_all_users()
    
    for group in awsClient.get_iam_all_groups().get('Groups'):
        groups.append(group.get('GroupName'))
        
    for policy in awsClient.get_iam_all_policies().get('Policies'):
        if(policy.get('IsAttachable')):
            attach_policies.append( {'PolicyName': policy.get('PolicyName'), 'PolicyArn': policy.get('Arn')  } )
            
            
    
    return render_template('index.html', title="Users", users = users, groups = groups, attach_policies = attach_policies)

@app.route('/users', methods=['POST'])
def insert_users():
    try :
        data = request.json
        
        username = data.get("username") 
        groups_to_add = data.get("groups")
        attach_policies_to_add = data.get("attach_policies")
        
        groups = []
        attach_policies = []
        
        awsClient.create_iam_user(username=username)


        for group in groups_to_add:
        #     #iam_group = awsClient.get_iam_group(groupName=group)
        #     #groupname = iam_group.get('Group').get('GroupName')
            awsClient.add_user_to_group(username=username, groupname=group)
            groups.append(group)
            
        for attachPolicyArn in attach_policies_to_add:
            policy = awsClient.get_iam_policy(policyArn=attachPolicyArn).get('Policy')
            awsClient.add_user_to_policy(username=username, policyArn=policy.get('Arn'))
            attach_policies.append( {'PolicyName': policy.get('PolicyName'), 'PolicyArn': policy.get('Arn')  } )
            
        azureDbClient.insert_user(username, 
                            groups=groups,
                            policies=[] , 
                            attachedPolices=attach_policies, 
                            keys=[], 
                            creationDate= datetime.today().strftime('%Y-%m-%d'), 
                            lastLogin= ''
                            )
        return json.dumps({'success':'User is creared in AWS and save to AWS.'}), 200, {'ContentType':'application/json'} 
    except Exception as e:
        return str(e), 500 

    return request.data

@app.route('/users', methods=['PUT'])
def delete_users():
    try :
        username = request.args.get('name')
        dbClient = AzureDbClient()
        awsClient = AWSClient()    
        awsClient.delete_user(username)
        dbClient.delete_user(username)        
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    except Exception as e:
        return str(e), 500 

@app.route('/sync', methods=['GET'])
def sync_users_from_aws():
    try :        
        for user in awsClient.get_iam_users():
            username = user.get('UserName')
            groups =  awsClient.get_iam_user_groups(username)
            policies = awsClient.get_iam_user_policies(username)
            attachedPolicies = awsClient.get_iam_attached_user_policies(username)
            keys = awsClient.get_iam_user_keys(username)
            
            azureDbClient.insert_user(username=username, 
                            groups=groups, 
                            policies=policies, 
                            attachedPolices=attachedPolicies,
                            keys=keys,
                            creationDate=str(user.get('CreateDate'))[:10],
                            lastLogin= str(user.get('PasswordLastUsed'))[:10])
        return json.dumps({'success':'Users are synced.'}), 200, {'ContentType':'application/json'} 
    except Exception as e:
        return str(e), 500 

    return request.data
