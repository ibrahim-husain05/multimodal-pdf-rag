from ollama import chat

response = chat(
    model="qwen2.5vl:3b",
    messages=[
        {
            "role": "user",
            "content": (
                "Describe this image accurately. "
                "If it contains a table, extract its contents."
            ),
            "images": ["extracted_images/table-3-1.jpg"],
        }
    ],
)

print(response.message.content)