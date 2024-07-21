from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from exchange_APIs.bybit_exchange import BybitExchange
from exchange_APIs.mexc_exchange import MexcExchange
import bcrypt
import re


class DataBase:
    uri = "mongodb+srv://vkalushev:darkkong363@trading-bot.hmq5dih.mongodb.net/?retryWrites=true&w=majority"

    def __init__(self):
        self.client = MongoClient(self.uri, server_api=ServerApi('1'))

        try:
            self.client.admin.command('ping')
            print("Successfully connected to the Database")
            self.db = self.client["users"]
            self.accounts_collection = self.db["account-details"]
        except Exception as e:
            print('Couldnt connect to the database for the reason: ', e)


    def add_user(self, data):
        try:
            name = data["name"]
            email = data["email"]
            username = data["username"]
            password = data["password"].encode("utf-8")
            is_demo = data['is_account_demo']

            exchange_settings = {'bybit_api_key': "", 'bybit_secret_key': "",'bybit_button_clicked': True, 'mexc_api_key': "",'mexc_secret_key': ""}
            bot_settings = {'risk_to_reward' : '1:2', 'trading_contract': 'BTCUSDT', 'used_timeframe': '5', 'account_risk': '0.02'}
            account_settings = {'exchange_settings': exchange_settings,'bot_settings': bot_settings, 'is_account_demo': is_demo}

            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password, salt)

            self.document = {"name": name, "email": email, "username": username, "password": hashed_password, "salt": salt, "account_settings" : account_settings }
            self.accounts_collection.insert_one(self.document)

            print(f'User {self.document["name"]} was successfully added to the Cluster')
            return {'bool' : True, 'message' : 'The account was successfully created'}
        except Exception as e:
            print(e)
            return {'bool': False, 'message': 'The Registration was unsuccessful please try again later or contact support'}
        
    def attempt_to_login(self,data):
        entered_username = data['username']
        entered_password = data['password']

        find_user = self.accounts_collection.find_one({'username': entered_username})

        if find_user:
            user_password_hashed = find_user['password']
            user_salt = find_user['salt']

            hashed_entered_password = bcrypt.hashpw(entered_password.encode('utf-8'), user_salt)

            if user_password_hashed == hashed_entered_password:
                return {'bool': True, 'message': 'Login successful', 'data': find_user}

        return {'bool': False, 'message': 'Username or password is incorrect'}

    def check_register_input_validity(self, data):
        name = data['name']
        name_pattern = re.compile("^[a-zA-Z]+$")
        if not name_pattern.match(name) :
            result = {'bool': False, 'message': 'The name is invalid it should be first name only with no symbols'}
            return result
        
        email = data['email']
        email_pattern = re.compile("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        if not email_pattern.match(email):
            result = {'bool': False, 'message': 'The entered email is invalid'}
            return result

        username = data['username']
        username_pattern  = re.compile("^[a-zA-Z0-9]+$")
        if not username_pattern.match(username):
            result = {'bool': False, 'message': 'The username is invalid it only letters and digits can be used'}
            return result
        
        password = data['password']
        confirmation_password = data['confirmation-password']

        if not password == confirmation_password:
            result = {'bool': False, 'message': 'Passwords do not match'}
            return result
        
        return self.attempt_to_register_user(data)
    

    def attempt_to_register_user(self,user_data):
        find_email = self.accounts_collection.count_documents({"email": user_data["email"]})
        if(find_email):
            return {'bool': False, 'message': 'The email is already used'}
        
        find_username = self.accounts_collection.count_documents({"username": user_data["username"]})
        if(find_username):
            return {'bool': False, 'message': 'The username is already used'}

        return self.add_user(user_data)
    

    def change_email(self,user_data,new_email):
        email_pattern = re.compile("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        if email_pattern.match(new_email):
            update_data = { "$set": {"email": new_email,}}
            query_filter = {'username': user_data['username']}
            
            self.accounts_collection.update_one(query_filter,update_data)

            return {'bool': True, 'message': 'The Email address was successfully changed'}
        
        return {'bool': False, 'message': 'The entered email is invalid'}
    
    def change_password(self,user_data,new_password):
        find_user = self.accounts_collection.find_one({'username': user_data['username']})
        current_salt = find_user['salt']
        current_password = find_user['password']

        new_password_hashed = bcrypt.hashpw(new_password.encode("utf-8"), current_salt)

        if(new_password_hashed == current_password):
            return {'bool': False, 'message': 'The new password should be different from the old one'}

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), salt)

        update_data = { "$set": {"password": hashed_password,"salt": salt}}
        query_filter = {'username': user_data['username']}
            
        self.accounts_collection.update_one(query_filter,update_data)

        return {'bool': True, 'message': 'The Password was successfully changed'}
    
    #(self,api_key = 'ZNxRJIueDe1e2oIfu2',secret_key = 'syhI92xuaDhnhaLHTGWgpLSJGRMEGax4ZbfB'):
    async def change_bybit_api_keys(self,user_data,new_api_key,new_secret_key):
        bybit_exchange = BybitExchange(new_api_key,new_secret_key)
        
        result = await bybit_exchange.get_wallet_by_coin()

        if(result == ""):
            return {'bool': False, 'message': 'The entered API keys are incorrect'}
        elif result['retMsg'] == "OK": 
            exchange_settings = user_data['account_settings']['exchange_settings']

            exchange_settings['bybit_api_key'] = new_api_key
            exchange_settings['bybit_secret_key'] = new_secret_key

            user_data['account_settings']['exchange_settings'] = exchange_settings

            update_data = { "$set": {"account_settings": user_data['account_settings']}}
            query_filter = {'username': user_data['username']}
            
            self.accounts_collection.update_one(query_filter,update_data)
            
            return {'bool': True, 'message': 'The keys were seccessfully changed', 'data': user_data}
        else:
            return {'bool': False, 'message': "Unexpected response when changing Bybit's API Keys"}
        

        #(self,api_key = 'mx0vglMeocWxhcb3eA',secret_key = '2b3906e753b7409591a35431910ea005'):
    async def change_mexc_api_keys(self,user_data,new_api_key,new_secret_key):
        mexc_exchange =  MexcExchange(new_api_key,new_secret_key)
        
        result = mexc_exchange.get_account_assets()
        print(result)
        if(result == ""):
            return {'bool': False, 'message': 'The entered API keys are incorrect'}
        elif result['success']: 
            exchange_settings = user_data['account_settings']['exchange_settings']

            exchange_settings['mexc_api_key'] = new_api_key
            exchange_settings['mexc_secret_key'] = new_secret_key

            user_data['account_settings']['exchange_settings'] = exchange_settings

            update_data = { "$set": {"account_settings": user_data['account_settings']}}
            query_filter = {'username': user_data['username']}
            
            self.accounts_collection.update_one(query_filter,update_data)
            
            return {'bool': True, 'message': 'The keys were seccessfully changed', 'data': user_data}
        else:
            return {'bool': False, 'message': "Unexpected response while changing MEXC's API Keys"}
        
    def update_active_exchange(self,user_data):
            
        user_data['account_settings']['exchange_settings']['bybit_button_clicked'] = not user_data['account_settings']['exchange_settings']['bybit_button_clicked']

        update_data = { "$set": {"account_settings": user_data['account_settings'],}}
        query_filter = {'username': user_data['username']}
            
        result = self.accounts_collection.update_one(query_filter,update_data)

        if result.modified_count > 0:
            return {'bool': True, 'message': 'The used exchange was successfully changed', 'data': user_data}
        else:
            return {'bool': False, 'message': 'Unexpected response while updating the active exchange'}
        

    def update_used_timeframe(self,user_data,new_timeframe):
        user_data['account_settings']['bot_settings']['used_timeframe'] = new_timeframe
                
        update_data = { "$set": {"account_settings": user_data['account_settings'],}}
        query_filter = {'username': user_data['username']}
        result = self.accounts_collection.update_one(query_filter,update_data)
        if result.modified_count > 0:
            return {'bool': True, 'message': 'The used exchange was successfully changed', 'data': user_data}
        else:
            return {'bool': False, 'message': 'Unexpected response while updating the used timeframe'}
       
    def update_trading_contract(self,user_data,new_contract):
        user_data['account_settings']['bot_settings']['trading_contract'] = new_contract

        update_data = { "$set": {"account_settings": user_data['account_settings'],}}
        query_filter = {'username': user_data['username']}

        result = self.accounts_collection.update_one(query_filter,update_data)

        if result.modified_count > 0:
            return {'bool': True, 'message': 'The used contract was successfully changed', 'data': user_data}
        else:
            return {'bool': False, 'message': 'Unexpected response while updating the used trading contract'}
        
    def update_risk_to_reward(self,user_data,new_risk_to_reward):
        number_pattern = re.compile('^\d+:\d+$')

        if(number_pattern.match(new_risk_to_reward)):
            user_data['account_settings']['bot_settings']['risk_to_reward'] = new_risk_to_reward

            update_data = { "$set": {"account_settings": user_data['account_settings'],}}
            query_filter = {'username': user_data['username']}

            result = self.accounts_collection.update_one(query_filter,update_data)

            if result.modified_count > 0:
                return {'bool': True, 'message': 'The used exchange was successfully changed', 'data': user_data}
            else:
                return {'bool': False, 'message': 'Unexpected response while updating the used risk to reward ratio'}   
        
        else:
            return {'bool': False, 'message': 'Invalid risk to reward patten use: number(SP) : number(TP)'}
        
    
    def update_account_risk(self,user_data,new_account_risk):
        number_pattern = re.compile('^0\.0[1-9]$|^0\.1$|^0\.[0-9][1-9]$')

        if(number_pattern.match(new_account_risk)):
            user_data['account_settings']['bot_settings']['account_risk'] = new_account_risk

            update_data = { "$set": {"account_settings": user_data['account_settings'],}}
            query_filter = {'username': user_data['username']}

            result = self.accounts_collection.update_one(query_filter,update_data)

            if result.modified_count > 0:
                return {'bool': True, 'message': 'The used exchange was successfully changed', 'data': user_data}
            else:
                return {'bool': False, 'message': 'Unexpected response while updating the used account risk'}   
        
        else:
            return {'bool': False, 'message': 'Invalid entry, the number should be between 0.01 amd 0.1'}
        
    
    def clear_bybit_keys(self,user_data):
        user_data['account_settings']['exchange_settings']['bybit_api_key'] = ""
        user_data['account_settings']['exchange_settings']['bybit_secret_key'] = ""
        update_data = { "$set": {"account_settings": user_data['account_settings'],}}
        query_filter = {'username': user_data['username']}

        result = self.accounts_collection.update_one(query_filter,update_data)
        
        if result.modified_count > 0:
            return {'bool': True, 'message': 'The used exchange was successfully changed', 'data': user_data}
        else:
            return {'bool': False, 'message': 'Unexpected response while clearing Bybits Keys'}   
        
    def clear_mexc_keys(self,user_data):
        user_data['account_settings']['exchange_settings']['mexc_api_key'] = ""
        user_data['account_settings']['exchange_settings']['mexc_secret_key'] = ""
        update_data = { "$set": {"account_settings": user_data['account_settings'],}}
        query_filter = {'username': user_data['username']}

        result = self.accounts_collection.update_one(query_filter,update_data)
        
        if result.modified_count > 0:
            return {'bool': True, 'message': 'The used exchange was successfully changed', 'data': user_data}
        else:
            return {'bool': False, 'message': 'Unexpected response while clearing MEXCs Keys'}   
 
