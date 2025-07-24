#!/usr/bin/env python3
"""
Track Docker Hub download statistics for MCP Tool Kit
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, Optional
import argparse


class DockerHubStats:
    """Track Docker Hub statistics for a repository."""
    
    def __init__(self, namespace: str, repository: str):
        self.namespace = namespace
        self.repository = repository
        self.api_base = "https://hub.docker.com/v2"
        
    def get_repository_info(self) -> Optional[Dict]:
        """Get repository information from Docker Hub."""
        url = f"{self.api_base}/repositories/{self.namespace}/{self.repository}/"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching repository info: {e}")
            return None
    
    def get_pull_count(self) -> Optional[int]:
        """Get the current pull count."""
        info = self.get_repository_info()
        if info:
            return info.get('pull_count', 0)
        return None
    
    def save_stats(self, stats_file: str = "docker_stats.json"):
        """Save current stats to a file."""
        pull_count = self.get_pull_count()
        if pull_count is None:
            print("Could not fetch pull count")
            return
        
        # Load existing stats
        stats = []
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
            except:
                stats = []
        
        # Add new entry
        new_entry = {
            'timestamp': datetime.now().isoformat(),
            'pull_count': pull_count,
            'repository': f"{self.namespace}/{self.repository}"
        }
        stats.append(new_entry)
        
        # Save updated stats
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"Stats saved: {pull_count} pulls as of {new_entry['timestamp']}")
        
        # Calculate daily increase if we have previous data
        if len(stats) > 1:
            prev_count = stats[-2]['pull_count']
            increase = pull_count - prev_count
            print(f"Increase since last check: {increase} pulls")
    
    def generate_report(self, stats_file: str = "docker_stats.json"):
        """Generate a report from saved stats."""
        if not os.path.exists(stats_file):
            print("No stats file found")
            return
        
        with open(stats_file, 'r') as f:
            stats = json.load(f)
        
        if not stats:
            print("No stats available")
            return
        
        print("\n=== Docker Hub Statistics Report ===")
        print(f"Repository: {stats[0]['repository']}")
        print(f"Total entries: {len(stats)}")
        
        # Current stats
        latest = stats[-1]
        print(f"\nLatest Stats ({latest['timestamp']}):")
        print(f"  Total pulls: {latest['pull_count']:,}")
        
        # Growth analysis
        if len(stats) > 1:
            first = stats[0]
            total_growth = latest['pull_count'] - first['pull_count']
            days = (datetime.fromisoformat(latest['timestamp']) - 
                   datetime.fromisoformat(first['timestamp'])).days
            
            if days > 0:
                daily_average = total_growth / days
                print(f"\nGrowth Analysis:")
                print(f"  Total growth: {total_growth:,} pulls")
                print(f"  Time period: {days} days")
                print(f"  Daily average: {daily_average:.1f} pulls/day")
        
        # Recent trend (last 7 entries)
        if len(stats) > 7:
            recent_stats = stats[-7:]
            print(f"\nRecent Trend (last {len(recent_stats)} checks):")
            for i in range(1, len(recent_stats)):
                prev = recent_stats[i-1]
                curr = recent_stats[i]
                increase = curr['pull_count'] - prev['pull_count']
                date = datetime.fromisoformat(curr['timestamp']).strftime('%Y-%m-%d %H:%M')
                print(f"  {date}: +{increase} pulls (total: {curr['pull_count']:,})")


def main():
    parser = argparse.ArgumentParser(description='Track Docker Hub statistics')
    parser.add_argument('--namespace', default='getfounded', 
                       help='Docker Hub namespace (default: getfounded)')
    parser.add_argument('--repository', default='mcp-tool-kit',
                       help='Repository name (default: mcp-tool-kit)')
    parser.add_argument('--stats-file', default='docker_stats.json',
                       help='Stats file path (default: docker_stats.json)')
    parser.add_argument('--report', action='store_true',
                       help='Generate report from existing stats')
    
    args = parser.parse_args()
    
    tracker = DockerHubStats(args.namespace, args.repository)
    
    if args.report:
        tracker.generate_report(args.stats_file)
    else:
        tracker.save_stats(args.stats_file)
        tracker.generate_report(args.stats_file)


if __name__ == '__main__':
    main()