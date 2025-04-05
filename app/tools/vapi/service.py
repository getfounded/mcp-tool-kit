#!/usr/bin/env python3
"""
Enhanced VAPI service implementation for making and managing phone calls.
"""
import os
import logging
import json
from typing import Dict, List, Any, Optional, Union, Tuple

from app.tools.base.service import ToolServiceBase


class VAPIService(ToolServiceBase):
    """Service to handle VAPI operations for making and managing phone calls"""

    def __init__(self):
        """Initialize the VAPI service"""
        super().__init__()
        self.api_key = None
        self.client = None

        # Create rate limiters
        self.create_rate_limiter("api_calls", 100, 60)  # 100 calls per minute

    def initialize(self) -> Tuple[bool, str]:
        """
        Initialize the VAPI service with required libraries and API key.

        Returns:
            Tuple of (success, message)
        """
        try:
            # Get API key from environment
            self.api_key = self.get_env_var("VAPI_API_KEY", required=True)

            # Import VAPI client
            try:
                from vapi import Client
                self.client = Client(api_key=self.api_key)
                self.logger.info("VAPI client initialized successfully")
                self.initialized = True
                return True, "VAPI service initialized successfully"
            except ImportError:
                error_msg = "VAPI library not installed. Please install with 'pip install vapi'"
                self.logger.error(error_msg)
                return False, error_msg

        except ValueError as e:
            self.logger.error(f"Failed to initialize VAPI service: {e}")
            return False, str(e)
        except Exception as e:
            self.logger.error(
                f"Unexpected error initializing VAPI service: {e}")
            return False, f"Unexpected error: {str(e)}"

    def _check_rate_limit(self, operation: str) -> None:
        """
        Check rate limit for an operation.

        Args:
            operation: Name of the operation for logging

        Raises:
            ValueError: If rate limit is exceeded
        """
        # Apply rate limiting
        wait_time = self.apply_rate_limit("api_calls", 100, 60)
        if wait_time > 0:
            self.logger.info(
                f"Rate limited {operation} operation - waited {wait_time:.2f}s")

    async def make_call(self, to: str, assistant_id: str,
                        from_number: Optional[str] = None,
                        assistant_options: Optional[Dict[str, Any]] = None,
                        server_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Make a call using VAPI.

        Args:
            to: Phone number to call (E.164 format recommended)
            assistant_id: ID of the assistant to use for the call
            from_number: Optional phone number to display as caller ID
            assistant_options: Optional dictionary of assistant configuration options
            server_url: Optional server URL for call events

        Returns:
            Dictionary with call details or error information
        """
        self._is_initialized()
        self._check_rate_limit("make_call")

        try:
            # Prepare call parameters
            params = {
                "to": to,
                "assistant_id": assistant_id
            }

            # Add optional parameters if provided
            if from_number:
                params["from"] = from_number
            if assistant_options:
                params["options"] = assistant_options
            if server_url:
                params["server_url"] = server_url

            # Make the API call
            call = self.client.calls.create(**params)
            return call
        except Exception as e:
            error_msg = f"Error making call: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}

    async def list_calls(self,
                         limit: Optional[int] = 10,
                         before: Optional[str] = None,
                         after: Optional[str] = None,
                         status: Optional[str] = None) -> Dict[str, Any]:
        """
        List calls from VAPI.

        Args:
            limit: Maximum number of calls to return
            before: Return calls created before this cursor
            after: Return calls created after this cursor
            status: Filter calls by status

        Returns:
            Dictionary with list of calls or error information
        """
        self._is_initialized()
        self._check_rate_limit("list_calls")

        try:
            # Prepare parameters
            params = {}
            if limit:
                params["limit"] = limit
            if before:
                params["before"] = before
            if after:
                params["after"] = after
            if status:
                params["status"] = status

            # Make the API call
            calls = self.client.calls.list(**params)
            return calls
        except Exception as e:
            error_msg = f"Error listing calls: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}

    async def get_call(self, call_id: str) -> Dict[str, Any]:
        """
        Get details of a specific call.

        Args:
            call_id: ID of the call to retrieve

        Returns:
            Dictionary with call details or error information
        """
        self._is_initialized()
        self._check_rate_limit("get_call")

        try:
            # Make the API call
            call = self.client.calls.get(call_id)
            return call
        except Exception as e:
            error_msg = f"Error getting call details: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}

    async def end_call(self, call_id: str) -> Dict[str, Any]:
        """
        End a call.

        Args:
            call_id: ID of the call to end

        Returns:
            Dictionary with operation result or error information
        """
        self._is_initialized()
        self._check_rate_limit("end_call")

        try:
            # Make the API call
            result = self.client.calls.end(call_id)
            return result
        except Exception as e:
            error_msg = f"Error ending call: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}

    async def get_recordings(self, call_id: str) -> Dict[str, Any]:
        """
        Get recordings for a call.

        Args:
            call_id: ID of the call to get recordings for

        Returns:
            Dictionary with recording information or error information
        """
        self._is_initialized()
        self._check_rate_limit("get_recordings")

        try:
            # Make the API call
            recordings = self.client.calls.recordings(call_id)
            return recordings
        except Exception as e:
            error_msg = f"Error getting call recordings: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}

    async def add_human(self, call_id: str,
                        phone_number: str = None,
                        transfer: bool = False) -> Dict[str, Any]:
        """
        Add a human to a call.

        Args:
            call_id: ID of the call to add the human to
            phone_number: Phone number of the human to add
            transfer: Whether to transfer the call to the human

        Returns:
            Dictionary with operation result or error information
        """
        self._is_initialized()
        self._check_rate_limit("add_human")

        try:
            # Prepare parameters
            params = {}
            if phone_number:
                params["phone_number"] = phone_number
            if transfer is not None:
                params["transfer"] = transfer

            # Make the API call
            result = self.client.calls.add_human(call_id, **params)
            return result
        except Exception as e:
            error_msg = f"Error adding human to call: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}

    async def pause_call(self, call_id: str) -> Dict[str, Any]:
        """
        Pause a call.

        Args:
            call_id: ID of the call to pause

        Returns:
            Dictionary with operation result or error information
        """
        self._is_initialized()
        self._check_rate_limit("pause_call")

        try:
            # Make the API call
            result = self.client.calls.pause(call_id)
            return result
        except Exception as e:
            error_msg = f"Error pausing call: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}

    async def resume_call(self, call_id: str) -> Dict[str, Any]:
        """
        Resume a paused call.

        Args:
            call_id: ID of the call to resume

        Returns:
            Dictionary with operation result or error information
        """
        self._is_initialized()
        self._check_rate_limit("resume_call")

        try:
            # Make the API call
            result = self.client.calls.resume(call_id)
            return result
        except Exception as e:
            error_msg = f"Error resuming call: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}

    async def send_event(self, call_id: str,
                         event_type: str,
                         data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send an event to a call.

        Args:
            call_id: ID of the call to send the event to
            event_type: Type of event to send
            data: Optional data payload for the event

        Returns:
            Dictionary with operation result or error information
        """
        self._is_initialized()
        self._check_rate_limit("send_event")

        try:
            # Prepare parameters
            params = {
                "type": event_type
            }
            if data:
                params["data"] = data

            # Make the API call
            result = self.client.calls.send_event(call_id, params)
            return result
        except Exception as e:
            error_msg = f"Error sending event to call: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}
