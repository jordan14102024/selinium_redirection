from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests

# Initialize options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")

# Set up WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Define the base domain and components
domain = "piranti.hk"  # Replace with your domain
protocols = ["http", "https"]
subdomains = ["", "www"]
paths = [
    "", "/index.html", "/index.php", "/blogs/", "////////////////", 
    "/blogs////////////////", "////////////////error/"
]

# File to store redirection results
result_file = "redirection_results.txt"

def determine_expected_redirections(protocol, subdomain, path):
    """
    Determines the expected redirection chain based on URL components.
    Adds an extra redirection if WordPress redirects the path.
    """
    expected_chain = []
    
    # Rule for HTTP -> HTTPS redirection
    if protocol == "http":
        expected_chain.append(301)
        protocol = "https"
    
    # Rule for WWW -> Non-WWW redirection
    if subdomain == "www":
        expected_chain.append(301)
        subdomain = ""
    
    # Define specific rules for WordPress redirects
    if path == "/index.php":
        # Additional 301 for `/index.php` to home
        expected_chain.extend([301, 200])
    elif path == "/index.html":
        # Redirects directly to a 404 page
        expected_chain.extend([404])
    elif path == "////////////////error/":
        # Redirects directly to a 404 page
        expected_chain.extend([404])    
    elif path == "/blogs////////////////":
        # Redirects directly to a 404 page
        expected_chain.extend([301])        
    else:
        expected_chain.append(200)
    
    return expected_chain

def check_redirection(url, expected_redirections):
    """
    Checks the redirection path for a given URL and compares it with expected redirections.
    Returns a result message.
    """
    current_url = url
    redirection_chain = []

    try:
        for expected_code in expected_redirections:
            response = requests.head(current_url, allow_redirects=False)

            # Store the actual status code
            status_code = response.status_code
            redirection_chain.append(status_code)

            # Check if the current status matches the expected status
            if status_code != expected_code:
                return f"Redirection check failed for {url}. Expected: {expected_redirections}, Got: {redirection_chain}"

            # Update current URL for the next step in the chain if it's a redirect
            if status_code in [301, 302]:
                current_url = response.headers["Location"]
            elif status_code == 200:
                # Reached final destination
                break

        # Successful check if all expected codes matched
        if redirection_chain == expected_redirections:
            return f"Redirection correct for {url}: {redirection_chain}"
        else:
            return f"Redirection incorrect for {url}. Expected: {expected_redirections}, Got: {redirection_chain}"

    except Exception as e:
        return f"Error checking redirection for {url}: {str(e)}"

# Write results to file
with open(result_file, "w") as file:
    for path in paths:
        for protocol in protocols:
            for subdomain in subdomains:
                url = f"{protocol}://{subdomain + '.' if subdomain else ''}{domain}{path}"
                expected_redirections = determine_expected_redirections(protocol, subdomain, path)
                result = check_redirection(url, expected_redirections)
                file.write(result + "\n")
                print(result)

# Close the driver
driver.quit()

