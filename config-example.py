BASE_URL='http://127.0.0.1:8081/artifactory/'
USER='admin'
PASSWORD='XXXXXXX'

HEADERS = {
    'content-type': 'text/plain',
}

SAFE_TAG = 'stable'

PATHS = [
    {
        #clean images older than 5w except the ones with stable or latest or main tags (regex)
        'repo': 'general-docker-local',
        'path': 'apollo9',
        'keep_time': '5w',
        'keep_filters': [
            'main',
            'latest',
            '_uploads',
            '^v\d+\.\d+\.\d+stable$',
        ],
    },
    {
        #clean images older than 12w except the _upload folder (regex)
        'repo': 'general-docker-local',
        'path': 'apollo9',
        'keep_time': '12w',
        'keep_filters': [
            '_uploads',
        ],
    },
]
