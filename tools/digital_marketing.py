#!/usr/bin/env python3
import os
import json
import logging
import time
import asyncio
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta
import uuid

I'll continue with the Digital Marketing Automation Tool implementation:

```python
# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context

# External MCP reference for tool registration
external_mcp = None

def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("Marketing Automation tools MCP reference set")

class MarketingTools(str, Enum):
    """Enum of Marketing Automation tool names"""
    GET_CAMPAIGNS = "marketing_get_campaigns"
    GET_CAMPAIGN = "marketing_get_campaign"
    CREATE_CAMPAIGN = "marketing_create_campaign"
    UPDATE_CAMPAIGN = "marketing_update_campaign"
    DELETE_CAMPAIGN = "marketing_delete_campaign"
    GET_AUDIENCE = "marketing_get_audience"
    CREATE_AUDIENCE = "marketing_create_audience"
    ADD_TO_AUDIENCE = "marketing_add_to_audience"
    CREATE_EMAIL = "marketing_create_email"
    SEND_EMAIL = "marketing_send_email"
    GET_EMAIL_STATS = "marketing_get_email_stats"
    GET_CAMPAIGN_STATS = "marketing_get_campaign_stats"
    CREATE_SOCIAL_POST = "marketing_create_social_post"
    SCHEDULE_SOCIAL_POST = "marketing_schedule_social_post"
    GET_SOCIAL_STATS = "marketing_get_social_stats"

class MarketingAutomationService:
    """Service to handle Marketing Automation operations"""
    
    def __init__(self, api_key=None, provider="mailchimp"):
        """Initialize the Marketing Automation service"""
        # API credentials
        self.api_key = api_key or os.environ.get("MARKETING_API_KEY")
        self.provider = provider or os.environ.get("MARKETING_PROVIDER", "mailchimp")
        
        # Validate credentials
        if not self.api_key:
            logging.warning("Marketing Automation API key not configured. Please set MARKETING_API_KEY environment variable.")
        
        # Store mock data
        self.campaigns = {}
        self.audiences = {}
        self.emails = {}
        self.social_posts = {}
        
        # Initialize with some sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with some sample data for demo purposes"""
        # Create sample audiences
        audience1 = {
            "id": "aud_1",
            "name": "Newsletter Subscribers",
            "description": "People who subscribed to our newsletter",
            "member_count": 2450,
            "created_at": (datetime.now() - timedelta(days=180)).isoformat(),
            "fields": ["email", "first_name", "last_name", "signup_date"],
            "tags": ["newsletter", "engaged"]
        }
        
        audience2 = {
            "id": "aud_2",
            "name": "Product Users",
            "description": "Active users of our product",
            "member_count": 1870,
            "created_at": (datetime.now() - timedelta(days=150)).isoformat(),
            "fields": ["email", "first_name", "last_name", "signup_date", "last_login", "product_tier"],
            "tags": ["product", "active"]
        }
        
        # Store audiences
        self.audiences["aud_1"] = audience1
        self.audiences["aud_2"] = audience2
        
        # Create sample campaigns
        campaign1 = {
            "id": "camp_1",
            "name": "January Newsletter",
            "description": "Monthly newsletter for January",
            "type": "email",
            "status": "sent",
            "audience_id": "aud_1",
            "created_at": (datetime.now() - timedelta(days=45)).isoformat(),
            "scheduled_at": (datetime.now() - timedelta(days=40)).isoformat(),
            "sent_at": (datetime.now() - timedelta(days=40)).isoformat(),
            "email_id": "email_1",
            "stats": {
                "sent": 2400,
                "delivered": 2350,
                "opens": 980,
                "clicks": 340,
                "unsubscribes": 12,
                "open_rate": 41.7,
                "click_rate": 14.5
            }
        }
        
        campaign2 = {
            "id": "camp_2",
            "name": "Product Update Announcement",
            "description": "Announcing new features",
            "type": "email",
            "status": "scheduled",
            "audience_id": "aud_2",
            "created_at": (datetime.now() - timedelta(days=5)).isoformat(),
            "scheduled_at": (datetime.now() + timedelta(days=2)).isoformat(),
            "email_id": "email_2",
        }
        
        campaign3 = {
            "id": "camp_3",
            "name": "Summer Promotion",
            "description": "Summer discount campaign",
            "type": "multi-channel",
            "status": "draft",
            "audience_id": "aud_1",
            "created_at": (datetime.now() - timedelta(days=10)).isoformat(),
            "components": [
                {"type": "email", "id": "email_3", "status": "draft"},
                {"type": "social", "id": "social_1", "status": "draft"}
            ]
        }
        
        # Store campaigns
        self.campaigns["camp_1"] = campaign1
        self.campaigns["camp_2"] = campaign2
        self.campaigns["camp_3"] = campaign3
        
        # Create sample emails
        email1 = {
            "id": "email_1",
            "subject": "January Newsletter: Top Stories",
            "preview_text": "See what's new this month with our top stories",
            "from_email": "newsletter@example.com",
            "from_name": "Example Company",
            "body_html": "<h1>January Newsletter</h1><p>This is our monthly newsletter.</p>",
            "created_at": (datetime.now() - timedelta(days=45)).isoformat(),
            "status": "sent",
            "campaign_id": "camp_1"
        }
        
        email2 = {
            "id": "email_2",
            "subject": "New Features Announcement",
            "preview_text": "We've added some exciting new features",
            "from_email": "updates@example.com",
            "from_name": "Example Product Team",
            "body_html": "<h1>New Features!</h1><p>We're excited to announce new features.</p>",
            "created_at": (datetime.now() - timedelta(days=5)).isoformat(),
            "status": "ready",
            "campaign_id": "camp_2"
        }
        
        email3 = {
            "id": "email_3",
            "subject": "Summer Sale: 30% Off",
            "preview_text": "Get 30% off all products this summer",
            "from_email": "promotions@example.com",
            "from_name": "Example Sales",
            "body_html": "<h1>Summer Sale!</h1><p>30% off everything.</p>",
            "created_at": (datetime.now() - timedelta(days=10)).isoformat(),
            "status": "draft",
            "campaign_id": "camp_3"
        }
        
        # Store emails
        self.emails["email_1"] = email1
        self.emails["email_2"] = email2
        self.emails["email_3"] = email3
        
        # Create sample social posts
        social1 = {
            "id": "social_1",
            "platform": "twitter",
            "content": "Summer is here! Get 30% off all products with code SUMMER30",
            "image_url": "https://example.com/images/summer-sale.jpg",
            "created_at": (datetime.now() - timedelta(days=10)).isoformat(),
            "status": "draft",
            "campaign_id": "camp_3"
        }
        
        # Store social posts
        self.social_posts["social_1"] = social1
    
    async def get_campaigns(self, status=None, limit=20):
        """Get a list of marketing campaigns"""
        try:
            results = []
            count = 0
            
            for campaign_id, campaign in self.campaigns.items():
                # Filter by status if provided
                if status and campaign["status"] != status:
                    continue
                
                # Add campaign to results
                results.append(campaign)
                count += 1
                
                # Respect the limit
                if count >= limit:
                    break
            
            return {
                "campaigns": results,
                "count": len(results),
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_campaign(self, campaign_id):
        """Get a specific campaign by ID"""
        try:
            # Check if campaign exists
            if campaign_id not in self.campaigns:
                return {"error": f"Campaign not found: {campaign_id}"}
            
            # Return the campaign
            return self.campaigns[campaign_id]
        except Exception as e:
            return {"error": str(e)}
    
    async def create_campaign(self, name, description=None, type="email", audience_id=None):
        """Create a new marketing campaign"""
        try:
            # Generate a new campaign ID
            campaign_id = f"camp_{uuid.uuid4().hex[:8]}"
            
            # Create the campaign
            campaign = {
                "id": campaign_id,
                "name": name,
                "description": description or "",
                "type": type,
                "status": "draft",
                "audience_id": audience_id,
                "created_at": datetime.now().isoformat(),
                "components": []
            }
            
            # Store the campaign
            self.campaigns[campaign_id] = campaign
            
            return {
                "status": "success",
                "campaign": campaign,
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def update_campaign(self, campaign_id, updates):
        """Update an existing campaign"""
        try:
            # Check if campaign exists
            if campaign_id not in self.campaigns:
                return {"error": f"Campaign not found: {campaign_id}"}
            
            # Update the campaign
            campaign = self.campaigns[campaign_id]
            
            for key, value in updates.items():
                if key in campaign:
                    campaign[key] = value
            
            # Save the updated campaign
            self.campaigns[campaign_id] = campaign
            
            return {
                "status": "success",
                "campaign": campaign,
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def delete_campaign(self, campaign_id):
        """Delete a campaign"""
        try:
            # Check if campaign exists
            if campaign_id not in self.campaigns:
                return {"error": f"Campaign not found: {campaign_id}"}
            
            # Delete the campaign
            del self.campaigns[campaign_id]
            
            return {
                "status": "success",
                "message": f"Campaign {campaign_id} deleted",
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_audience(self, audience_id=None, limit=20):
        """Get audience information"""
        try:
            if audience_id:
                # Get a specific audience
                if audience_id not in self.audiences:
                    return {"error": f"Audience not found: {audience_id}"}
                
                return self.audiences[audience_id]
            else:
                # Get all audiences up to the limit
                results = []
                count = 0
                
                for aud_id, audience in self.audiences.items():
                    results.append(audience)
                    count += 1
                    
                    if count >= limit:
                        break
                
                return {
                    "audiences": results,
                    "count": len(results),
                    "provider": self.provider
                }
        except Exception as e:
            return {"error": str(e)}
    
    async def create_audience(self, name, description=None, fields=None):
        """Create a new audience segment"""
        try:
            # Generate a new audience ID
            audience_id = f"aud_{uuid.uuid4().hex[:8]}"
            
            # Create the audience
            audience = {
                "id": audience_id,
                "name": name,
                "description": description or "",
                "member_count": 0,
                "created_at": datetime.now().isoformat(),
                "fields": fields or ["email", "first_name", "last_name"],
                "tags": []
            }
            
            # Store the audience
            self.audiences[audience_id] = audience
            
            return {
                "status": "success",
                "audience": audience,
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def add_to_audience(self, audience_id, members):
        """Add members to an audience"""
        try:
            # Check if audience exists
            if audience_id not in self.audiences:
                return {"error": f"Audience not found: {audience_id}"}
            
            # Update audience member count
            audience = self.audiences[audience_id]
            audience["member_count"] += len(members)
            
            # Save the updated audience
            self.audiences[audience_id] = audience
            
            return {
                "status": "success",
                "added_count": len(members),
                "audience": audience,
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def create_email(self, subject, body_html, from_email=None, from_name=None, preview_text=None, campaign_id=None):
        """Create a new email for a campaign"""
        try:
            # Generate a new email ID
            email_id = f"email_{uuid.uuid4().hex[:8]}"
            
            # Create the email
            email = {
                "id": email_id,
                "subject": subject,
                "preview_text": preview_text or "",
                "from_email": from_email or "info@example.com",
                "from_name": from_name or "Example Company",
                "body_html": body_html,
                "created_at": datetime.now().isoformat(),
                "status": "draft",
                "campaign_id": campaign_id
            }
            
            # Store the email
            self.emails[email_id] = email
            
            # If part of a campaign, add to campaign components
            if campaign_id and campaign_id in self.campaigns:
                campaign = self.campaigns[campaign_id]
                if "components" not in campaign:
                    campaign["components"] = []
                
                campaign["components"].append({
                    "type": "email",
                    "id": email_id,
                    "status": "draft"
                })
                
                self.campaigns[campaign_id] = campaign
            
            return {
                "status": "success",
                "email": email,
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def send_email(self, email_id, test_emails=None):
        """Send an email to an audience or test addresses"""
        try:
            # Check if email exists
            if email_id not in self.emails:
                return {"error": f"Email not found: {email_id}"}
            
            email = self.emails[email_id]
            
            # If test emails provided, send a test
            if test_emails:
                return {
                    "status": "success",
                    "message": f"Test email sent to {len(test_emails)} addresses",
                    "email_id": email_id,
                    "provider": self.provider
                }
            
            # Check for campaign
            campaign_id = email["campaign_id"]
            if not campaign_id:
                return {"error": "Email is not associated with a campaign"}
            
            if campaign_id not in self.campaigns:
                return {"error": f"Campaign not found: {campaign_id}"}
            
            campaign = self.campaigns[campaign_id]
            
            # Check for audience
            audience_id = campaign.get("audience_id")
            if not audience_id:
                return {"error": "Campaign has no audience"}
            
            if audience_id not in self.audiences:
                return {"error": f"Audience not found: {audience_id}"}
            
            audience = self.audiences[audience_id]
            
            # Update email status
            email["status"] = "sent"
            email["sent_at"] = datetime.now().isoformat()
            self.emails[email_id] = email
            
            # Update campaign status
            campaign["status"] = "sent"
            campaign["sent_at"] = datetime.now().isoformat()
            
            # Generate email statistics
            send_count = audience["member_count"]
            delivered = int(send_count * 0.98)  # 98% delivery rate
            opens = int(delivered * 0.4)  # 40% open rate
            clicks = int(opens * 0.3)  # 30% click rate
            unsubscribes = int(delivered * 0.005)  # 0.5% unsubscribe rate
            
            campaign["stats"] = {
                "sent": send_count,
                "delivered": delivered,
                "opens": opens,
                "clicks": clicks,
                "unsubscribes": unsubscribes,
                "open_rate": round(opens / delivered * 100, 1),
                "click_rate": round(clicks / delivered * 100, 1)
            }
            
            self.campaigns[campaign_id] = campaign
            
            return {
                "status": "success",
                "message": f"Email sent to {send_count} recipients",
                "email_id": email_id,
                "campaign_id": campaign_id,
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_email_stats(self, email_id):
        """Get statistics for an email"""
        try:
            # Check if email exists
            if email_id not in self.emails:
                return {"error": f"Email not found: {email_id}"}
            
            email = self.emails[email_id]
            
            # Check if email is part of a campaign
            campaign_id = email.get("campaign_id")
            if not campaign_id or campaign_id not in self.campaigns:
                return {
                    "email_id": email_id,
                    "status": email.get("status", "draft"),
                    "stats": None,
                    "provider": self.provider
                }
            
            campaign = self.campaigns[campaign_id]
            
            # Return campaign stats for the email
            return {
                "email_id": email_id,
                "campaign_id": campaign_id,
                "status": email.get("status", "draft"),
                "stats": campaign.get("stats"),
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_campaign_stats(self, campaign_id):
        """Get performance statistics for a campaign"""
        try:
            # Check if campaign exists
            if campaign_id not in self.campaigns:
                return {"error": f"Campaign not found: {campaign_id}"}
            
            campaign = self.campaigns[campaign_id]
            
            # Get basic campaign info
            result = {
                "campaign_id": campaign_id,
                "name": campaign["name"],
                "status": campaign["status"],
                "type": campaign["type"],
                "provider": self.provider
            }
            
            # Add stats if available
            if "stats" in campaign:
                result["stats"] = campaign["stats"]
            else:
                result["stats"] = None
            
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def create_social_post(self, platform, content, image_url=None, campaign_id=None):
        """Create a social media post for a campaign"""
        try:
            # Generate a new social post ID
            post_id = f"social_{uuid.uuid4().hex[:8]}"
            
            # Create the social post
            social_post = {
                "id": post_id,
                "platform": platform,
                "content": content,
                "image_url": image_url,
                "created_at": datetime.now().isoformat(),
                "status": "draft",
                "campaign_id": campaign_id
            }
            
            # Store the social post
            self.social_posts[post_id] = social_post
            
            # If part of a campaign, add to campaign components
            if campaign_id and campaign_id in self.campaigns:
                campaign = self.campaigns[campaign_id]
                if "components" not in campaign:
                    campaign["components"] = []
                
                campaign["components"].append({
                    "type": "social",
                    "id": post_id,
                    "status": "draft"
                })
                
                self.campaigns[campaign_id] = campaign
            
            return {
                "status": "success",
                "social_post": social_post,
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def schedule_social_post(self, post_id, schedule_time):
        """Schedule a social media post"""
        try:
            # Check if post exists
            if post_id not in self.social_posts:
                return {"error": f"Social post not found: {post_id}"}
            
            post = self.social_posts[post_id]
            
            # Update post status and schedule time
            post["status"] = "scheduled"
            post["schedule_time"] = schedule_time
            
            # Update the post
            self.social_posts[post_id] = post
            
            # If part of a campaign, update component status
            campaign_id = post.get("campaign_id")
            if campaign_id and campaign_id in self.campaigns:
                campaign = self.campaigns[campaign_id]
                if "components" in campaign:
                    for component in campaign["components"]:
                        if component.get("id") == post_id:
                            component["status"] = "scheduled"
                            break
                
                self.campaigns[campaign_id] = campaign
            
            return {
                "status": "success",
                "social_post": post,
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_social_stats(self, post_id=None):
        """Get statistics for social media posts"""
        try:
            # If post_id is provided, get stats for a specific post
            if post_id:
                if post_id not in self.social_posts:
                    return {"error": f"Social post not found: {post_id}"}
                
                post = self.social_posts[post_id]
                
                # Generate mock stats if the post is published
                if post.get("status") == "published":
                    stats = {
                        "impressions": 1500,
                        "engagements": 120,
                        "clicks": 45,
                        "likes": 85,
                        "shares": 12,
                        "comments": 8,
                        "engagement_rate": 8.0
                    }
                else:
                    stats = None
                
                return {
                    "post_id": post_id,
                    "platform": post.get("platform"),
                    "status": post.get("status"),
                    "stats": stats,
                    "provider": self.provider
                }
            
            # Otherwise, get stats for all published posts
            results = []
            
            for post_id, post in self.social_posts.items():
                if post.get("status") == "published":
                    # Generate mock stats
                    stats = {
                        "impressions": 1500,
                        "engagements": 120,
                        "clicks": 45,
                        "likes": 85,
                        "shares": 12,
                        "comments": 8,
                        "engagement_rate": 8.0
                    }
                    
                    results.append({
                        "post_id": post_id,
                        "platform": post.get("platform"),
                        "stats": stats
                    })
            
            return {
                "posts": results,
                "count": len(results),
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}

# Tool function definitions

async def marketing_get_campaigns(status: str = None, limit: int = 20, ctx: Context = None) -> str:
    """Get a list of marketing campaigns
    
    Parameters:
    - status: Optional filter by campaign status (draft, scheduled, sent)
    - limit: Maximum number of campaigns to return (default: 20)
    """
    marketing_service = _get_marketing_service()
    if not marketing_service:
        return "Marketing Automation service not properly initialized. Please check environment variables."
    
    try:
        result = await marketing_service.get_campaigns(status, limit)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def marketing_get_campaign(campaign_id: str, ctx: Context = None) -> str:
    """Get detailed information about a specific campaign
    
    Parameters:
    - campaign_id: ID of the campaign to retrieve
    """
    marketing_service = _get_marketing_service()
    if not marketing_service:
        return "Marketing Automation service not properly initialized. Please check environment variables."
    
    try:
        result = await marketing_service.get_campaign(campaign_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def marketing_create_campaign(name: str, description: str = None, 
                                  type: str = "email", audience_id: str = None, 
                                  ctx: Context = None) -> str:
    """Create a new marketing campaign
    
    Parameters:
    - name: Name of the campaign
    - description: Optional detailed description of the campaign
    - type: Campaign type (email, social, multi-channel)
    - audience_id: Optional ID of the audience for this campaign
    """
    marketing_service = _get_marketing_service()
    if not marketing_service:
        return "Marketing Automation service not properly initialized. Please check environment variables."
    
    try:
        result = await marketing_service.create_campaign(name, description, type, audience_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def marketing_update_campaign(campaign_id: str, updates: Dict[str, Any], ctx: Context = None) -> str:
    """Update an existing campaign
    
    Parameters:
    - campaign_id: ID of the campaign to update
    - updates: Dictionary of fields to update (name, description, status, audience_id)
    """
    marketing_service = _get_marketing_service()
    if not marketing_service:
        return "Marketing Automation service not properly initialized. Please check environment variables."
    
    try:
        result = await marketing_service.update_campaign(campaign_id, updates)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def marketing_delete_campaign(campaign_id: str, ctx: Context = None) -> str:
    """Delete a marketing campaign
    
    Parameters:
    - campaign_id: ID of the campaign to delete
    """
    marketing_service = _get_marketing_service()
    if not marketing_service:
        return "Marketing Automation service not properly initialized. Please check environment variables."
    
    try:
        result = await marketing_service.delete_campaign(campaign_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def marketing_get_audience(audience_id: str = None, limit: int = 20, ctx: Context = None) -> str:
    """Get audience information
    
    Parameters:
    - audience_id: Optional ID of a specific audience to retrieve
    - limit: Maximum number of audiences to return if no ID specified (default: 20)
    """
    marketing_service = _get_marketing_service()
    if not marketing_service:
        return "Marketing Automation service not properly initialized. Please check environment variables."
    
    try:
        result = await marketing_service.get_audience(audience_id, limit)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def marketing_create_audience(name: str, description: str = None, 
                                  fields: List[str] = None, ctx: Context = None) -> str:
    """Create a new audience segment
    
    Parameters:
    - name: Name of the audience
    - description: Optional detailed description of the audience
    - fields: Optional list of fields to collect for this audience
    """
    marketing_service = _get_marketing_service()
    if not marketing_service:
        return "Marketing Automation service not properly initialized. Please check environment variables."
    
    try:
        result = await marketing_service.create_audience(name, description, fields)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def marketing_add_to_audience(audience_id: str, members: List[Dict[str, Any]], ctx: Context = None) -> str:
    """Add members to an audience
    
    Parameters:
    - audience_id: ID of the audience to add members to
    - members: List of member objects with at least an email field
    """
    marketing_service = _get_marketing_service()
    if not marketing_service:
        return "Marketing Automation service not properly initialized. Please check environment variables."
    
    try:
        result = await marketing_service.add_to_audience(audience_id, members)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def marketing_create_email(subject: str, body_html: str, from_email: str = None, 
                               from_name: str = None, preview_text: str = None, 
                               campaign_id: str = None, ctx: Context = None) -> str:
    """Create a new email for a campaign
    
    Parameters:
    - subject: Email subject line
    - body_html: HTML content of the email
    - from_email: Optional sender email address
    - from_name: Optional sender name
    - preview_text: Optional preview text shown in email clients
    - campaign_id: Optional ID of the campaign this email belongs to
    """
    marketing_service = _get_marketing_service()
    if not marketing_service:
        return "Marketing Automation service not properly initialized. Please check environment variables."
    
    try:
        result = await marketing_service.create_email(
            subject, body_html, from_email, from_name, preview_text, campaign_id
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def marketing_send_email(email_id: str, test_emails: List[str] = None, ctx: Context = None) -> str:
    """Send an email to an audience or test addresses
    
    Parameters:
    - email_id: ID of the email to send
    - test"""