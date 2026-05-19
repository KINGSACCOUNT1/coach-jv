"""
Icon Replacement Script - Replace emoji with Font Awesome icons
Run this to automatically update all templates
"""

import os
import re
from pathlib import Path

# Emoji to Font Awesome mapping
ICON_REPLACEMENTS = {
    # Navigation & Features
    '📊': '<i class="fas fa-chart-line"></i>',
    '💰': '<i class="fas fa-coins"></i>',
    '💎': '<i class="fas fa-gem"></i>',
    '🎓': '<i class="fas fa-graduation-cap"></i>',
    '👥': '<i class="fas fa-users"></i>',
    '⛏️': '<i class="fas fa-hammer"></i>',
    '💼': '<i class="fas fa-briefcase"></i>',
    '📈': '<i class="fas fa-chart-line"></i>',
    '🔒': '<i class="fas fa-lock"></i>',
    '🔐': '<i class="fas fa-shield-alt"></i>',
    '📰': '<i class="fas fa-newspaper"></i>',
    '🎁': '<i class="fas fa-gift"></i>',
    '📚': '<i class="fas fa-book"></i>',
    '🎥': '<i class="fas fa-video"></i>',
    '📱': '<i class="fas fa-mobile-alt"></i>',
    '⚙️': '<i class="fas fa-cog"></i>',
    '📧': '<i class="fas fa-envelope"></i>',
    '💬': '<i class="fas fa-comments"></i>',
    '🤝': '<i class="fas fa-handshake"></i>',
    '👤': '<i class="fas fa-user-circle"></i>',
    '🎤': '<i class="fas fa-chalkboard-teacher"></i>',
    '🎯': '<i class="fas fa-bullseye"></i>',
    '🎫': '<i class="fas fa-ticket-alt"></i>',
    
    # Status Indicators
    '✅': '<i class="fas fa-check-circle text-success"></i>',
    '❌': '<i class="fas fa-times-circle text-danger"></i>',
    '⏳': '<i class="fas fa-hourglass-half text-warning"></i>',
    '🔴': '<i class="fas fa-circle text-danger"></i>',
    '🟢': '<i class="fas fa-circle text-success"></i>',
    '🟡': '<i class="fas fa-circle text-warning"></i>',
    
    # Actions & Features
    '🔔': '<i class="fas fa-bell"></i>',
    '🔍': '<i class="fas fa-search"></i>',
    '📁': '<i class="fas fa-folder"></i>',
    '📂': '<i class="fas fa-folder-open"></i>',
    '📝': '<i class="fas fa-edit"></i>',
    '🗑️': '<i class="fas fa-trash"></i>',
    '⬆️': '<i class="fas fa-arrow-up"></i>',
    '⬇️': '<i class="fas fa-arrow-down"></i>',
    '➡️': '<i class="fas fa-arrow-right"></i>',
    '⬅️': '<i class="fas fa-arrow-left"></i>',
    '🔄': '<i class="fas fa-sync"></i>',
    '📥': '<i class="fas fa-download"></i>',
    '📤': '<i class="fas fa-upload"></i>',
    '💾': '<i class="fas fa-save"></i>',
    '🖨️': '<i class="fas fa-print"></i>',
    '📋': '<i class="fas fa-clipboard"></i>',
    
    # Emotions & Reactions
    '👍': '<i class="fas fa-thumbs-up"></i>',
    '👎': '<i class="fas fa-thumbs-down"></i>',
    '❤️': '<i class="fas fa-heart"></i>',
    '⭐': '<i class="fas fa-star"></i>',
    '🎉': '<i class="fas fa-trophy"></i>',
    '🏆': '<i class="fas fa-trophy"></i>',
    '🚀': '<i class="fas fa-rocket"></i>',
    
    # Special Characters
    '💡': '<i class="fas fa-lightbulb"></i>',
    '🛡️': '<i class="fas fa-shield-alt"></i>',
    '⚡': '<i class="fas fa-bolt"></i>',
    '🔗': '<i class="fas fa-link"></i>',
    '📆': '<i class="fas fa-calendar"></i>',
    '🕒': '<i class="fas fa-clock"></i>',
    '📍': '<i class="fas fa-map-marker-alt"></i>',
    '🌐': '<i class="fas fa-globe"></i>',
    '💳': '<i class="fas fa-credit-card"></i>',
    '🏦': '<i class="fas fa-university"></i>',
    '📉': '<i class="fas fa-chart-line"></i>',
    '🥧': '<i class="fas fa-chart-pie"></i>',
    
    # Section Headers (preserve emoji but add icon)
    '🎊': '<i class="fas fa-party-horn"></i>',
    '😱': '<i class="fas fa-exclamation-triangle"></i>',
}

def replace_icons_in_file(file_path):
    """Replace emoji icons with Font Awesome in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        replacements_made = 0
        
        # Replace each emoji
        for emoji, fontawesome in ICON_REPLACEMENTS.items():
            if emoji in content:
                content = content.replace(emoji, fontawesome)
                replacements_made += content.count(fontawesome) - original_content.count(fontawesome)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return replacements_made
        
        return 0
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def process_templates(templates_dir):
    """Process all HTML templates in directory"""
    total_replacements = 0
    files_modified = 0
    
    templates_path = Path(templates_dir)
    
    # Find all HTML files
    html_files = list(templates_path.rglob('*.html'))
    
    print(f"Found {len(html_files)} HTML files to process...\n")
    
    for html_file in html_files:
        replacements = replace_icons_in_file(html_file)
        if replacements > 0:
            files_modified += 1
            total_replacements += replacements
            print(f"✓ {html_file.name}: {replacements} icons replaced")
    
    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"Files modified: {files_modified}")
    print(f"Total replacements: {total_replacements}")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    # Get templates directory (script is in project root)
    base_dir = Path(__file__).resolve().parent
    templates_dir = base_dir / "templates"
    
    if not templates_dir.exists():
        print(f"Templates directory not found: {templates_dir}")
        print("Please run this script from the project root directory.")
        exit(1)
    
    print("=" * 50)
    print("CoachJVTech Icon Replacement Script")
    print("=" * 50)
    print(f"Templates directory: {templates_dir}\n")
    
    # Ask for confirmation
    response = input("This will replace ALL emoji icons with Font Awesome. Continue? (y/n): ")
    
    if response.lower() == 'y':
        process_templates(templates_dir)
        print("\n✓ Icon replacement complete!")
        print("\nNext steps:")
        print("1. Review changes in templates")
        print("2. Add cryptocurrency logo images")
        print("3. Create/add main logo")
        print("4. Test pages in browser")
    else:
        print("Operation cancelled.")
