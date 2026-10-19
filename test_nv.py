import openai
import httpx
client = openai.OpenAI(
    api_key='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',
    base_url='https://integrate.api.nvidia.com/v1',
    timeout=httpx.Timeout(45.0, connect=10.0, read=45.0, write=10.0)
)
prompt = """
You are an expert video editor and audio engineer.
I will give you a chunk of subtitles. You must assign ONE appropriate background emotion/sound effect category to each subtitle.
If no sound is appropriate, assign the category 'none'.

The available sounds/categories are: angry, shock, none.
These may include emotions (like 'sad', 'angry') or sound effects (like 'camera transition', 'pop', 'boom'). Use them frequently to match the context.
IMPORTANT: You should assign a sound to about 1 out of every 2 or 3 lines to maintain a high-energy, engaging atmosphere. Do NOT leave too many lines as 'none'.
CRITICAL RULE: You MUST assign a category to the very first subtitle (index 0) to start the video with high energy! After that, keep the energy up by assigning sounds frequently.

Respond ONLY with a JSON object mapping the index (as a string) to the category.
Example: {"0": "angry", "2": "none", "3": "wealth"}

Subtitles:
[0] I am so angry right now!
[1] Just kidding, I am actually laughing.
[2] Wow, this is amazing!
[3] I'm so sad it's over.
"""
print('Sending complex request to NVIDIA...')
try:
    response = client.chat.completions.create(
        model='meta/llama-3.2-11b-vision-instruct',
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.3,
        max_tokens=2048
    )
    print('SUCCESS:', response.choices[0].message.content)
except Exception as e:
    print('ERROR:', e)
