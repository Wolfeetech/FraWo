import time
import os
import urllib.request
import json
import re
from odoo_rpc_client import connect, OdooSession

OPENCLAW_URL = "http://127.0.0.1:5555/api/chat"

def xmlrpc_call(session, model, method, args=None, kwargs=None):
    return session.models.execute_kw(
        session.db, session.uid, session.secret,
        model, method, args or [], kwargs or {}
    )

def main():
    print("Starte Odoo-OpenClaw Bridge...")
    
    # Connect to Odoo (uses env vars)
    session = connect(default_user="agent@frawo-tech.de", prompt_for_username=False)
    
    # Find agent user and partner
    users = xmlrpc_call(session, 'res.users', 'search_read', [[('login', '=', 'agent@frawo-tech.de')]], {'fields': ['partner_id']})
    if not users:
        print("Agent user not found!")
        return
    agent_partner_id = users[0]['partner_id'][0]
    
    print(f"Agent Partner ID: {agent_partner_id}")
    
    # Find channels where agent is member
    model_name = 'discuss.channel'
    try:
        channels = xmlrpc_call(session, model_name, 'search', [[('channel_partner_ids', 'in', [agent_partner_id])]])
    except Exception as e:
        print(f"discuss.channel failed, trying mail.channel. Error: {e}")
        model_name = 'mail.channel'
        channels = xmlrpc_call(session, model_name, 'search', [[('channel_partner_ids', 'in', [agent_partner_id])]])
        
    print(f"Listening on channels: {channels} using model {model_name}")
    
    # Get last message ID
    last_id = 0
    if channels:
        messages = xmlrpc_call(session, 'mail.message', 'search_read', [[('model', '=', model_name), ('res_id', 'in', channels)]], {'fields': ['id'], 'order': 'id desc', 'limit': 1})
        if messages:
            last_id = messages[0]['id']
            
    print(f"Starting poll. Last message ID: {last_id}")
    
    # Set to track messages posted by the bridge to avoid infinite loops
    posted_message_ids = set()
    
    while True:
        try:
            # Refresh channels to find new direct messages
            channels = xmlrpc_call(session, model_name, 'search', [[('channel_partner_ids', 'in', [agent_partner_id])]])
            
            if not channels:
                time.sleep(5)
                continue
                
            # Poll for new messages
            messages = xmlrpc_call(session, 'mail.message', 'search_read', [
                [('model', '=', model_name), ('res_id', 'in', channels), ('id', '>', last_id)]
            ], {'fields': ['id', 'body', 'author_id', 'res_id'], 'order': 'id asc'})
            
            for msg in messages:
                last_id = msg['id']
                
                # Skip if we posted this message ourselves
                if last_id in posted_message_ids:
                    print(f"Skipping self-posted message {last_id}")
                    continue
                    
                author_id = msg['author_id'][0] if msg['author_id'] else None
                
                # Skip messages from the agent itself (if it ever logs in as agent)
                if author_id == agent_partner_id:
                    continue
                    
                body = msg['body'] or ""
                clean_body = re.sub(r'<[^>]+>', '', body).strip()
                
                if not clean_body:
                    continue
                    
                print(f"New message from author {author_id} in channel {msg['res_id']}: {clean_body}")
                
                # Forward to OpenClaw
                try:
                    payload = {"message": clean_body}
                    req = urllib.request.Request(
                        OPENCLAW_URL,
                        data=json.dumps(payload).encode(),
                        headers={"Content-Type": "application/json"}
                    )
                    with urllib.request.urlopen(req, timeout=360) as response:
                        resp_data = json.loads(response.read().decode())
                        ai_response = resp_data.get('response', '')
                        
                    print(f"OpenClaw reply: {ai_response}")
                    
                    # Post reply back to Odoo
                    reply_id = xmlrpc_call(session, model_name, 'message_post', [msg['res_id']], {'body': ai_response})
                    if reply_id:
                        posted_message_ids.add(reply_id)
                        print(f"Reply posted to Odoo. Ignored ID: {reply_id}")
                    
                except Exception as e:
                    print(f"Error calling OpenClaw or posting reply: {e}")
                    
            time.sleep(5)
            
        except Exception as e:
            print(f"Error in poll loop: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
