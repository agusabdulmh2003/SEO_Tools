import requests
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin

def check_robots_txt(url, user_agent='*'):
    robots_url = urljoin(url, "/robots.txt")
    rp = RobotFileParser()
    
    try:
        rp.set_url(robots_url)
        rp.read()
    except:
        return {
            "robots_url": robots_url,
            "found": False,
            "can_fetch": False,
            "error": "Gagal membaca robots.txt"
        }

    can_fetch = rp.can_fetch(user_agent, url)
    
    return {
        "robots_url": robots_url,
        "found": True,
        "can_fetch": can_fetch,
        "error": None
    }
