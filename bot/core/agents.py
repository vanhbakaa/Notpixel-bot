import re

import ua_generator
from ua_generator.options import Options
from ua_generator.data.version import VersionRange

def generate_random_user_agent(device_type='android', browser_type='chrome'):
    chrome_version_range = VersionRange(min_version=117, max_version=130)
    options = Options(version_ranges={'chrome': chrome_version_range})
    ua = ua_generator.generate(platform=device_type, browser=browser_type, options=options)
    return ua.text


def fetch_version(ua):
    match = re.search(r"Chrome/(\d+)", ua)

    if match:
        major_version = match.group(1)
        return major_version
    else:
        return

