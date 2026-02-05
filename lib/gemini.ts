const GEMINI_API_KEY = process.env.GEMINI_API_KEY || '';
const GEMINI_API_BASE = 'https://generativelanguage.googleapis.com/v1beta';

export interface GeminiError {
  error: {
    code: number;
    message: string;
    status: string;
  };
}

export async function generateScript(topic: string): Promise<string> {
  const prompt = `Create a short, engaging video script (about 30-60 seconds when read aloud) about the topic: "${topic}".

The script should:
1. Have a hook at the beginning
2. Present 3-4 interesting facts or points
3. End with a memorable conclusion

Write ONLY the narration text, no scene descriptions or directions. Keep it conversational and easy to listen to.`;

  const response = await fetch(
    `${GEMINI_API_BASE}/models/gemini-2.0-flash:generateContent?key=${GEMINI_API_KEY}`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contents: [
          {
            parts: [{ text: prompt }],
          },
        ],
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 1024,
        },
      }),
    }
  );

  if (!response.ok) {
    const error = await response.json() as GeminiError;
    throw new Error(`Gemini API error: ${error.error?.message || response.statusText}`);
  }

  const data = await response.json();
  const text = data.candidates?.[0]?.content?.parts?.[0]?.text;

  if (!text) {
    throw new Error('No content generated from Gemini');
  }

  return text;
}

export async function generateImagePrompts(topic: string, count: number = 4): Promise<string[]> {
  const prompt = `For a video about "${topic}", create ${count} detailed image generation prompts.
Each prompt should describe a visually striking scene related to the topic.
Make each prompt vivid and specific for AI image generation.

Return ONLY the prompts, one per line, numbered 1-${count}. No other text.`;

  const response = await fetch(
    `${GEMINI_API_BASE}/models/gemini-2.0-flash:generateContent?key=${GEMINI_API_KEY}`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contents: [
          {
            parts: [{ text: prompt }],
          },
        ],
        generationConfig: {
          temperature: 0.8,
          maxOutputTokens: 1024,
        },
      }),
    }
  );

  if (!response.ok) {
    const error = await response.json() as GeminiError;
    throw new Error(`Gemini API error: ${error.error?.message || response.statusText}`);
  }

  const data = await response.json();
  const text = data.candidates?.[0]?.content?.parts?.[0]?.text;

  if (!text) {
    throw new Error('No content generated from Gemini');
  }

  // Parse numbered prompts
  const prompts = text
    .split('\n')
    .filter((line: string) => line.trim())
    .map((line: string) => line.replace(/^\d+[\.\)]\s*/, '').trim())
    .filter((line: string) => line.length > 0)
    .slice(0, count);

  if (prompts.length < count) {
    throw new Error(`Only generated ${prompts.length} prompts, expected ${count}`);
  }

  return prompts;
}

export async function generateTTS(text: string, outputPath: string): Promise<{ duration: number }> {
  // Using Gemini's TTS API
  const response = await fetch(
    `${GEMINI_API_BASE}/models/gemini-2.5-flash-preview-tts:generateContent?key=${GEMINI_API_KEY}`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contents: [
          {
            parts: [{ text }],
          },
        ],
        generationConfig: {
          responseModalities: ['AUDIO'],
          speechConfig: {
            voiceConfig: {
              prebuiltVoiceConfig: {
                voiceName: 'Kore',
              },
            },
          },
        },
      }),
    }
  );

  if (!response.ok) {
    const error = await response.json() as GeminiError;
    throw new Error(`Gemini TTS API error: ${error.error?.message || response.statusText}`);
  }

  const data = await response.json();
  const audioData = data.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;

  if (!audioData) {
    throw new Error('No audio generated from Gemini TTS');
  }

  // Write audio file
  const fs = await import('fs/promises');
  const audioBuffer = Buffer.from(audioData, 'base64');
  await fs.writeFile(outputPath, audioBuffer);

  // Estimate duration based on text length (rough estimate: 150 words per minute)
  const wordCount = text.split(/\s+/).length;
  const duration = (wordCount / 150) * 60;

  return { duration };
}
