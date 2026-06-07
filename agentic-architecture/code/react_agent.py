"""
Real ReAct Agent for E-Commerce Customer Support

This is a REAL agent that:
1. Uses Claude (or local LLM) as the reasoning engine
2. Has actual tools that retrieve real data
3. Solves actual customer support problems
4. Shows transparent reasoning process

Domain: E-Commerce Customer Support

Requirements:
    pip install anthropic python-dotenv

Setup (Choose ONE):

OPTION 1: Use Anthropic API (Claude)
    1. Get your API key from https://console.anthropic.com
    2. Create a .env file with: ANTHROPIC_API_KEY=your_key_here
    3. Run: python react_agent.py

OPTION 2: Use Local Model (Ollama - NO API KEY NEEDED)
    1. Install Ollama: https://ollama.ai
    2. Run: ollama pull mistral && ollama serve
    3. Run: python react_agent.py
"""

import os
import json
import requests
from typing import Optional
from dataclasses import dataclass
from enum import Enum
from anthropic import Anthropic

# ============================================================================
# OLLAMA CLIENT - Wrapper for calling Ollama API
# ============================================================================

class OllamaClient:
    """Wrapper for Ollama API optimized for local models like Mistral"""
    def __init__(self, model="mistral"):
        self.model = model
        self.api_url = "http://localhost:11434/api/generate"

    def messages_create(self, system, messages, max_tokens=1000):
        """Create a message using Ollama API with proper prompt formatting"""

        # Build a better prompt structure for local models
        full_prompt = system + "\n\n"

        # Add conversation history
        for msg in messages:
            role = msg["role"].upper()
            content = msg["content"]
            if role == "USER":
                full_prompt += f"User: {content}\n\n"
            elif role == "ASSISTANT":
                full_prompt += f"Assistant: {content}\n\n"

        # Force the model to start with the right prefix
        full_prompt += "Assistant: "

        # Call Ollama with conservative settings for better results
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": 0.3,  # Lower temperature = more consistent output
                    "num_predict": max_tokens,
                },
                timeout=120
            )

            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.status_code}")

            # Extract the response
            response_text = response.json().get("response", "").strip()

            # Return in Anthropic-compatible format
            class MockResponse:
                def __init__(self, text):
                    self.content = [type('obj', (object,), {'text': text})]

            return MockResponse(response_text)
        except Exception as e:
            raise Exception(f"Ollama error: {e}")

# ============================================================================
# CONFIGURATION - Switch between Anthropic API and Local Models
# ============================================================================

USE_LOCAL_MODEL = True  # Set to False to use Anthropic API instead

if USE_LOCAL_MODEL:
    print("🚀 Using LOCAL model (Ollama)")

    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print(f"✓ Ollama is running with models: {[m['name'] for m in models]}\n")
            else:
                print("⚠️  Ollama running but no models. Running: ollama pull mistral\n")
                os.system("ollama pull mistral")
        else:
            raise Exception("Ollama not responding")
    except Exception as e:
        print(f"❌ ERROR: Ollama is not running!")
        print(f"   Error: {e}")
        print("   Start Ollama: /Users/gaurav/Documents/Ollama/restart_ollama.sh")
        exit(1)

    client = OllamaClient(model="mistral")
    MODEL_NAME = "mistral"
else:
    print("🔑 Using Anthropic API (Claude)")
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("Please set your API key: export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)

    client = Anthropic()
    MODEL_NAME = "claude-3-5-sonnet-20241022"

print(f"✓ Model: {MODEL_NAME}\n")

# ============================================================================
# SIMULATED DATABASE - In real system, these would be actual databases
# ============================================================================

PRODUCT_DATABASE = {
    # Budget Laptops
    "LAPTOP-001": {
        "name": "Budget Laptop 13",
        "price": 449.99,
        "in_stock": True,
        "warranty": "1 year",
        "specs": "Intel i3, 4GB RAM, 128GB SSD, 13.3\" display - Great for students"
    },
    "LAPTOP-002": {
        "name": "Value Laptop 15",
        "price": 599.99,
        "in_stock": True,
        "warranty": "1 year",
        "specs": "Intel i5, 8GB RAM, 256GB SSD, 15.6\" display - Good all-rounder"
    },

    # Mid-Range Laptops
    "LAPTOP-003": {
        "name": "ProBook 15 Laptop",
        "price": 999.99,
        "in_stock": True,
        "warranty": "2 years",
        "specs": "Intel i7, 16GB RAM, 512GB SSD, 15.6\" display - High performance"
    },
    "LAPTOP-004": {
        "name": "WorkStation Pro",
        "price": 1399.99,
        "in_stock": True,
        "warranty": "3 years",
        "specs": "Intel i9, 32GB RAM, 1TB SSD, 17\" display - Professional grade"
    },

    # Phones
    "PHONE-001": {
        "name": "SmartPhone X",
        "price": 899.99,
        "in_stock": True,
        "warranty": "1 year",
        "specs": "6.5\" OLED, 128GB storage, 5G, excellent camera"
    },
    "PHONE-002": {
        "name": "Budget Phone Basic",
        "price": 299.99,
        "in_stock": True,
        "warranty": "1 year",
        "specs": "6.1\" LCD, 64GB storage, 4G, good for basic use"
    },

    # Accessories
    "HEADPHONES-001": {
        "name": "AudioMax Pro",
        "price": 199.99,
        "in_stock": False,
        "warranty": "1 year",
        "specs": "Noise cancelling, 30hr battery, Bluetooth 5.0"
    },
    "HEADPHONES-002": {
        "name": "Budget Headphones",
        "price": 49.99,
        "in_stock": True,
        "warranty": "6 months",
        "specs": "Wireless, 20hr battery, Bluetooth 5.0"
    },
    "MONITOR-001": {
        "name": "UltraWide Monitor",
        "price": 499.99,
        "in_stock": True,
        "warranty": "3 years",
        "specs": "34\" curved, 3440x1440, 144Hz, USB-C"
    }
}

CUSTOMER_ORDERS = {
    "ORD-12345": {
        "customer": "John Smith",
        "order_date": "2024-04-15",
        "status": "Delivered",
        "items": ["LAPTOP-001"],
        "total": 1299.99,
        "tracking": "Track00123"
    },
    "ORD-12346": {
        "customer": "Jane Doe",
        "order_date": "2024-05-01",
        "status": "Processing",
        "items": ["PHONE-001", "HEADPHONES-001"],
        "total": 1099.98,
        "tracking": "Track00124"
    },
    "ORD-12347": {
        "customer": "Bob Wilson",
        "order_date": "2024-04-20",
        "status": "Delivered",
        "items": ["MONITOR-001"],
        "total": 499.99,
        "tracking": "Track00125"
    }
}

RETURN_POLICY = """
RETURN POLICY:
- 30-day return window from delivery date
- Items must be in original condition
- Full refund minus 5% restocking fee
- Free return shipping for defective items
- Electronics: 15-day return window only
"""

FAQS = {
    "shipping": "We ship within 2-3 business days. Standard shipping takes 5-7 days. Express shipping available.",
    "warranty": "All products come with manufacturer warranty. Extended warranty available at purchase.",
    "defective": "If item is defective within 30 days, we offer free replacement or full refund.",
    "payment": "We accept credit cards, PayPal, and Apple Pay.",
    "tracking": "Track your order using the tracking number sent via email."
}

# ============================================================================
# REAL TOOLS - These actually interact with the "database"
# ============================================================================

def search_product(product_name: str) -> str:
    """Search for a product - matches keywords and sorts by relevance and price"""
    matching_products = []
    search_lower = product_name.lower()

    # Extract keywords from search (words longer than 2 chars)
    keywords = [w for w in search_lower.split() if len(w) > 2]

    for product_id, product in PRODUCT_DATABASE.items():
        product_name_lower = product["name"].lower()

        # Match if: exact substring OR any keyword matches
        if search_lower in product_name_lower:
            # Exact match
            matching_products.append((product_id, product))
        elif keywords:
            # Check if ANY keyword is in the product name
            for keyword in keywords:
                if keyword in product_name_lower:
                    matching_products.append((product_id, product))
                    break

    if matching_products:
        # Sort by price (ascending) so "cheap" searches show affordable options first
        matching_products.sort(key=lambda x: x[1]["price"])
        result_lines = [f"{pid}: {p['name']} - ${p['price']}" for pid, p in matching_products]
        return f"Found {len(matching_products)} product(s):\n" + "\n".join(result_lines)

    # If no exact match, show all products sorted by price
    all_products = sorted(PRODUCT_DATABASE.items(), key=lambda x: x[1]["price"])
    all_product_lines = [f"{pid}: {p['name']} - ${p['price']}" for pid, p in all_products]
    return f"No exact match for '{product_name}'. Here are all our products:\n" + "\n".join(all_product_lines)


def check_product_details(product_id: str) -> str:
    """Get detailed information about a specific product"""
    if product_id in PRODUCT_DATABASE:
        product = PRODUCT_DATABASE[product_id]
        return f"""
Product: {product['name']}
Price: ${product['price']}
In Stock: {'Yes' if product['in_stock'] else 'No'}
Warranty: {product['warranty']}
Specs: {product['specs']}
"""
    return f"Product {product_id} not found"


def check_order_status(order_id: str) -> str:
    """Check the status of a customer's order"""
    if order_id in CUSTOMER_ORDERS:
        order = CUSTOMER_ORDERS[order_id]
        return f"""
Order ID: {order_id}
Status: {order['status']}
Order Date: {order['order_date']}
Items: {', '.join(order['items'])}
Total: ${order['total']}
Tracking: {order['tracking']}
"""
    return f"Order {order_id} not found"


def get_return_policy() -> str:
    """Get the company's return policy"""
    return RETURN_POLICY


def search_faq(topic: str) -> str:
    """Search FAQ for common questions"""
    if topic.lower() in FAQS:
        return f"FAQ - {topic.upper()}:\n{FAQS[topic.lower()]}"
    return f"No FAQ found for '{topic}'. Available topics: {', '.join(FAQS.keys())}"


def process_refund(order_id: str, reason: str) -> str:
    """Process a refund for an order"""
    if order_id in CUSTOMER_ORDERS:
        order = CUSTOMER_ORDERS[order_id]
        refund_amount = order['total'] * 0.95  # 5% restocking fee
        return f"""
Refund processed for order {order_id}
Original amount: ${order['total']}
Refund amount (after 5% fee): ${refund_amount:.2f}
Reason: {reason}
Refund will appear in 3-5 business days
"""
    return f"Cannot process refund: Order {order_id} not found"


def escalate_to_human(reason: str) -> str:
    """Escalate issue to human support"""
    return f"""
Issue escalated to human support agent.
Reason: {reason}
A support specialist will contact you within 2 hours.
Reference ID: SUP-{hash(reason) % 10000:05d}
"""


# ============================================================================
# TOOL EXECUTION
# ============================================================================

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool and return the result"""
    tools = {
        "search_product": lambda: search_product(tool_input.get("product_name", "")),
        "check_product_details": lambda: check_product_details(tool_input.get("product_id", "")),
        "check_order_status": lambda: check_order_status(tool_input.get("order_id", "")),
        "get_return_policy": lambda: get_return_policy(),
        "search_faq": lambda: search_faq(tool_input.get("topic", "")),
        "process_refund": lambda: process_refund(
            tool_input.get("order_id", ""),
            tool_input.get("reason", "")
        ),
        "escalate_to_human": lambda: escalate_to_human(tool_input.get("reason", ""))
    }

    if tool_name in tools:
        return tools[tool_name]()
    return f"Unknown tool: {tool_name}"


# ============================================================================
# REACT AGENT - Uses model as the brain
# ============================================================================

class ReActEcommerceAgent:
    """Real ReAct Agent for E-Commerce Customer Support"""

    def __init__(self):
        self.conversation_history = []
        self.thought_action_log = []
        self.model = MODEL_NAME  # Uses the configured model (local or Anthropic)

    def get_system_prompt(self) -> str:
        """ReAct system prompt - guides reasoning about observations"""
        return """You are a ReAct (Reasoning + Acting) agent. Follow this exact pattern:

STEP 1 - Think (THOUGHT):
THOUGHT: [brief reasoning about what to do]

STEP 2 - Act (ACTION):
ACTION: [tool_name(param=value)]

STEP 3 - Observe (you will receive OBSERVATION):
The system will give you tool results as OBSERVATION:

STEP 4 - Reason about observation (THOUGHT):
After OBSERVATION, output another THOUGHT to reason about the result:
THOUGHT: [reason about what the observation means]

STEP 5 - Decide (ACTION or FINAL ANSWER):
Either:
  a) ACTION: [call another tool if you need more info]
  b) FINAL ANSWER: [answer the user's question]

CRITICAL RULES:
1. Always reason ABOUT observations before acting
2. One ACTION per response - NEVER multiple actions
3. Use only REAL tool names and parameters
4. No fake data - only use tool results
5. Loop until you can provide FINAL ANSWER

Available tools:
- search_product(product_name=TEXT)
- check_product_details(product_id=TEXT)
- check_order_status(order_id=TEXT)
- get_return_policy()
- search_faq(topic=TEXT)
- process_refund(order_id=TEXT,reason=TEXT)
- escalate_to_human(reason=TEXT)

CORRECT EXAMPLE - With Reasoning Loop:
User: "What's a good cheap laptop?"

[Iteration 1]
THOUGHT: User wants a cheap laptop. I should search for affordable options.
ACTION: search_product(product_name=cheap laptop)

[You receive: OBSERVATION: Found Budget Laptop 13 - $449.99, Value Laptop 15 - $599.99]

[Iteration 2]
THOUGHT: Good! I found two affordable options. The Budget Laptop is cheapest at $449.99.
         Should I get more details? Let me check what the user really wants - just price or also specs?
         I have enough info, I can answer now.
FINAL ANSWER: I recommend the Budget Laptop 13 at $449.99. It's very affordable with great value.
              If you want better specs, the Value Laptop 15 at $599.99 is excellent."""

    def process_response(self, response_text: str) -> tuple[str, bool]:
        """Parse response - case-insensitive, handles typos

        Important: If multiple ACTIONs exist, takes only the FIRST one.
        This enforces the ReAct pattern: one action per iteration.
        """

        response_upper = response_text.upper()

        # PRIORITY 1: Look for FINAL ANSWER (case-insensitive)
        if "FINAL ANSWER" in response_upper:
            # Find the actual position in original text
            idx = response_upper.find("FINAL ANSWER")
            # Find the colon after it
            colon_idx = response_text.find(":", idx)
            if colon_idx != -1:
                final_answer = response_text[colon_idx+1:].strip()
                # Take only first paragraph
                if "\n\n" in final_answer:
                    final_answer = final_answer.split("\n\n")[0]
                # Stop at next section
                for marker in ["\nthought", "\naction", "\nTHOUGHT", "\nACTION"]:
                    if marker.lower() in final_answer.lower():
                        final_answer = final_answer.split(marker)[0]
                return final_answer.strip(), True

        # PRIORITY 2: Look for ACTION (case-insensitive)
        # IMPORTANT: If multiple ACTIONs exist, take only the FIRST one
        if "ACTION" in response_upper:
            # Find the FIRST occurrence of "ACTION" in the original text
            # Search for "ACTION:" case-insensitively
            idx_upper = response_upper.find("ACTION")

            # Find the colon after "ACTION"
            colon_search_start = idx_upper
            colon_idx = response_text.find(":", colon_search_start)

            if colon_idx != -1:
                # Get everything after the colon until next newline
                action_section = response_text[colon_idx+1:]
                action_line = action_section.split("\n")[0].strip()

                # Remove any trailing garbage or second action
                for marker in ["thought", "assistant", "action"]:
                    if marker in action_line.lower():
                        # Only split if this is a DIFFERENT word, not part of the tool name
                        marker_pos = action_line.lower().find(marker)
                        # Check if marker is at word boundary (after space or at start)
                        if marker_pos == 0 or action_line[marker_pos-1] in " \n":
                            action_line = action_line[:marker_pos].strip()

                # Count how many ACTION lines were in the response
                action_count = sum(1 for line in response_text.split("\n") if "ACTION:" in line.upper())
                if action_count > 1:
                    print(f"    [Note: Found {action_count} actions, using only the first one]")

                return action_line, False

        # PRIORITY 3: Look for THOUGHT
        if "THOUGHT" in response_upper:
            idx = response_upper.find("THOUGHT")
            colon_idx = response_text.find(":", idx)
            if colon_idx != -1:
                thought = response_text[colon_idx+1:].split("\n")[0].strip()
                return thought, False

        # Default: empty response
        return "", False

    def parse_tool_call(self, action_string: str) -> tuple[str, dict]:
        """Parse tool calls - case-insensitive, handles Mistral variations"""
        try:
            action_string = action_string.strip()

            # Must have parentheses
            if "(" not in action_string or ")" not in action_string:
                return "", {}

            # Extract tool name and parameters
            tool_part = action_string.split("(")[0].strip()
            params_part = action_string.split("(", 1)[1].rsplit(")", 1)[0].strip()

            # Get first word as tool name
            tool_name = tool_part.split()[0] if tool_part else ""
            # Convert to lowercase for comparison
            tool_name_lower = tool_name.lower()

            # Validate tool name (case-insensitive)
            valid_tools = [
                "search_product", "check_product_details", "check_order_status",
                "get_return_policy", "search_faq", "process_refund", "escalate_to_human"
            ]
            if tool_name_lower not in valid_tools:
                return "", {}

            # Use the correct lowercase tool name
            tool_name = tool_name_lower

            # Parse parameters
            params = {}
            if params_part:
                # Try to parse as key=value pairs
                if "=" in params_part:
                    for item in params_part.split(","):
                        if "=" in item:
                            k, v = item.split("=", 1)
                            params[k.strip()] = v.strip().strip("'\"")
                else:
                    # Just a value - map based on tool
                    val = params_part.strip().strip("'\"")
                    if tool_name == "search_product":
                        params["product_name"] = val
                    elif tool_name == "search_faq":
                        params["topic"] = val
                    elif tool_name in ["escalate_to_human", "process_refund"]:
                        params["reason"] = val

            return tool_name, params

        except Exception as e:
            return "", {}

    def solve_customer_issue(self, customer_message: str) -> str:
        """Use ReAct to solve a customer's issue"""
        print(f"\n{'='*70}")
        print(f"CUSTOMER: {customer_message}")
        print(f"{'='*70}\n")

        # Add customer message to conversation
        self.conversation_history.append({
            "role": "user",
            "content": customer_message
        })

        iteration = 0
        max_iterations = 10

        while iteration < max_iterations:
            iteration += 1

            # Get Model's response
            try:
                if USE_LOCAL_MODEL:
                    # Use OllamaClient.messages_create
                    response = client.messages_create(
                        system=self.get_system_prompt(),
                        messages=self.conversation_history,
                        max_tokens=1000
                    )
                else:
                    # Use Anthropic client.messages.create
                    response = client.messages.create(
                        model=self.model,
                        max_tokens=1000,
                        system=self.get_system_prompt(),
                        messages=self.conversation_history
                    )

                assistant_message = response.content[0].text
            except Exception as e:
                print(f"❌ LLM Error: {e}")
                print("   Check: Is Ollama running? Run: /Users/gaurav/Documents/Ollama/restart_ollama.sh")
                return f"Error: {str(e)}"

            # Print the response (shows thinking)
            print(f"[Iteration {iteration}]")
            print(assistant_message)
            print()

            # Check if this is the final answer
            content, is_final = self.process_response(assistant_message)

            if is_final:
                # We have the final answer
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                print(f"\n{'='*70}")
                print(f"FINAL RESPONSE FROM AGENT:")
                print(f"{'='*70}")
                print(content)
                return content

            # Extract and execute the tool call
            tool_name, tool_params = self.parse_tool_call(content)

            if tool_name and tool_name in [
                "search_product", "check_product_details", "check_order_status",
                "get_return_policy", "search_faq", "process_refund", "escalate_to_human"
            ]:
                # ===================================================================
                # STEP 1: Add assistant's action (THOUGHT + ACTION) to history
                # ===================================================================
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })

                # ===================================================================
                # STEP 2: Execute the tool and get OBSERVATION
                # ===================================================================
                print(f"→ Executing tool: {tool_name}({tool_params})")
                tool_result = execute_tool(tool_name, tool_params)
                print(f"✓ Tool result: {tool_result}\n")

                # ===================================================================
                # STEP 3: Add OBSERVATION to conversation history
                # This is the critical step - the model will reason about this
                # ===================================================================
                observation = f"OBSERVATION: {tool_result}"
                self.conversation_history.append({
                    "role": "user",
                    "content": observation
                })

                print(f"[Observation added to context]\n")

                # ===================================================================
                # STEP 4: Loop back - let model reason about the observation
                # The model will see the observation and decide:
                #   - Take another ACTION (if more info needed)
                #   - Provide FINAL ANSWER (if question is answered)
                # This is the REASONING LOOP of ReAct
                # ===================================================================
                # Loop continues here - no return statement
                # The next iteration will call the model with the observation
            else:
                # Tool call was invalid, ask Mistral to use proper tools
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                self.conversation_history.append({
                    "role": "user",
                    "content": "Please use one of the available tools to answer this question. Valid tools: search_product(product_name=TEXT), check_product_details(product_id=TEXT), check_order_status(order_id=TEXT), get_return_policy(), search_faq(topic=TEXT), process_refund(order_id=TEXT,reason=TEXT), escalate_to_human(reason=TEXT)"
                })

        return "Max iterations reached. Please escalate to human support."


# ============================================================================
# MAIN - Test the agent
# ============================================================================

def main():
    """Run the ReAct agent - interactive chat"""
    agent = ReActEcommerceAgent()

    print("Welcome to E-Commerce Support Agent!")
    print("Type your questions. Type 'quit' to exit.\n")

    # Interactive loop - no automatic test queries
    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "quit":
            print("Goodbye!")
            break

        if not user_input:
            continue

        # Process the user's question
        agent.solve_customer_issue(user_input)
        print("\n")


if __name__ == "__main__":
    main()
