#!/usr/bin/env python3
"""
Static site generator for Live-SWE-agent leaderboard
Converts YAML data to static HTML using Jinja2 templates
"""

import json
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import yaml
import markdown


def load_yaml_data(yaml_file: Path) -> dict:
    """Load leaderboard data from YAML file and auto-generate names"""
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    # Auto-generate 'name' from 'display_name' if not provided
    for leaderboard in data.get('leaderboards', []):
        if 'name' not in leaderboard and 'display_name' in leaderboard:
            # Convert to lowercase and replace spaces/special chars with underscores
            display_name = leaderboard['display_name']
            auto_name = display_name.lower().replace(' ', '_').replace('-', '_')
            # Remove any non-alphanumeric characters except underscores
            auto_name = ''.join(c if c.isalnum() or c == '_' else '' for c in auto_name)
            leaderboard['name'] = auto_name

    return data


def load_markdown_content(content_dir: Path) -> dict:
    """Load about.md and split by H2 sections, extract Paper URL"""
    import re

    md = markdown.Markdown(extensions=['fenced_code', 'tables', 'nl2br'])
    content = {}

    about_file = content_dir / 'about.md'

    if about_file.exists():
        with open(about_file, 'r', encoding='utf-8') as f:
            md_text = f.read()

        # Extract Paper URL from HTML comment
        paper_url_match = re.search(r'<!-- Paper URL: (.+?) -->', md_text)
        if paper_url_match:
            content['paper_url'] = paper_url_match.group(1).strip()
        else:
            content['paper_url'] = 'https://www.swebench.com'  # Default

        # Split by H2 headers (## Title)
        # Pattern: ## Section Title
        sections = re.split(r'\n## ', md_text)

        # First section is the main About content (before first ##)
        if sections:
            main_content = sections[0].replace('# About\n\n', '')
            # Remove the Paper URL comment
            main_content = re.sub(r'<!-- Paper URL: .+? -->\n\n', '', main_content)
            if main_content.strip():
                content['about'] = md.convert(main_content)
                md.reset()

        # Process each H2 section
        for section in sections[1:]:
            # Extract section title (first line)
            lines = section.split('\n', 1)
            if len(lines) >= 1:
                title = lines[0].strip().lower()  # e.g., "Code" -> "code"
                section_content = lines[1] if len(lines) > 1 else ''

                # Add the H2 header back for proper rendering
                full_section = f'## {lines[0]}\n{section_content}'
                content[title] = md.convert(full_section)
                md.reset()
    else:
        print(f"⚠ Warning: about.md not found")
        content['about'] = ''
        content['code'] = ''
        content['citation'] = ''
        content['paper_url'] = 'https://www.swebench.com'

    return content


def extract_tags(leaderboards_data: dict) -> tuple[dict, list]:
    """
    Extract tags from leaderboard data
    Returns: (leaderboard_tags, all_tags)
    - leaderboard_tags: {leaderboard_name: [tag1, tag2, ...]}
    - all_tags: [unique tags across all leaderboards]
    """
    leaderboard_tags = {}
    all_tags_set = set()

    for leaderboard in leaderboards_data['leaderboards']:
        name = leaderboard['name']
        tags = set()

        for result in leaderboard['results']:
            if 'tags' in result:
                for tag in result['tags']:
                    tags.add(tag)
                    all_tags_set.add(tag)

        leaderboard_tags[name] = sorted(list(tags))

    all_tags = sorted(list(all_tags_set))
    return leaderboard_tags, all_tags


def copy_static_files(src_dir: Path, dest_dir: Path):
    """Copy static files (CSS, JS, images) to dist directory"""
    static_dirs = ['css', 'js', 'img']

    for dirname in static_dirs:
        src = src_dir / dirname
        dest = dest_dir / dirname

        if src.exists():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
            print(f"✓ Copied {dirname}/")


def build_site():
    """Main build function"""
    print("Building Live-SWE-agent leaderboard site...")

    # Setup paths
    base_dir = Path(__file__).parent
    templates_dir = base_dir / 'templates'
    data_dir = base_dir / 'data'
    content_dir = base_dir / 'content'
    dist_dir = base_dir / 'dist'

    # Load data
    print("\nLoading data...")
    leaderboards_data = load_yaml_data(data_dir / 'leaderboards.yaml')
    leaderboard_tags, all_tags = extract_tags(leaderboards_data)
    markdown_content = load_markdown_content(content_dir)

    print(f"✓ Loaded {len(leaderboards_data['leaderboards'])} leaderboards")
    print(f"✓ Extracted {len(all_tags)} unique tags")
    print(f"✓ Loaded {len(markdown_content)} markdown content files")

    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader(templates_dir))

    # Create dist directory
    dist_dir.mkdir(exist_ok=True)

    # Copy static files
    print("\nCopying static files...")
    copy_static_files(base_dir, dist_dir)

    # Render index page
    print("\nRendering pages...")
    template = env.get_template('index.html')

    # Extract footer links from YAML, use defaults if not present
    footer_links = leaderboards_data.get('footer_links', [
        {'name': 'GitHub', 'url': 'https://github.com/your-org/live-swe-agent'},
        {'name': 'HuggingFace', 'url': 'https://huggingface.co/your-org'},
        {'name': 'Paper', 'url': 'https://www.swebench.com'}
    ])

    # Extract website title, subtitle, section title and description
    website_title = leaderboards_data.get('website_title', 'Live-SWE-agent Leaderboard')
    website_subtitle = leaderboards_data.get('website_subtitle', None)
    section_title = leaderboards_data.get('section_title', 'Leaderboard')
    section_description = leaderboards_data.get('section_description',
        'Performance of various language models using the Live-SWE-agent scaffold on SWE-bench datasets.')

    html = template.render(
        leaderboards=leaderboards_data['leaderboards'],
        leaderboard_tags=leaderboard_tags,
        all_tags=all_tags,
        content=markdown_content,
        footer_links=footer_links,
        website_title=website_title,
        website_subtitle=website_subtitle,
        section_title=section_title,
        section_description=section_description
    )

    output_file = dist_dir / 'index.html'
    output_file.write_text(html)
    print(f"✓ Rendered index.html")

    print("\n✅ Build complete! Output in dist/")
    print(f"   Run: python3 -m http.server --directory dist/ 8000")


if __name__ == '__main__':
    build_site()
