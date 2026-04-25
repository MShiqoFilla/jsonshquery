import json
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers import JsonLexer
from argparse import ArgumentParser
from pathlib import Path
from pydantic import ValidationError
import time

from jsonshquery.models.query import ESRequestBody
from jsonshquery.core import Jsonshquery #search_by_query

INDENT_SIZE = 2

def calculate_indent(current_line: str) -> int:
    stripped = current_line.strip()
    current_indent = len(current_line) - len(current_line.lstrip())
    if stripped.startswith(("}", "]")):
        return max(current_indent - INDENT_SIZE, 0)
    if current_line.rstrip().endswith(("{", "[")):
        return current_indent + INDENT_SIZE
    return current_indent

def get_json_indent_level(full_text: str) -> int:
    """Calculate current JSON brace level from full text"""
    level = 0
    for i, char in enumerate(full_text):
        if char == "{":
            level += 1
        elif char == "}":
            level -= 1
        elif char == "[":
            level += 1
        elif char == "]":
            level -= 1
    return level

def calculate_json_indent(current_line: str, full_text: str) -> int:
    """Calculate indent for next line based on JSON structure"""
    current_level = get_json_indent_level(full_text)
    expected_indent = max(current_level * INDENT_SIZE, 0)
    if current_line.rstrip().endswith(("}", "]")):
        return expected_indent
    if current_line.rstrip().endswith(("{", "[")):
        return expected_indent + INDENT_SIZE

    current_indent = len(current_line) - len(current_line.lstrip())
    return current_indent


def braces_balanced(text: str) -> bool:
    stack = []
    pairs = {
        "}": "{",
        "]": "["
    }
    for ch in text:
        if ch in "{[":
            stack.append(ch)
        elif ch in "}]":
            if not stack or stack.pop() != pairs[ch]:
                return False
    return len(stack) == 0


def app(data):
    session = PromptSession(
        multiline=True,
        lexer=PygmentsLexer(JsonLexer),
    )
    kb = KeyBindings()
    
    # ENTER KEY
    @kb.add("enter")
    def _(event):
        buffer = event.app.current_buffer
        doc = buffer.document

        full_text = buffer.text.rstrip()
        current_line = doc.current_line_before_cursor
        should_submit = (
            full_text.endswith(";")
            and braces_balanced(full_text)
        )
        if should_submit:
            buffer.validate_and_handle()
            return
        char_before = doc.char_before_cursor
        char_after = doc.current_char

        # Expand block when pressing Enter between {}
        if char_before in "{[" and char_after in "}]":
            current_indent = len(current_line) - len(current_line.lstrip())
            inner_indent = current_indent + INDENT_SIZE
            buffer.insert_text(
                "\n"
                + (" " * inner_indent)
                + "\n"
                + (" " * current_indent)
            )
            buffer.cursor_up()
            buffer.cursor_right(inner_indent)
            return

        next_indent = calculate_json_indent(current_line, full_text)
        buffer.insert_text("\n" + (" " * next_indent))

    # AUTO-PAIR OPEN BRACES
    @kb.add('"')
    def _(event):
        buffer = event.app.current_buffer
        doc = buffer.document
        if doc.current_char == '"':
            buffer.cursor_right()
            return
        buffer.insert_text('""')
        buffer.cursor_left()

    @kb.add("{")
    def _(event):
        buffer = event.app.current_buffer
        buffer.insert_text("{}")
        buffer.cursor_left()

    @kb.add("[")
    def _(event):
        buffer = event.app.current_buffer
        buffer.insert_text("[]")
        buffer.cursor_left()

    # SMART CLOSE BRACE
    @kb.add("}")
    def _(event):
        buffer = event.app.current_buffer
        doc = buffer.document

        # Skip over existing }
        if doc.current_char == "}":
            buffer.cursor_right()
            return

        line = doc.current_line_before_cursor
        current_indent = len(line) - len(line.lstrip())
        if line.strip() == "" and current_indent >= INDENT_SIZE:
            buffer.delete_before_cursor(count=INDENT_SIZE)
        buffer.insert_text("}")

    @kb.add("]")
    def _(event):
        buffer = event.app.current_buffer
        doc = buffer.document
        # Skip over existing ]
        if doc.current_char == "]":
            buffer.cursor_right()
            return

        line = doc.current_line_before_cursor
        current_indent = len(line) - len(line.lstrip())
        if line.strip() == "" and current_indent >= INDENT_SIZE:
            buffer.delete_before_cursor(count=INDENT_SIZE)

        buffer.insert_text("]")

    print("JSONSHQUERY")
    print("End statement with ';' and press Enter to submit.")
    print("Press Ctrl+C to exit.\n")

    jshq = Jsonshquery(data=data)

    while True:
        try:
            text = session.prompt(
                ">>> ",
                key_bindings=kb,
            )

            text = text.strip().rstrip(";").strip()

            if not text:
                continue
            try:
                parsed = json.loads(text)
                parsed = ESRequestBody(**json.loads(text))
                query = parsed.model_dump(exclude_unset=True)
                
                start = time.time()
                result = jshq.search_by_query(query)
                execution_time = time.time() - start

                text_res = f"Total Hits = {result['count']}, Execution time = {execution_time:.8f} s"
                print("\n\033[93m" + "    ::: " + text_res + " :::" "\n")

                result_path = query.get("result_path")
                if result_path:
                    dirs = Path(result_path)
                    dirs.parent.mkdir(parents=True, exist_ok=True)
                if not result_path:
                    result_path = "jsonshquery_result.json"

                with open(result_path, "w") as f:
                    json.dump(result, f, indent=4)
            
            except ValidationError:
                print("\n    " + f"\033[91mPlease provide a valid query body!\n")

            # This Exception raised from search_by_query function
            except ValueError as e: 
                print("\n    " + f"\033[91m{e}\n")

            except json.JSONDecodeError:
                print("\n    " + f"\033[95mPlease provide a valid json!\n")

        except KeyboardInterrupt:
            print("\nExiting...")
            break

        except EOFError:
            print("\nExiting...")
            break


def main():
    parser = ArgumentParser(
        description="Query JSON files using Elasticsearch Query DSL syntax"
    )
    parser.add_argument(
        "--file", "-f",
        required=True,
        help="Path to JSON file containing array of documents to query"
    )
    args = parser.parse_args()

    try:
        with open(args.file, "r") as f:
            data = json.load(f)

        if not isinstance(data, list):
            print("Error: JSON file must contain an array of documents")
            return

        print(f"Loaded {len(data)} documents from {args.file}")
        app(data)

    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{args.file}': {e}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")