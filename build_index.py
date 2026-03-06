import urllib.request
import json
import os
import datetime

def build_index():
    USERNAME = "LuminairPrime"
    # Using the GitHub Actions standard token environment variable
    TOKEN = os.environ.get("GITHUB_TOKEN")
    
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=updated"
    req = urllib.request.Request(url)
    req.add_header('Accept', 'application/vnd.github.v3+json')
    req.add_header('User-Agent', 'LuminairPrime-Index-Builder')
    
    # If the token exists, inject it to get up to 1000 requests/hr
    if TOKEN:
        req.add_header('Authorization', f'token {TOKEN}')

    print(f"Fetching repository metadata for {USERNAME}...")
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching API data: {e}")
        exit(1)

    html_snippets = []
    
    # Filter only repositories with active GitHub pages
    for repo in data:
        # Prevent self-referencing if someone configures the root repo
        if repo['name'] == f"{USERNAME}.github.io":
            continue
            
        if repo.get('has_pages', False):
            name = repo.get('name', 'Unknown')
            desc = repo.get('description') or "No description provided."
            url = f"https://{USERNAME}.github.io/{name}/"
            
            # Format update date into something cleaner
            raw_date = repo.get('updated_at', '2000-01-01T00:00:00Z')
            clean_date = datetime.datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%b %d, %Y")
            lang = repo.get('language') or 'N/A'

            card = f"""
        <a href="{url}" class="card">
            <h2>{name}</h2>
            <p class="desc">{desc}</p>
            <div class="meta">
                <span>{lang}</span>
                <span>Updated: {clean_date}</span>
            </div>
        </a>"""
            html_snippets.append(card)

    if not html_snippets:
        html_snippets.append('<p style="grid-column: 1 / -1; text-align: center; color: #94a3b8;">No projects with GitHub Pages currently active.</p>')

    final_injection = "\n".join(html_snippets)

    # Inject into the template
    print("Reading HTML template...")
    try:
        with open("index_template.html", "r", encoding="utf-8") as f:
            template = f.read()
            
        final_html = template.replace("<!-- PROJECTS_INJECT_HERE -->", final_injection)
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(final_html)
            
        print(f"Successfully generated index.html containing {len(html_snippets)} projects.")
    except Exception as e:
        print(f"Failed to assemble HTML: {e}")
        exit(1)

if __name__ == "__main__":
    build_index()
