import * as fs from 'fs/promises';
import * as path from 'path';

const GEMINI_API_KEY = process.env.GEMINI_API_KEY || '';
const GEMINI_API_BASE = 'https://generativelanguage.googleapis.com/v1beta';

export interface ImageGenerationResult {
  path: string;
  prompt: string;
}

export async function generateImage(
  prompt: string,
  outputPath: string
): Promise<ImageGenerationResult> {
  // Using Gemini Imagen 3 for image generation
  const response = await fetch(
    `${GEMINI_API_BASE}/models/imagen-3.0-generate-002:predict?key=${GEMINI_API_KEY}`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        instances: [
          {
            prompt: prompt,
          },
        ],
        parameters: {
          sampleCount: 1,
          aspectRatio: '16:9',
          safetyFilterLevel: 'block_few',
        },
      }),
    }
  );

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Image generation failed: ${errorText}`);
  }

  const data = await response.json();
  const imageData = data.predictions?.[0]?.bytesBase64Encoded;

  if (!imageData) {
    throw new Error('No image data in response');
  }

  // Decode base64 and save
  const imageBuffer = Buffer.from(imageData, 'base64');

  // Ensure directory exists
  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  await fs.writeFile(outputPath, imageBuffer);

  return {
    path: outputPath,
    prompt,
  };
}

export async function generateImagesParallel(
  prompts: string[],
  projectId: string
): Promise<ImageGenerationResult[]> {
  const baseDir = `public/storage/images/${projectId}`;
  await fs.mkdir(baseDir, { recursive: true });

  // Generate all images in parallel
  const results = await Promise.all(
    prompts.map(async (prompt, index) => {
      const outputPath = `${baseDir}/image_${index + 1}.png`;
      return generateImage(prompt, outputPath);
    })
  );

  return results;
}
