def get_sample_data():
    recent_results = [
        {
            'local_government': 'Colombo Municipal Council',
            'timestamp': '2025-05-01 10:00:00',
            'district': 'Colombo',
            'lg_code': 'CMC',
            'lg_name': 'Colombo_Municipal_Council'
        },
        {
            'local_government': 'Galle Municipal Council',
            'timestamp': '2025-05-01 09:30:00',
            'district': 'Galle',
            'lg_code': 'GMC',
            'lg_name': 'Galle_Municipal_Council'
        }
    ]
    
    detailed_results = [
        {
            'party_name': 'United National Party',
            'party_abbr': 'UNP',
            'votes': '120,000',
            'share': '40%',
            'seats': '15',
            'symbol_url': 'https://via.placeholder.com/32'
        },
        {
            'party_name': 'Sri Lanka Podujana Peramuna',
            'party_abbr': 'SLPP',
            'votes': '90,000',
            'share': '30%',
            'seats': '10',
            'symbol_url': 'https://via.placeholder.com/32'
        }
    ]
    
    districts = ['Colombo', 'Galle']
    
    return recent_results, detailed_results, districts