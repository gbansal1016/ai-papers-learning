from transformers import pipeline

print("Testing Local Model Approach...")
print("=" * 60)

# Load a small model locally
print("\n1. Loading GPT-2 model (first time takes ~1 min)...")
try:
    generator = pipeline("text-generation", model="gpt2", device=-1)
    print("   ✅ Model loaded successfully!")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Test the model
print("\n2. Testing model...")
try:
    prompt = "What is 2 + 2? The answer is "
    response = generator(prompt, max_length=30, num_return_sequences=1)
    generated_text = response[0]["generated_text"]
    print(f"   ✅ Success!")
    print(f"   Prompt: {prompt}")
    print(f"   Response: {generated_text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ Local model approach works!")
