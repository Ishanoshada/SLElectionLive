import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

def get_recent_results():
    """Fetch and parse the recent results from the elections website"""
    url = "https://results.elections.gov.lk/index.php"
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all recent result items
        recent_results = soup.select('.recent-result')
        
        results_list = []
        
        for result in recent_results:
            # Extract local government name
            lg_name_elem = result.select_one('h6 a')
            if lg_name_elem:
                lg_name = lg_name_elem.text.strip()
                
                # Extract href link to get district, lg_code and lg_name
                href = lg_name_elem.get('href', '')
                params = parse_result_url(href)
                
                # Extract timestamp
                timestamp_elem = result.select_one('p.text-muted')
                timestamp = timestamp_elem.text.strip() if timestamp_elem else "Unknown"
                
                results_list.append({
                    'local_government': lg_name,
                    'timestamp': timestamp,
                    'district': params.get('district', ''),
                    'lg_code': params.get('lg_code', ''),
                    'lg_name': params.get('lg_name', '')
                })
        
        return results_list
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

def parse_result_url(url):
    """Parse parameters from the result URL"""
    params = {}
    pattern = r'[?&]([^=]+)=([^&]+)'
    matches = re.findall(pattern, url)
    
    for match in matches:
        key, value = match
        params[key] = value
    
    return params

def get_lg_result_details(district, lg_code, lg_name):
    """Fetch and parse detailed results for a specific local government"""
    url = f"https://results.elections.gov.lk/index.php?page=lg_result&district={district}&lg_code={lg_code}&lg_name={lg_name}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all party result items
        party_results = soup.select('.party-result-item')
        
        results = []
        
        for party in party_results:
            # Extract party name
            party_name_elem = party.select_one('.fw-bold')
            party_name = party_name_elem.text.strip() if party_name_elem else "Unknown"
            
            # Extract party abbreviation
            party_abbr_elem = party.select_one('small.text-muted')
            party_abbr = party_abbr_elem.text.strip() if party_abbr_elem else "Unknown"
            
            # Extract votes, share and seats
            votes_elem = party.select('.fw-bold')[1] if len(party.select('.fw-bold')) > 1 else None
            votes = votes_elem.text.strip() if votes_elem else "0"
            
            share_elem = party.select('.fw-bold')[2] if len(party.select('.fw-bold')) > 2 else None
            share = share_elem.text.strip() if share_elem else "0%"
            
            seats_elem = party.select('.fw-bold')[3] if len(party.select('.fw-bold')) > 3 else None
            seats = seats_elem.text.strip() if seats_elem else "0"
            
            results.append({
                'party_name': party_name,
                'party_abbr': party_abbr,
                'votes': votes,
                'share': share,
                'seats': seats
            })
        
        # Sort by votes (descending)
        results = sorted(results, key=lambda x: int(x['votes'].replace(',', '')), reverse=True)
        
        return results
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

def main():
    # Get recent results
    print("Fetching recent election results...")
    recent_results = get_recent_results()
    
    if recent_results:
        # Display recent results
        print("\n===== RECENT RESULTS =====")
        for i, result in enumerate(recent_results):
            print(f"{i+1}. {result['local_government']} ({result['timestamp']})")
        
        # Get the most recent result
        most_recent = recent_results[0]
        print(f"\n===== MOST RECENT RESULT =====")
        print(f"Local Government: {most_recent['local_government']}")
        print(f"Timestamp: {most_recent['timestamp']}")
        print(f"District: {most_recent['district']}")
        
        # Get detailed results for the most recent election
        print("\nFetching detailed results for the most recent election...")
        detailed_results = get_lg_result_details(
            most_recent['district'],
            most_recent['lg_code'],
            most_recent['lg_name']
        )
        
        if detailed_results:
            print("\n===== DETAILED RESULTS =====")
            print(f"{'Party':<30} {'Votes':<10} {'Share':<10} {'Seats':<5}")
            print("-" * 55)
            
            for party in detailed_results:
                print(f"{party['party_name']:<30} {party['votes']:<10} {party['share']:<10} {party['seats']:<5}")
            
            # Determine the winner
            winner = detailed_results[0]
            print(f"\nWinner: {winner['party_name']} with {winner['votes']} votes ({winner['share']}), securing {winner['seats']} seats")
        else:
            print("No detailed results found.")
    else:
        print("No recent results found.")

# Sample usage for the most recent result from the document
def parse_sample_data():
    """Parse the sample data provided in the document"""
    # Based on the first document, the most recent result is Bentota Pradeshiya Sabha
    print("\n===== SAMPLE DATA ANALYSIS =====")
    print("Most recent result from document: Bentota Pradeshiya Sabha (07 May 2025 03:54 AM)")
    
    # Parse the provided detailed results for Bentota Pradeshiya Sabha
    party_results = [
        {'party_name': 'Jathika Jana Balawegaya', 'party_abbr': 'NPP', 'votes': '10,028', 'share': '36.12%', 'seats': '10'},
        {'party_name': 'Samagi Jana Balawegaya', 'party_abbr': 'SJB', 'votes': '6,108', 'share': '22.00%', 'seats': '5'},
        {'party_name': 'Independent Group 2', 'party_abbr': 'IND2', 'votes': '3,015', 'share': '10.86%', 'seats': '2'},
        {'party_name': 'Independent Group 1', 'party_abbr': 'IND1', 'votes': '2,484', 'share': '8.95%', 'seats': '2'},
        {'party_name': 'Sri Lanka Podujana Peramuna', 'party_abbr': 'SLPP', 'votes': '1,872', 'share': '6.74%', 'seats': '2'},
        {'party_name': 'People\'s Alliance', 'party_abbr': 'PA', 'votes': '1,817', 'share': '6.54%', 'seats': '1'},
        {'party_name': 'United National Party', 'party_abbr': 'UNP', 'votes': '1,577', 'share': '5.68%', 'seats': '1'},
        {'party_name': 'People\'s Struggle Alliance', 'party_abbr': 'PSA', 'votes': '336', 'share': '1.21%', 'seats': '0'},
        {'party_name': 'Independent Group 3', 'party_abbr': 'IND3', 'votes': '372', 'share': '1.34%', 'seats': '0'},
        {'party_name': 'Independent Group 4', 'party_abbr': 'IND4', 'votes': '156', 'share': '0.56%', 'seats': '0'}
    ]
    
    # Sort by votes (descending)
    party_results = sorted(party_results, key=lambda x: int(x['votes'].replace(',', '')), reverse=True)
    
    print("\n===== DETAILED RESULTS =====")
    print(f"{'Party':<30} {'Votes':<10} {'Share':<10} {'Seats':<5}")
    print("-" * 55)
    
    for party in party_results:
        print(f"{party['party_name']:<30} {party['votes']:<10} {party['share']:<10} {party['seats']:<5}")
    
    # Determine the winner
    winner = party_results[0]
    print(f"\nWinner: {winner['party_name']} with {winner['votes']} votes ({winner['share']}), securing {winner['seats']} seats")

if __name__ == "__main__":
    # Try to fetch live data
    try:
        main()
    except Exception as e:
        print(f"Error fetching live data: {e}")
        print("Falling back to sample data...")
        parse_sample_data()