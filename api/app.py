from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import time
import json
import os
from .sample_data import get_sample_data  # Assuming this module exists

# Create Flask app and configure it
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Enable auto-reload of templates

# Cache for previous results (used for index.html and news.html)
previous_results = []

def sms_send(number_list, msg):
    """Placeholder for SMS sending logic"""
    print(f"SMS would be sent to {number_list} with message: {msg}")
    # Add your custom SMS sending logic here
    return True

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
                
                # Extract href link to get district, lg_code, and lg_name
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
        
        # Sort by timestamp (newest first)
        results_list.sort(key=lambda x: x['timestamp'], reverse=True)
        
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
        base_url = "https://results.elections.gov.lk/"
        
        for party in party_results:
            # Extract party name
            party_name_elem = party.select_one('.fw-bold')
            party_name = party_name_elem.text.strip() if party_name_elem else "Unknown"
            
            # Extract party abbreviation
            party_abbr_elem = party.select_one('small.text-muted')
            party_abbr = party_abbr_elem.text.strip() if party_abbr_elem else "Unknown"
            
            # Extract votes, share, and seats
            votes_elem = party.select('.fw-bold')[1] if len(party.select('.fw-bold')) > 1 else None
            votes = votes_elem.text.strip() if votes_elem else "0"
            
            share_elem = party.select('.fw-bold')[2] if len(party.select('.fw-bold')) > 2 else None
            share = share_elem.text.strip() if share_elem else "0%"
            
            seats_elem = party.select('.fw-bold')[3] if len(party.select('.fw-bold')) > 3 else None
            seats = seats_elem.text.strip() if seats_elem else "0"
            
            # Extract party symbol image
            img_elem = party.select_one('img')
            symbol_url = base_url + img_elem['src'].lstrip('/') if img_elem and img_elem.get('src') else "https://via.placeholder.com/32"
            
            results.append({
                'party_name': party_name,
                'party_abbr': party_abbr,
                'votes': votes,
                'share': share,
                'seats': seats,
                'symbol_url': symbol_url
            })
        
        # Sort by votes (descending)
        results = sorted(results, key=lambda x: int(x['votes'].replace(',', '')), reverse=True)
        
        return results
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

@app.route('/')
def index():
    global previous_results
    try:
        # Try to get live data
        recent_results = get_recent_results()
        
        if recent_results:
            most_recent = recent_results[0]
            detailed_results = get_lg_result_details(
                most_recent['district'],
                most_recent['lg_code'],
                most_recent['lg_name']
            )
            previous_results = recent_results  # Update cache
        else:
            # Fall back to sample data if live data fails
            recent_results, detailed_results, _ = get_sample_data()
            most_recent = recent_results[0]
            previous_results = recent_results
        
        # Get distinct districts for filtering
        districts = sorted(list(set([result['district'] for result in recent_results])))
            
        return render_template(
            'index.html', 
            recent_results=recent_results, 
            most_recent=most_recent, 
            detailed_results=detailed_results,
            districts=districts,
            last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            use_sample_data=False
        )
    except Exception as e:
        print(f"Error loading live data: {e}")
        # Fall back to sample data if any exception occurs
        recent_results, detailed_results, _ = get_sample_data()
        most_recent = recent_results[0]
        previous_results = recent_results
        
        # Get distinct districts for filtering
        districts = sorted(list(set([result['district'] for result in recent_results])))
        
        return render_template(
            'index.html', 
            recent_results=recent_results, 
            most_recent=most_recent, 
            detailed_results=detailed_results,
            districts=districts,
            last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            error=str(e),
            use_sample_data=True
        )

@app.route('/refresh_data')
def refresh_data():
    global previous_results
    try:
        # Get filter values and auto-SMS settings
        district_filter = request.args.get('district', None)
        auto_sms = request.args.get('auto_sms', 'false').lower() == 'true'
        number_list_str = request.args.get('number_list', '')
        
        # Try to get live data
        recent_results = get_recent_results()
        
        if recent_results:
            most_recent = recent_results[0]
            detailed_results = get_lg_result_details(
                most_recent['district'],
                most_recent['lg_code'],
                most_recent['lg_name']
            )
            use_sample_data = False
        else:
            # Fall back to sample data if live data fails
            recent_results, detailed_results, _ = get_sample_data()
            most_recent = recent_results[0]
            use_sample_data = True
        
        # Detect new results
        new_results = []
        if not use_sample_data and previous_results:
            prev_lg_names = set(r['local_government'] for r in previous_results)
            new_results = [r for r in recent_results if r['local_government'] not in prev_lg_names]
        
        # Send SMS if new results are detected and auto_sms is enabled
        if new_results and auto_sms and number_list_str:
            number_list = [num.strip() for num in number_list_str.split(',')]
            valid_numbers = [num for num in number_list if re.match(r'^\+94\d{9}$', num)]
            
            if valid_numbers:
                # Get details for the first new result
                new_result = new_results[0]
                selected_result = next((r for r in recent_results if r['local_government'] == new_result['local_government']), None)
                if selected_result:
                    detailed_results = get_lg_result_details(
                        selected_result['district'],
                        selected_result['lg_code'],
                        selected_result['lg_name']
                    ) or get_sample_data()[1]
                    
                    # Format message with top 4 parties
                    top_parties = detailed_results[:4]
                    party_shares = [f"{i+1}. {p['party_abbr']}: {p['share']}" for i, p in enumerate(top_parties)]
                    msg = f"{selected_result['local_government']}: {'; '.join(party_shares)}"
                    msg = msg[:160]  # Truncate to SMS limit
                    
                    sms_success = sms_send(valid_numbers, msg)
                    print(f"Auto-SMS sending {'successful' if sms_success else 'failed'} for new results: {new_result['local_government']}")
        
        # Update previous results cache
        previous_results = recent_results
        
        # Apply district filter if specified
        if district_filter and district_filter != 'all':
            filtered_results = [r for r in recent_results if r['district'] == district_filter]
            if filtered_results:
                recent_results = filtered_results
                if most_recent['district'] != district_filter:
                    most_recent = filtered_results[0]
                    detailed_results = get_lg_result_details(
                        most_recent['district'],
                        most_recent['lg_code'],
                        most_recent['lg_name']
                    ) if not use_sample_data else detailed_results
        
        # Get distinct districts for filtering
        districts = sorted(list(set([result['district'] for result in recent_results])))
            
        return jsonify({
            'recent_results': recent_results,
            'most_recent': most_recent,
            'detailed_results': detailed_results,
            'districts': districts,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'use_sample_data': use_sample_data,
            'new_results': [r['local_government'] for r in new_results]
        })
    except Exception as e:
        print(f"Error refreshing data: {e}")
        # Fall back to sample data if any exception occurs
        recent_results, detailed_results, _ = get_sample_data()
        most_recent = recent_results[0]
        
        # No new results for sample data
        new_results = []
        previous_results = recent_results
        
        # Apply district filter if specified
        district_filter = request.args.get('district', None)
        if district_filter and district_filter != 'all':
            filtered_results = [r for r in recent_results if r['district'] == district_filter]
            if filtered_results:
                recent_results = filtered_results
                most_recent = filtered_results[0]
        
        # Get distinct districts for filtering
        districts = sorted(list(set([result['district'] for result in recent_results])))
        
        return jsonify({
            'recent_results': recent_results,
            'most_recent': most_recent,
            'detailed_results': detailed_results,
            'districts': districts,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'use_sample_data': True,
            'new_results': new_results,
            'error': str(e)
        })

@app.route('/get_details/<district>/<lg_code>/<lg_name>')
def get_details(district, lg_code, lg_name):
    try:
        detailed_results = get_lg_result_details(district, lg_code, lg_name)
        
        if not detailed_results:
            # Fall back to sample data if live data fails
            _, detailed_results, _ = get_sample_data()
        
        return jsonify({
            'detailed_results': detailed_results,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'use_sample_data': not detailed_results
        })
    except Exception as e:
        print(f"Error fetching details: {e}")
        # Fall back to sample data if any exception occurs
        _, detailed_results, _ = get_sample_data()
        
        return jsonify({
            'detailed_results': detailed_results,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'use_sample_data': True,
            'error': str(e)
        })

@app.route('/sms_campaign')
def sms_campaign():
    try:
        # Get recent results for the dropdown
        recent_results = get_recent_results()
        
        if not recent_results:
            recent_results, _, _ = get_sample_data()
        
        return render_template(
            'sms_campaign.html',
            recent_results=recent_results,
            last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    except Exception as e:
        print(f"Error loading SMS campaign page: {e}")
        recent_results, _, _ = get_sample_data()
        
        return render_template(
            'sms_campaign.html',
            recent_results=recent_results,
            last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            error=str(e)
        )

@app.route('/send_sms_campaign', methods=['POST'])
def send_sms_campaign():
    try:
        # Get form data
        lg_name = request.form.get('lg_name')
        phone_numbers = request.form.get('phone_numbers')
        
        if not lg_name or not phone_numbers:
            return jsonify({
                'success': False,
                'message': 'Please select an election and provide phone numbers'
            })
        
        # Validate phone numbers (E.164 format: +94 followed by 9 digits)
        number_list = [num.strip() for num in phone_numbers.split(',')]
        valid_numbers = []
        for num in number_list:
            if re.match(r'^\+94\d{9}$', num):
                valid_numbers.append(num)
            else:
                print(f"Invalid phone number: {num}")
        
        if not valid_numbers:
            return jsonify({
                'success': False,
                'message': 'No valid phone numbers provided (use +94xxxxxxxxx format)'
            })
        
        # Find the selected result
        recent_results = get_recent_results() or get_sample_data()[0]
        selected_result = next((r for r in recent_results if r['lg_name'] == lg_name), None)
        
        if not selected_result:
            return jsonify({
                'success': False,
                'message': 'Selected election not found'
            })
        
        # Fetch detailed results
        detailed_results = get_lg_result_details(
            selected_result['district'],
            selected_result['lg_code'],
            selected_result['lg_name']
        ) or get_sample_data()[1]
        
        if not detailed_results:
            return jsonify({
                'success': False,
                'message': 'No results available for the selected election'
            })
        
        # Format message with top 4 parties
        top_parties = detailed_results[:4]
        party_shares = [f"{i+1}. {p['party_abbr']}: {p['share']}" for i, p in enumerate(top_parties)]
        msg = f"{selected_result['local_government']}: {'; '.join(party_shares)}"
        msg = msg[:160]  # Truncate to SMS limit
        
        # Send SMS
        success = sms_send(valid_numbers, msg)
        
        return jsonify({
            'success': success,
            'message': 'SMS campaign sent successfully' if success else 'Failed to send SMS campaign'
        })
    except Exception as e:
        print(f"Error sending SMS campaign: {e}")
        return jsonify({
            'success': False,
            'message': f'Error sending SMS campaign: {str(e)}'
        })

@app.route('/news')
def news():
    global previous_results
    try:
        # Try to get live data
        recent_results = get_recent_results()
        
        if recent_results:
            most_recent = recent_results[0]
            detailed_results = get_lg_result_details(
                most_recent['district'],
                most_recent['lg_code'],
                most_recent['lg_name']
            )
            previous_results = recent_results  # Update cache
        else:
            # Fall back to sample data if live data fails
            recent_results, detailed_results, _ = get_sample_data()
            most_recent = recent_results[0]
            previous_results = recent_results
        
        return render_template(
            'news.html',
            recent_results=recent_results,
            most_recent=most_recent,
            detailed_results=detailed_results,
            current_index=0,
            last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            use_sample_data=False
        )
    except Exception as e:
        print(f"Error loading news page: {e}")
        # Fall back to sample data
        recent_results, detailed_results, _ = get_sample_data()
        most_recent = recent_results[0]
        previous_results = recent_results
        
        return render_template(
            'news.html',
            recent_results=recent_results,
            most_recent=most_recent,
            detailed_results=detailed_results,
            current_index=0,
            last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            error=str(e),
            use_sample_data=True
        )

@app.route('/news_refresh')
def news_refresh():
    global previous_results
    try:
        # Get current index from request
        current_index = int(request.args.get('current_index', 0))
        
        # Try to get live data
        recent_results = get_recent_results()
        
        if recent_results:
            use_sample_data = False
        else:
            # Fall back to sample data if live data fails
            recent_results, _, _ = get_sample_data()
            use_sample_data = True
        
        # Detect new results
        new_results = []
        if not use_sample_data and previous_results:
            prev_lg_names = set(r['local_government'] for r in previous_results)
            new_results = [r for r in recent_results if r['local_government'] not in prev_lg_names]
        
        # Update previous results cache
        previous_results = recent_results
        
        # Ensure current_index is valid
        if current_index < 0 or current_index >= len(recent_results):
            current_index = 0
        
        # Get details for the current result
        current_result = recent_results[current_index]
        detailed_results = get_lg_result_details(
            current_result['district'],
            current_result['lg_code'],
            current_result['lg_name']
        ) if not use_sample_data else get_sample_data()[1]
        
        return jsonify({
            'recent_results': recent_results,
            'current_result': current_result,
            'detailed_results': detailed_results,
            'current_index': current_index,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'use_sample_data': use_sample_data,
            'new_results': [r['local_government'] for r in new_results]
        })
    except Exception as e:
        print(f"Error refreshing news data: {e}")
        # Fall back to sample data
        recent_results, detailed_results, _ = get_sample_data()
        current_index = max(0, min(current_index, len(recent_results) - 1))
        current_result = recent_results[current_index] if recent_results else {}
        
        return jsonify({
            'recent_results': recent_results,
            'current_result': current_result,
            'detailed_results': detailed_results,
            'current_index': current_index,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'use_sample_data': True,
            'new_results': [],
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)