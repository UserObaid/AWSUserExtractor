from socket import socket
import boto3


MAXITEMS = 100
ITEMSPERPAGE = 100

class AWSClient:
    
    def __init__(self):
        self.client =  boto3.client(
            'iam',
            aws_access_key_id= '',  # ADD YOUR OWN AWS API KEY
            aws_secret_access_key= ''  # ADD YOUR OWN AWS SECRET KEY
        )
       #session = boto3.Session(profile_name='default')
       #self.client = session.client('iam')
        
    #this function is not being used anymore
    def get_iam_users(self):
        """
        Return a list of IAM user accounts. Get the users in batches.
        """
        users = []
        more = True
        marker = ''

        while more is True:
            u = {}
            if marker == '':
                u = self.client.list_users(MaxItems=MAXITEMS)
            else:
                u = self.client.list_users(Marker=marker, MaxItems=MAXITEMS)

            more = u.get('IsTruncated')
            marker = u.get('Marker')
            users.extend(u['Users'])

        return users

    #this function is not being used anymore
    def get_iam_user_list(self):
        user_list = list()
        iam_all_users = self.client.list_users(MaxItems=200)
        for user in iam_all_users['Users']:
            user_list.append(user['UserName'])
        # list of policy for each user
        for key in user_list['Users']:
            List_of_Groups = self.client.list_groups_for_user(UserName=key['UserName'])
            for key in List_of_Groups['Groups']:
                print
                key['GroupName']
        return user_list
    
    def get_iam_user_groups(self, user):
        """
        Return a list of groups of which the IAM user is a member. Get the groups
        in batches.
        """
        groups = []
        more = True
        marker = ''

        while more is True:
            g = {}
            if marker == '':
                g = self.client.list_groups_for_user(UserName=user, MaxItems=MAXITEMS)
            else:
                g = self.client.list_groups_for_user(UserName=user, Marker=marker, MaxItems=MAXITEMS)

            more = g.get('IsTruncated')
            marker = g.get('Marker')
            groups.extend([f['GroupName'] for f in g['Groups']])

        return groups

    def get_iam_user_policies(self, user):
        policies = []
        paginator = self.client.get_paginator('list_user_policies')
        response_iterator = paginator.paginate(
            UserName = user,
            PaginationConfig={
                'MaxItems': MAXITEMS,
                'PageSize': ITEMSPERPAGE,
            })        
        for response in response_iterator:
            policies.extend(response["PolicyNames"]);
        
        return policies;
   
    def get_iam_attached_user_policies(self, user):
        policies = []
        paginator = self.client.get_paginator('list_attached_user_policies')
        response_iterator = paginator.paginate(
            UserName = user,
            PaginationConfig={
                'MaxItems': MAXITEMS,
                'PageSize': ITEMSPERPAGE,
            })        
        for response in response_iterator:
            policies.extend(response["AttachedPolicies"]);
        
        return policies

    def get_iam_key_last_used(self, key):
        """
        Return the last used date of the specified key.
        """
        last_used = self.client.get_access_key_last_used(AccessKeyId=key)
        alu = last_used.get('AccessKeyLastUsed')

        if alu.get('LastUsedDate') is None:
            return 'Never'
        else:
            return str(alu.get('LastUsedDate'))

    def get_iam_user_keys(self, user):
        """
        Return a list of access keys which belong to the IAM user. Get the keys in
        batches.
        """
        keys = []
        more = True
        marker = ''

        while more is True:
            k = {}
            if marker == '':
                k = self.client.list_access_keys(UserName=user, MaxItems=MAXITEMS)
            else:
                k = self.client.list_access_keys(UserName=user, Marker=marker, MaxItems=MAXITEMS)

            more = k.get('IsTruncated')
            marker = k.get('Marker')
            key_list = [l['AccessKeyId'] for l in k['AccessKeyMetadata']]
            for key in key_list:
                last_used = self.get_iam_key_last_used( key)
                keys.append((key, last_used[:10]))

        return keys

    def get_iam_all_groups(self):
        return self.client.list_groups()
        
    def get_iam_all_policies(self):
        return self.client.list_policies()
    
    def get_iam_group(self, groupName) :
        return self.client.get_group(GroupName=groupName);
    
    def get_iam_policy(self, policyArn) :
        return self.client.get_policy(PolicyArn=policyArn);
    
    def create_iam_user(self, username):
        self.client.create_user(UserName=username)
        
    def add_user_to_group(self, username, groupname):
        self.client.add_user_to_group(GroupName=groupname, UserName=username)
   
    def add_user_to_policy(self, username, policyArn):
       self.client.attach_user_policy( UserName=username,PolicyArn=policyArn)
       
    def delete_user(self, username):
        
        groups = self.get_iam_user_groups(username)
        for group in groups:
            self.client.remove_user_from_group( GroupName=group ,UserName=username)            
        
        keys = self.get_iam_user_keys(username)
        for key in keys:
            print(key)
            self.client.delete_access_key(UserName=username,AccessKeyId=key[0])
        
        attachedPolicies = self.get_iam_attached_user_policies(username)
        for policy in attachedPolicies:
            self.client.detach_user_policy( UserName=username, PolicyArn=policy.get('PolicyArn'))
            
        self.client.delete_user(UserName=username)
    