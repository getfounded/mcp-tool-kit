#!/usr/bin/env python3
"""
Track Docker Hub download statistics for MCP Tool Kit.

The Docker Hub API provides pull count information for public repositories.
"""
import requests
import json
from datetime import datetime
import os
from pathlib import Path


def get_docker_hub_stats(namespace: str, repository: str):
    """
    Get statistics from Docker Hub for a specific repository.
    
    Args:
        namespace: Docker Hub namespace (username or organization)
        repository: Repository name
        
    Returns:
        Dictionary with repository statistics
    """
    # Docker Hub API v2 endpoint
    url = f"https://hub.docker.com/v2/repositories/{namespace}/{repository}/"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        stats = {
            "timestamp": datetime.now().isoformat(),
            "namespace": namespace,
            "repository": repository,
            "pull_count": data.get("pull_count", 0),
            "star_count": data.get("star_count", 0),
            "description": data.get("description", ""),
            "last_updated": data.get("last_updated", ""),
            "is_private": data.get("is_private", False)
        }
        
        return stats
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Docker Hub stats: {e}")
        return None


def save_stats(stats: dict, output_dir: str = "docker_stats"):
    """
    Save statistics to a JSON file with timestamp.
    
    Args:
        stats: Statistics dictionary
        output_dir: Directory to save stats files
    """
    if not stats:
        return
        
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)
    
    # Create filename with date
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/docker_stats_{date_str}.json"
    
    # Save to file
    with open(filename, 'w') as f:
        json.dump(stats, f, indent=2)
        
    print(f"Stats saved to {filename}")
    
    # Also update a 'latest' file for easy access
    latest_file = f"{output_dir}/docker_stats_latest.json"
    with open(latest_file, 'w') as f:
        json.dump(stats, f, indent=2)


def display_stats(stats: dict):
    """Display statistics in a readable format."""
    if not stats:
        print("No statistics available")
        return
        
    print("\n=== Docker Hub Statistics ===")
    print(f"Repository: {stats['namespace']}/{stats['repository']}")
    print(f"Pull Count: {stats['pull_count']:,}")
    print(f"Star Count: {stats['star_count']:,}")
    print(f"Last Updated: {stats['last_updated']}")
    print(f"Timestamp: {stats['timestamp']}")
    print("===========================\n")


def track_growth(output_dir: str = "docker_stats"):
    """
    Compare current stats with previous stats to show growth.
    
    Args:
        output_dir: Directory containing stats files
    """
    latest_file = f"{output_dir}/docker_stats_latest.json"
    
    if not os.path.exists(latest_file):
        print("No previous stats found for comparison")
        return
        
    try:
        with open(latest_file, 'r') as f:
            previous_stats = json.load(f)
            
        # Get current stats
        current_stats = get_docker_hub_stats("getfounded", "mcp-tool-kit")
        
        if current_stats and previous_stats:
            pull_growth = current_stats['pull_count'] - previous_stats['pull_count']
            star_growth = current_stats['star_count'] - previous_stats['star_count']
            
            print("\n=== Growth Statistics ===")
            print(f"New Pulls: +{pull_growth}")
            print(f"New Stars: +{star_growth}")
            print(f"Since: {previous_stats['timestamp']}")
            print("========================\n")
            
    except Exception as e:
        print(f"Error tracking growth: {e}")


def main():
    """Main function to track Docker Hub statistics."""
    # Configuration
    NAMESPACE = "getfounded"  # Update this with your Docker Hub namespace
    REPOSITORY = "mcp-tool-kit"  # Update this with your repository name
    
    print(f"Fetching Docker Hub statistics for {NAMESPACE}/{REPOSITORY}...")
    
    # Get current statistics
    stats = get_docker_hub_stats(NAMESPACE, REPOSITORY)
    
    if stats:
        # Display statistics
        display_stats(stats)
        
        # Save statistics
        save_stats(stats)
        
        # Track growth
        track_growth()
    else:
        print("Failed to fetch statistics")


if __name__ == "__main__":
    main()