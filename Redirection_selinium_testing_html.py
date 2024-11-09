from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests

site_type = HTML

# Initialize options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")

# Set up WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Define the base domain and components
domain = "example.com"  # Replace with your domain without "http://" or "https://"
protocols = ["http", "https"]
subdomains = ["", "www"]
paths = [
    "", "/index.html", "/index.php", "/blog.html", "/horror", "////////////////", 
     "/blog.html////////////////", "////////////////horror/"
]

# File to store redirection results
result_file = "redirection_results.txt"

def determine_expected_redirections(protocol, subdomain, path):
    """
    Determines the expected redirection chain based on URL components.
    Adds an extra redirection if the path leads to a 404 page.
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
    
    # Determine if additional redirection is needed to reach a 404 page
    if path in ["/index.html", "/index.php", "/horror", "////////////////horror/", "/blog.html////////////////"]:
        # Two-step redirection before reaching final 404 page
        expected_chain.extend([301, 200])  # Last 200 means display of 404.html or equivalent
    else:
        expected_chain.append(200)  # Final destination is homepage or other paths
    
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
