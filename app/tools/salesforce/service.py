#!/usr/bin/env python3
"""
Salesforce API Service for MCP toolkit.
"""
import os
import json
import logging
import time
import requests
from typing import Dict, List, Any, Optional, Union

from app.tools.base.service import ToolServiceBase
from app.tools.utils.auth import create_auth_handler, BasicAuth


class SalesforceService(ToolServiceBase):
    """Service for Salesforce API operations"""

    def __init__(self):
        """Initialize the Salesforce service"""
        super().__init__()
        self.client = None
        self.auth_handler = None

    def initialize(self) -> bool:
        """
        Initialize the service with credentials from environment variables.

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Try to import required libraries
            try:
                from simple_salesforce import Salesforce
                self.sf_module = Salesforce
            except ImportError:
                self.logger.error(
                    "simple_salesforce module not installed. Please install it with 'pip install simple-salesforce'")
                return False

            # Get credentials from environment
            self.username = self.get_env_var("SF_USERNAME")
            self.password = self.get_env_var("SF_PASSWORD")
            self.security_token = self.get_env_var("SF_SECURITY_TOKEN")
            self.consumer_key = self.get_env_var("SF_CONSUMER_KEY")
            self.consumer_secret = self.get_env_var("SF_CONSUMER_SECRET")
            self.domain = self.get_env_var("SF_DOMAIN", default="login")

            # Create rate limiter
            calls_per_day = int(self.get_env_var(
                "SF_RATE_LIMIT_CALLS", default="1000"))
            self.create_rate_limiter(
                "salesforce_api", calls_per_day, 86400)  # 24 hours

            # Create auth handler
            self.auth_handler = create_auth_handler(
                service_name="salesforce",
                auth_type="basic",
                username=self.username,
                password=self.password,
                username_env="SF_USERNAME",
                password_env="SF_PASSWORD"
            )

            self.initialized = True
            return True
        except Exception as e:
            self.logger.error(
                f"Failed to initialize Salesforce service: {str(e)}")
            return False

    def _ensure_connected(self):
        """Ensure we have an active Salesforce connection"""
        self._is_initialized()

        if self.client is None:
            # Apply rate limiting
            self.apply_rate_limit("salesforce_api", wait=True)

            try:
                # Connect to Salesforce
                # OAuth2 connection if consumer key and secret are provided
                if self.consumer_key and self.consumer_secret:
                    self.client = self.sf_module(
                        username=self.username,
                        password=self.password,
                        security_token=self.security_token,
                        consumer_key=self.consumer_key,
                        consumer_secret=self.consumer_secret,
                        domain=self.domain
                    )
                # Password-based auth
                else:
                    self.client = self.sf_module(
                        username=self.username,
                        password=self.password,
                        security_token=self.security_token,
                        domain=self.domain
                    )
                self.logger.info(f"Connected to Salesforce as {self.username}")
            except Exception as e:
                self.logger.error(f"Failed to connect to Salesforce: {str(e)}")
                raise

    async def query(self, soql_query: str) -> Dict[str, Any]:
        """Execute a SOQL query against Salesforce"""
        try:
            self._ensure_connected()
            # Apply rate limiting
            self.apply_rate_limit("salesforce_api", wait=True)
            result = self.client.query(soql_query)
            return self._format_query_result(result)
        except Exception as e:
            self.logger.error(f"Salesforce query error: {str(e)}")
            return {"error": str(e)}

    async def create(self, object_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record in Salesforce"""
        try:
            self._ensure_connected()
            # Apply rate limiting
            self.apply_rate_limit("salesforce_api", wait=True)

            # Get the Salesforce object (Account, Contact, etc.)
            sf_object = getattr(self.client, object_name)

            # Create the record
            result = sf_object.create(data)

            return {
                "success": result["success"],
                "id": result["id"] if result["success"] else None,
                "errors": result.get("errors", [])
            }
        except Exception as e:
            self.logger.error(f"Salesforce create error: {str(e)}")
            return {"error": str(e)}

    async def update(self, object_name: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing record in Salesforce"""
        try:
            self._ensure_connected()
            # Apply rate limiting
            self.apply_rate_limit("salesforce_api", wait=True)

            # Get the Salesforce object (Account, Contact, etc.)
            sf_object = getattr(self.client, object_name)

            # Update the record
            result = sf_object.update(record_id, data)

            return {
                "success": result == 204,  # HTTP 204 means success with no content
                "id": record_id,
                "status_code": result
            }
        except Exception as e:
            self.logger.error(f"Salesforce update error: {str(e)}")
            return {"error": str(e)}

    async def delete(self, object_name: str, record_id: str) -> Dict[str, Any]:
        """Delete a record from Salesforce"""
        try:
            self._ensure_connected()
            # Apply rate limiting
            self.apply_rate_limit("salesforce_api", wait=True)

            # Get the Salesforce object (Account, Contact, etc.)
            sf_object = getattr(self.client, object_name)

            # Delete the record
            result = sf_object.delete(record_id)

            return {
                "success": result == 204,  # HTTP 204 means success with no content
                "id": record_id,
                "status_code": result
            }
        except Exception as e:
            self.logger.error(f"Salesforce delete error: {str(e)}")
            return {"error": str(e)}

    async def describe(self, object_name: str = None) -> Dict[str, Any]:
        """Get metadata about a Salesforce object or all objects"""
        try:
            self._ensure_connected()
            # Apply rate limiting
            self.apply_rate_limit("salesforce_api", wait=True)

            if object_name:
                # Get metadata for a specific object
                sf_object = getattr(self.client, object_name)
                result = sf_object.describe()
                return self._format_describe_result(result)
            else:
                # Get global metadata for all objects
                result = self.client.describe()
                return self._format_describe_result(result)
        except Exception as e:
            self.logger.error(f"Salesforce describe error: {str(e)}")
            return {"error": str(e)}

    async def get_object(self, object_name: str, record_id: str) -> Dict[str, Any]:
        """Get a specific record from Salesforce"""
        try:
            self._ensure_connected()
            # Apply rate limiting
            self.apply_rate_limit("salesforce_api", wait=True)

            # Get the Salesforce object (Account, Contact, etc.)
            sf_object = getattr(self.client, object_name)

            # Get the record
            result = sf_object.get(record_id)

            # Remove null values for better readability
            cleaned_result = {k: v for k, v in result.items() if v is not None}

            return cleaned_result
        except Exception as e:
            self.logger.error(f"Salesforce get_object error: {str(e)}")
            return {"error": str(e)}

    async def search(self, sosl_query: str) -> Dict[str, Any]:
        """Execute a SOSL search against Salesforce"""
        try:
            self._ensure_connected()
            # Apply rate limiting
            self.apply_rate_limit("salesforce_api", wait=True)

            result = self.client.search(sosl_query)
            return self._format_search_result(result)
        except Exception as e:
            self.logger.error(f"Salesforce search error: {str(e)}")
            return {"error": str(e)}

    async def list_objects(self) -> Dict[str, Any]:
        """List available Salesforce objects"""
        try:
            self._ensure_connected()
            # Apply rate limiting
            self.apply_rate_limit("salesforce_api", wait=True)

            # Get global metadata
            global_describe = self.client.describe()

            # Extract object info
            objects = []
            for obj in global_describe["sobjects"]:
                objects.append({
                    "name": obj["name"],
                    "label": obj["label"],
                    "custom": obj["custom"],
                    "createable": obj["createable"],
                    "updateable": obj["updateable"],
                    "deletable": obj["deletable"],
                    "queryable": obj["queryable"]
                })

            return {
                "objects": objects,
                "count": len(objects)
            }
        except Exception as e:
            self.logger.error(f"Salesforce list_objects error: {str(e)}")
            return {"error": str(e)}

    def _format_query_result(self, result):
        """Format query results for better readability"""
        if not result:
            return {"records": [], "totalSize": 0, "done": True}

        # For normal query results
        if hasattr(result, "get"):
            return {
                "records": result.get("records", []),
                "totalSize": result.get("totalSize", 0),
                "done": result.get("done", True),
                "nextRecordsUrl": result.get("nextRecordsUrl", None)
            }

        # Fallback for other result types
        return result

    def _format_describe_result(self, result):
        """Format describe results to be more readable"""
        # If it's a list of objects (global describe)
        if isinstance(result, dict) and "sobjects" in result:
            simplified = []
            for obj in result["sobjects"]:
                simplified.append({
                    "name": obj.get("name"),
                    "label": obj.get("label"),
                    "custom": obj.get("custom", False),
                    "keyPrefix": obj.get("keyPrefix")
                })
            return {"objects": simplified}

        # If it's a single object describe
        if isinstance(result, dict) and "fields" in result:
            fields = []
            for field in result["fields"]:
                fields.append({
                    "name": field.get("name"),
                    "label": field.get("label"),
                    "type": field.get("type"),
                    "custom": field.get("custom", False),
                    "nillable": field.get("nillable", True),
                    "picklistValues": field.get("picklistValues", [])
                })

            return {
                "name": result.get("name"),
                "label": result.get("label"),
                "custom": result.get("custom", False),
                "fields": fields
            }

        # Fallback
        return result

    def _format_search_result(self, result):
        """Format search results for better readability"""
        if isinstance(result, list):
            return {"searchRecords": result, "totalSize": len(result)}
        return result
