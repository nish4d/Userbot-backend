from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from bson import ObjectId
from database import (
    get_reply_rules, 
    create_reply_rule, 
    update_reply_rule, 
    delete_reply_rule,
    get_reply_rule_by_id,
    add_to_blacklist,
    get_blacklist,
    remove_from_blacklist
)

router = APIRouter(prefix="/api")

# Pydantic models for request/response validation
from pydantic import BaseModel

class ReplyRule(BaseModel):
    id: Optional[str] = None
    triggers: Optional[List[str]] = None
    trigger: Optional[str] = None  # Kept for backward compatibility
    response: str
    image_url: Optional[str] = None
    enabled: Optional[bool] = True

class ReplyRuleCreate(BaseModel):
    triggers: Optional[List[str]] = None
    trigger: Optional[str] = None  # Kept for backward compatibility
    response: str
    image_url: Optional[str] = None
    enabled: Optional[bool] = True

class ReplyRuleUpdate(BaseModel):
    triggers: Optional[List[str]] = None
    trigger: Optional[str] = None  # Kept for backward compatibility
    response: Optional[str] = None
    image_url: Optional[str] = None
    enabled: Optional[bool] = None

class BlacklistEntry(BaseModel):
    user_id: int

class BlacklistEntryResponse(BaseModel):
    id: str
    user_id: int

class HealthResponse(BaseModel):
    status: str
    message: str

# Health check endpoint
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Userbot is running"}

# Root endpoint
@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Telegram Userbot API", "docs": "/docs"}

# Reply rules endpoints
@router.get("/rules", response_model=List[ReplyRule])
async def list_rules():
    """Get all reply rules"""
    try:
        rules = get_reply_rules()
        # Convert ObjectId to string for JSON serialization
        for rule in rules:
            rule["id"] = str(rule["_id"])
            del rule["_id"]
        return rules
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve rules: {str(e)}"
        )

@router.post("/rules", response_model=str)
async def create_rule(rule: ReplyRuleCreate):
    """Create a new reply rule"""
    try:
        # Handle both new triggers array and old trigger string
        triggers = rule.triggers
        if triggers is None and rule.trigger is not None:
            triggers = [rule.trigger]
        elif triggers is None:
            triggers = []
            
        rule_id = create_reply_rule(
            triggers=triggers,
            response=rule.response,
            image_url=rule.image_url,
            enabled=rule.enabled
        )
        if rule_id:
            return rule_id
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create rule"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create rule: {str(e)}"
        )

@router.put("/rules/{rule_id}")
async def update_rule(rule_id: str, rule: ReplyRuleUpdate):
    """Update an existing reply rule"""
    try:
        # Convert string ID to ObjectId
        object_id = ObjectId(rule_id)
        
        # Check if rule exists
        existing_rule = get_reply_rule_by_id(object_id)
        if not existing_rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule not found"
            )
            
        # Handle both new triggers array and old trigger string
        triggers = rule.triggers
        if triggers is None and rule.trigger is not None:
            triggers = [rule.trigger]
            
        success = update_reply_rule(
            rule_id=object_id,
            triggers=triggers,
            response=rule.response,
            image_url=rule.image_url,
            enabled=rule.enabled
        )
        
        if success:
            return {"message": "Rule updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update rule"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update rule: {str(e)}"
        )

@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str):
    """Delete a reply rule"""
    try:
        # Convert string ID to ObjectId
        object_id = ObjectId(rule_id)
        
        success = delete_reply_rule(object_id)
        if success:
            return {"message": "Rule deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete rule: {str(e)}"
        )

# Blacklist endpoints
@router.get("/blacklist", response_model=List[BlacklistEntryResponse])
async def get_blacklist_endpoint():
    """Get all blacklisted users"""
    try:
        blacklist = get_blacklist()
        return blacklist
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve blacklist: {str(e)}"
        )

@router.post("/blacklist")
async def add_to_blacklist_endpoint(entry: BlacklistEntry):
    """Add a user to the blacklist"""
    try:
        blacklist_id = add_to_blacklist(entry.user_id)
        if blacklist_id:
            return {"message": "User added to blacklist", "id": blacklist_id}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add user to blacklist"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add user to blacklist: {str(e)}"
        )

@router.delete("/blacklist/{user_id}")
async def remove_from_blacklist_endpoint(user_id: int):
    """Remove a user from the blacklist"""
    try:
        success = remove_from_blacklist(user_id)
        if success:
            return {"message": "User removed from blacklist"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in blacklist"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove user from blacklist: {str(e)}"
        )