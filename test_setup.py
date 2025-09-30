#!/usr/bin/env python3
"""
Simple test setup script for AI Agent Digest
This script applies testing configurations by:
1. Disabling all sources except TechCrunch in sources.yaml
2. Commenting out additional search queries in search_agent.yaml
3. Adding return "deliver" at line 63 in main.py
4. Limiting fresh articles to 3 at line 141 in main.py
"""

import os
import re
from pathlib import Path

def setup_test_config():
    """Apply test configurations to the project files."""
    
    # 1. Update sources.yaml - disable all sources except TechCrunch
    sources_file = Path("config/sources.yaml")
    if sources_file.exists():
        with open(sources_file, 'r') as f:
            content = f.read()
        
        # Simple approach: replace all enabled: true with enabled: false, then enable TechCrunch
        content = content.replace('enabled: true', 'enabled: false')
        content = content.replace('TechCrunch\n    type: rss\n    url: "https://techcrunch.com/category/artificial-intelligence/feed/"\n    enabled: false', 
                                 'TechCrunch\n    type: rss\n    url: "https://techcrunch.com/category/artificial-intelligence/feed/"\n    enabled: true')
        
        with open(sources_file, 'w') as f:
            f.write(content)
        
        print("[OK] Updated sources.yaml - disabled all sources except TechCrunch")
    else:
        print("[ERROR] sources.yaml not found")
    
    # 2. Update search_agent.yaml - comment out additional queries
    search_agent_file = Path("config/search_agent.yaml")
    if search_agent_file.exists():
        with open(search_agent_file, 'r') as f:
            content = f.read()
        
        # Comment out the additional search queries
        content = re.sub(
            r'^  - (LangChain agents|autonomous AI agents|multi-agent systems|CrewAI OR AutoGen agents)$',
            r'  # - \1',
            content,
            flags=re.MULTILINE
        )
        
        with open(search_agent_file, 'w') as f:
            f.write(content)
        
        print("[OK] Updated search_agent.yaml - commented out additional queries")
    else:
        print("[ERROR] search_agent.yaml not found")
    
    # 3. Update main.py - add return "deliver" at line 63
    main_file = Path("main.py")
    if main_file.exists():
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Check if return "deliver" is already in the right place
        if 'if state.get("error"):\n            return "END"\n        \n        return "deliver"' in content:
            print("[OK] main.py already has return 'deliver' in correct position")
        else:
            # Add return "deliver" after the error check
            content = content.replace(
                'if state.get("error"):\n            return "END"',
                'if state.get("error"):\n            return "END"\n        \n        return "deliver"'
            )
            
            with open(main_file, 'w') as f:
                f.write(content)
            
            print("[OK] Updated main.py - added return 'deliver' in correct position")
    else:
        print("[ERROR] main.py not found")
    
    # 4. Update main.py - limit fresh articles to 3
    if main_file.exists():
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Check if the limit is already applied
        if 'fresh_articles = fresh_articles[:3]' in content:
            print("[OK] main.py already limits fresh articles to 3")
        else:
            # Add the limit after the logging line
            content = content.replace(
                'logging.info(f"Found {len(fresh_articles)} fresh articles")',
                'logging.info(f"Found {len(fresh_articles)} fresh articles")\n        \n        fresh_articles = fresh_articles[:3]'
            )
            
            with open(main_file, 'w') as f:
                f.write(content)
            
            print("[OK] Updated main.py - limited fresh articles to 3")
    else:
        print("[ERROR] main.py not found")

def restore_production_config():
    """Restore production configurations."""
    
    # 1. Restore sources.yaml - enable all sources
    sources_file = Path("config/sources.yaml")
    if sources_file.exists():
        with open(sources_file, 'r') as f:
            content = f.read()
        
        # Replace all enabled: false with enabled: true
        content = content.replace('enabled: false', 'enabled: true')
        
        with open(sources_file, 'w') as f:
            f.write(content)
        
        print("[OK] Restored sources.yaml - enabled all sources")
    else:
        print("[ERROR] sources.yaml not found")
    
    # 2. Restore search_agent.yaml - uncomment additional queries
    search_agent_file = Path("config/search_agent.yaml")
    if search_agent_file.exists():
        with open(search_agent_file, 'r') as f:
            content = f.read()
        
        # Uncomment the additional search queries
        content = re.sub(
            r'^  # - (LangChain agents|autonomous AI agents|multi-agent systems|CrewAI OR AutoGen agents)$',
            r'  - \1',
            content,
            flags=re.MULTILINE
        )
        
        with open(search_agent_file, 'w') as f:
            f.write(content)
        
        print("[OK] Restored search_agent.yaml - uncommented additional queries")
    else:
        print("[ERROR] search_agent.yaml not found")
    
    # 3. Restore main.py - remove return "deliver" at line 63
    main_file = Path("main.py")
    if main_file.exists():
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Remove the return "deliver" line
        content = content.replace(
            'if state.get("error"):\n            return "END"\n        \n        return "deliver"',
            'if state.get("error"):\n            return "END"'
        )
        
        with open(main_file, 'w') as f:
            f.write(content)
        
        print("[OK] Restored main.py - removed return 'deliver' line")
    else:
        print("[ERROR] main.py not found")
    
    # 4. Restore main.py - remove fresh articles limit
    if main_file.exists():
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Remove the fresh_articles limit line
        content = content.replace(
            'logging.info(f"Found {len(fresh_articles)} fresh articles")\n        \n        fresh_articles = fresh_articles[:3]',
            'logging.info(f"Found {len(fresh_articles)} fresh articles")'
        )
        
        with open(main_file, 'w') as f:
            f.write(content)
        
        print("[OK] Restored main.py - removed fresh articles limit")
    else:
        print("[ERROR] main.py not found")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        print("[INFO] Restoring production configuration...")
        restore_production_config()
        print("[OK] Production configuration restored!")
    else:
        print("[INFO] Setting up test configuration...")
        setup_test_config()
        print("[OK] Test configuration applied!")
        print("\nTo restore production config, run: python test_setup_simple.py restore")
