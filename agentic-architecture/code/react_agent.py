"""
Real ReAct Agent for E-Commerce Customer Support

This is a REAL agent that:
1. Uses Claude as the reasoning engine
2. Has actual tools that retrieve real data
3. Solves actual customer support problems
4. Shows transparent reasoning process

Domain: E-Commerce Customer Support

Requirements:
    pip install anthropic python-dotenv

Setup:
    1. Get your API key from https://console.anthropic.com
    2. Create a .env file with: ANTHROPIC_API_KEY=your_key_here
    3. Run: python real_ecommerce_support_agent.py
"""

import os
import json
from typing import Optional
from dataclasses import dataclass
from enum import Enum
from anthropic import Anthropic

# Initialize Anthropic client
client = Anthropic()

# ============================================================================
# SIMULATED DATABASE - In real system, these would be actual databases
# ============================================================================

PRODUCT_DATABASE = {
    "LAPTOP-001": {
        "name": "ProBook 15 Laptop",
        "price": 1299.99,
        "in_stock": True,
        "warranty": "2 years",
        "specs": "Intel i7, 16GB RAM, 512GB SSD, 15.6\" display"
    },
    "PHONE-001": {
        "name": "SmartPhone X",
        "price": 899.99,
        "in_stock": True,
        "warranty": "1 year",
        "specs": "6.5\" OLED, 128GB storage, 5G, excellent camera"
    },
    "HEADPHONES-001": {
        "name": "AudioMax Pro",
        "price": 199.99,
        "in_stock": False,
        "warranty": "1 year",
        "specs": "Noise cancelling, 30hr battery, Bluetooth 5.0"
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
    """Search for a product in the database"""
    matching_products = []
    for product_id, product in PRODUCT_DATABASE.items():
        if product_name.lower() in product["name"].lower():
            matching_products.append(f"{product_id}: {product['name']} - ${product['price']}")

    if matching_products:
        return f"Found products:\n" + "\n".join(matching_products)
    return f"No products found matching '{product_name}'"


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
# REACT AGENT - Uses Claude as the brain
# ============================================================================

class ReActEcommerceAgent:
    """Real ReAct Agent for E-Commerce Customer Support"""

    def __init__(self):
        self.conversation_history = []
        self.thought_action_log = []
        self.model = "claude-3-5-sonnet-20241022"

    def get_system_prompt(self) -> str:
        """System prompt that tells Claude how to be a support agent"""
        return """You are a helpful e-commerce customer support agent. Your job is to help customers with their questions about products, orders, returns, and general support.

You have access to these tools:
1. search_product(product_name) - Search for products in our catalog
2. check_product_details(product_id) - Get detailed info about a product
3. check_order_status(order_id) - Check status of a customer's order
4. get_return_policy() - Get our return policy
5. search_faq(topic) - Search FAQ for common questions
6. process_refund(order_id, reason) - Process a refund for an order
7. escalate_to_human(reason) - Escalate complex issues to a human agent

IMPORTANT: You must think out loud about what the customer is asking and what tools you need to use.

Format your response like this:

THOUGHT: [What are you thinking? What does the customer need? What tools should you use?]

ACTION: [Use the tool here - format as: tool_name(param1=value1, param2=value2)]

OBSERVATION: [I will provide the tool result]

THOUGHT: [Think about the result and next steps]

... repeat THOUGHT/ACTION/OBSERVATION until you have enough information to answer the customer ...

FINAL ANSWER: [Your helpful response to the customer]

Be friendly, thorough, and honest. If you don't have information, say so."""

    def process_response(self, response_text: str) -> tuple[str, bool]:
        """Parse Claude's response to extract thought/action/observation"""

        # Check if this is the final answer
        if "FINAL ANSWER:" in response_text:
            final_answer = response_text.split("FINAL ANSWER:")[-1].strip()
            return final_answer, True

        # Check if there's an action to execute
        if "ACTION:" in response_text:
            action_section = response_text.split("ACTION:")[-1].split("\n")[0].strip()
            return action_section, False

        # If no clear action, return the thought
        if "THOUGHT:" in response_text:
            thought = response_text.split("THOUGHT:")[-1].split("\n")[0].strip()
            return thought, False

        return response_text, False

    def parse_tool_call(self, action_string: str) -> tuple[str, dict]:
        """Parse tool call from action string like: search_product(product_name=laptop)"""
        try:
            # Extract tool name and parameters
            tool_name = action_string.split("(")[0].strip()
            params_str = action_string.split("(")[1].rstrip(")")

            # Parse parameters
            params = {}
            for param in params_str.split(","):
                if "=" in param:
                    key, value = param.split("=", 1)
                    params[key.strip()] = value.strip().strip("'\"")

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

            # Get Claude's response
            response = client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=self.get_system_prompt(),
                messages=self.conversation_history
            )

            assistant_message = response.content[0].text

            # Print the response (shows thinking)
            print(f"[Claude Iteration {iteration}]")
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
                # Execute the tool
                print(f"→ Executing tool: {tool_name}({tool_params})")
                tool_result = execute_tool(tool_name, tool_params)
                print(f"✓ Tool result: {tool_result}\n")

                # Add the assistant's message and tool result to conversation
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })

                self.conversation_history.append({
                    "role": "user",
                    "content": f"Tool result: {tool_result}\n\nContinue with THOUGHT/ACTION/OBSERVATION format or provide FINAL ANSWER."
                })
            else:
                # Claude didn't call a tool properly, ask it to use tools
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                self.conversation_history.append({
                    "role": "user",
                    "content": "Please use one of the available tools (search_product, check_product_details, check_order_status, get_return_policy, search_faq, process_refund, or escalate_to_human) to help answer this question."
                })

        return "Max iterations reached. Please escalate to human support."


# ============================================================================
# MAIN - Test the agent
# ============================================================================

def main():
    """Run the ReAct agent with test queries"""
    agent = ReActEcommerceAgent()

    # Test customer queries
    test_queries = [
        "I want to buy a laptop but I'm not sure which one. What do you recommend?",
        "I ordered a phone (order ID: ORD-12346) but haven't received it yet. Where is it?",
        "I'm not happy with my monitor purchase. Can I return it? What's your return policy?"
    ]

    for query in test_queries:
        agent.solve_customer_issue(query)
        print("\n\n")

        # Ask if user wants to continue
        user_input = input("Enter your question (or 'quit' to exit): ").strip()
        if user_input.lower() == "quit":
            break
        if user_input:
            agent.solve_customer_issue(user_input)
            print("\n\n")


if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("Please set your API key: export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)

    main()
