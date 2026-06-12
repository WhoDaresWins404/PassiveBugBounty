#!/usr/bin/env python3
"""
AI Context Generator
Scans the project directory to generate a comprehensive AI_CONTEXT.md file.
This file provides an AI assistant with the project structure, roadmap status, 
and code capabilities (classes, functions, and docstrings).
"""

import os
import ast
import datetime
from pathlib import Path

# --- Configuration ---
PROJECT_ROOT = Path(__file__).parent.resolve()
OUTPUT_FILE = PROJECT_ROOT / "AI_CONTEXT.md"
ROADMAP_FILE = PROJECT_ROOT / "ROADMAP_STATUS.md"

# Directories and files to ignore to keep the context clean and token-efficient
IGNORE_DIRS = {'.git', '__pycache__', 'venv', 'env', '.venv', 'node_modules', '.pytest_cache', '.idea', '.vscode'}
IGNORE_FILES = {'generate_ai_context.py', 'AI_CONTEXT.md'}
TARGET_EXTENSIONS = {'.py'}

def get_directory_tree(start_path: Path, prefix: str = "") -> str:
    """Generates a visual tree string of the project directory."""
    tree_str = ""
    try:
        # Sort directories first, then files
        entries = sorted(start_path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        entries = [e for e in entries if e.name not in IGNORE_DIRS and e.name not in IGNORE_FILES]
        
        pointers = ["├── "] * (len(entries) - 1) + ["└── "] if entries else []
        for pointer, path in zip(pointers, entries):
            tree_str += f"{prefix}{pointer}{path.name}\n"
            if path.is_dir():
                extension = "│   " if pointer == "├── " else "    "
                tree_str += get_directory_tree(path, prefix + extension)
    except PermissionError:
        pass
    return tree_str

def parse_python_file(filepath: Path) -> str:
    """Parses a Python file to extract module docstrings, classes, functions, and their docstrings."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source, filename=str(filepath))
        result = []
        rel_path = filepath.relative_to(PROJECT_ROOT)
        result.append(f"### 📄 `{rel_path}`\n")

        # Module docstring
        module_doc = ast.get_docstring(tree)
        if module_doc:
            result.append(f"**Module Description:**\n> {module_doc}\n")

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                docstring = ast.get_docstring(node)
                doc_str = f"\n> {docstring}" if docstring else "\n> *(No docstring provided)*"
                
                if isinstance(node, ast.ClassDef):
                    result.append(f"**Class:** `{node.name}`{doc_str}")
                    # Extract methods
                    methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name != '__init__']
                    for method in methods:
                        m_doc = ast.get_docstring(method)
                        m_doc_str = f"\n> {m_doc}" if m_doc else ""
                        # Basic signature extraction
                        args = [arg.arg for arg in method.args.args if arg.arg != 'self']
                        result.append(f"  - **Method:** `{method.name}({', '.join(args)})`{m_doc_str}")
                else:
                    result.append(f"**Function:** `{node.name}()`{doc_str}")
        
        return "\n".join(result) + "\n"
    
    except SyntaxError as e:
        return f"### 📄 `{filepath.relative_to(PROJECT_ROOT)}`\n*(Warning: Syntax error in file, could not parse: {e})*\n"
    except Exception as e:
        return f"### 📄 `{filepath.relative_to(PROJECT_ROOT)}`\n*(Warning: Could not read file: {e})*\n"

def read_roadmap() -> str:
    """Reads the manual roadmap status file."""
    if ROADMAP_FILE.exists():
        with open(ROADMAP_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return "*(ROADMAP_STATUS.md not found. Please create it to track progress.)*"

def generate_context():
    """Main orchestrator to generate the AI_CONTEXT.md file."""
    print(f"🔍 Scanning project at: {PROJECT_ROOT}")
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md_content = [
        "# 🧠 AI Project Context\n",
        f"*Generated automatically on: {timestamp}*\n",
        "This file provides the AI assistant with the current state of the project, directory structure, and code capabilities.\n",
        "---\n"
    ]
    
    # 1. Roadmap Status
    md_content.append("## 🗺️ 1. Project Roadmap & Status\n")
    md_content.append(read_roadmap())
    md_content.append("\n---\n")
    
    # 2. Directory Structure
    md_content.append("## 📂 2. Directory Structure\n")
    md_content.append("```\n")
    md_content.append(f"{PROJECT_ROOT.name}/\n")
    md_content.append(get_directory_tree(PROJECT_ROOT))
    md_content.append("```\n")
    md_content.append("\n---\n")
    
    # 3. Codebase Capabilities
    md_content.append("## 💻 3. Codebase Capabilities (Signatures & Docstrings)\n")
    
    # Find all target files
    py_files = []
    for ext in TARGET_EXTENSIONS:
        py_files.extend(PROJECT_ROOT.rglob(f"*{ext}"))
    
    # Filter out ignored directories
    valid_files = [
        f for f in py_files 
        if not any(ignore_dir in f.parts for ignore_dir in IGNORE_DIRS) 
        and f.name not in IGNORE_FILES
    ]
    
    for filepath in sorted(valid_files):
        md_content.append(parse_python_file(filepath))
    
    # Write to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
        
    print(f"✅ Successfully generated: {OUTPUT_FILE}")
    print("💡 Tip: Upload this file to your AI assistant at the start of a new chat session for instant project context.")

if __name__ == "__main__":
    generate_context()