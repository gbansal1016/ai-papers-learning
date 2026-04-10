import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
token = os.getenv('HUGGINGFACE_API_KEY')

print("Testing different HuggingFace API approaches...\n")

client = InferenceClient(api_key=token)

# Approach 1: Using text_generation with better error handling
print("1. Testing text_generation()...")
try:
    response = client.text_generation(
        "2 + 2 = ",
        max_new_tokens=10,
        model="gpt2"  # Simpler model
    )
    print(f"   ✅ Success: {response}")
except StopIteration:
    print("   ❌ StopIteration error")
except Exception as e:
    print(f"   ❌ Error: {type(e).__name__}: {e}")

# Approach 2: Using with_details parameter
print("\n2. Testing with details=True...")
try:
    response = client.text_generation(
        "2 + 2 = ",
        max_new_tokens=10,
        details=False,
        model="gpt2"
    )
    print(f"   ✅ Success: {response}")
except Exception as e:
    print(f"   ❌ Error: {type(e).__name__}: {e}")

# Approach 3: Using a different endpoint
print("\n3. Testing simple_hf_inference...")
try:
    response = client.text_generation(
        "What is 2+2?",
        max_new_tokens=20,
        temperature=0.1,
        model="gpt2"
    )
    print(f"   ✅ Success: {response}")
except Exception as e:
    print(f"   ❌ Error: {type(e).__name__}: {e}")

print("\n✅ Testing complete!")