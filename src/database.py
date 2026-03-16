# src/database.py snippet

def login(self, username, password):
    # Your existing query logic
    response = self.supabase.table("profiles")\
        .select("*, role:roles(role_name)")\
        .eq("username", username)\
        .eq("password", password)\
        .execute()
    
    if response.data:
        user = response.data[0]
        # FLATTEN HERE: Move the nested value to the top level
        if isinstance(user.get('role'), dict):
            user['role_name'] = user['role'].get('role_name')
        return user
    return None

def get_all_users(self):
    response = self.supabase.table("profiles")\
        .select("*, role:roles(role_name)")\
        .execute()
    
    # Map through the list and flatten every record
    flattened_data = []
    for user in response.data:
        if isinstance(user.get('role'), dict):
            user['role_name'] = user['role'].get('role_name')
        flattened_data.append(user)
    return flattened_data
