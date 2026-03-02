import logging
from pymongo import MongoClient
from config import Config

# Configure logging
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create a new database connection"""
    try:
        # Connect to MongoDB
        client = MongoClient(Config.MONGODB_URL)
        db = client.userbot_db
        return client, db, db.reply_rules, db.blacklist
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def get_reply_rules():
    """Get all reply rules from database"""
    try:
        client, db, reply_rules_collection, blacklist_collection = get_db_connection()
        rules = list(reply_rules_collection.find({}))
        client.close()
        return rules
    except Exception as e:
        logger.error(f"Failed to get reply rules: {e}")
        return []

def create_reply_rule(triggers, response, image_url=None, enabled=True):
    """Create a new reply rule with support for multiple triggers"""
    try:
        client, db, reply_rules_collection, blacklist_collection = get_db_connection()
        # Ensure triggers is always a list
        if isinstance(triggers, str):
            triggers = [triggers]
        elif triggers is None:
            triggers = []
            
        rule = {
            "triggers": triggers,
            "response": response,
            "image_url": image_url,
            "enabled": enabled
        }
        result = reply_rules_collection.insert_one(rule)
        client.close()
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Failed to create reply rule: {e}")
        return None

def update_reply_rule(rule_id, triggers=None, response=None, image_url=None, enabled=None):
    """Update an existing reply rule"""
    try:
        client, db, reply_rules_collection, blacklist_collection = get_db_connection()
        update_data = {}
        if triggers is not None:
            # Ensure triggers is always a list
            if isinstance(triggers, str):
                triggers = [triggers]
            update_data["triggers"] = triggers
        if response is not None:
            update_data["response"] = response
        if image_url is not None:
            update_data["image_url"] = image_url
        if enabled is not None:
            update_data["enabled"] = enabled
            
        result = reply_rules_collection.update_one(
            {"_id": rule_id}, 
            {"$set": update_data}
        )
        client.close()
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Failed to update reply rule: {e}")
        return False

def delete_reply_rule(rule_id):
    """Delete a reply rule"""
    try:
        client, db, reply_rules_collection, blacklist_collection = get_db_connection()
        result = reply_rules_collection.delete_one({"_id": rule_id})
        client.close()
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Failed to delete reply rule: {e}")
        return False

def get_reply_rule_by_id(rule_id):
    """Get a specific reply rule by ID"""
    try:
        client, db, reply_rules_collection, blacklist_collection = get_db_connection()
        rule = reply_rules_collection.find_one({"_id": rule_id})
        client.close()
        return rule
    except Exception as e:
        logger.error(f"Failed to get reply rule by ID: {e}")
        return None

def add_to_blacklist(user_id):
    """Add a user to the blacklist"""
    try:
        client, db, reply_rules_collection, blacklist_collection = get_db_connection()
        blacklist_entry = {
            "user_id": user_id
        }
        result = blacklist_collection.insert_one(blacklist_entry)
        client.close()
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Failed to add user to blacklist: {e}")
        return None

def is_user_blacklisted(user_id):
    """Check if a user is blacklisted"""
    try:
        client, db, reply_rules_collection, blacklist_collection = get_db_connection()
        result = blacklist_collection.find_one({"user_id": user_id})
        client.close()
        return result is not None
    except Exception as e:
        logger.error(f"Failed to check if user is blacklisted: {e}")
        return False

def remove_from_blacklist(user_id):
    """Remove a user from the blacklist"""
    try:
        client, db, reply_rules_collection, blacklist_collection = get_db_connection()
        result = blacklist_collection.delete_one({"user_id": user_id})
        client.close()
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Failed to remove user from blacklist: {e}")
        return False

def get_blacklist():
    """Get all blacklisted users"""
    try:
        client, db, reply_rules_collection, blacklist_collection = get_db_connection()
        blacklist_entries = list(blacklist_collection.find({}))
        client.close()
        # Convert ObjectId to string for JSON serialization
        for entry in blacklist_entries:
            entry["id"] = str(entry["_id"])
            del entry["_id"]
        return blacklist_entries
    except Exception as e:
        logger.error(f"Failed to get blacklist: {e}")
        return []