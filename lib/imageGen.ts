import * as fs from 'fs/promises';
import * as path from 'path';

const FAL_API_KEY = process.env.FAL_API_KEY || '';
const FAL_API_BASE = 'https://fal.run';

export interface ImageGenerationResult {
  path: string;
  prompt: string;
}

export async function generateImage(
  prompt: string,
  outputPath: string
): Promise<ImageGenerationResult> {
  // Using fal.ai's fast image generation model (similar to banana)
  const response = await fetch(
    `${FAL_API_BASE}/fal-ai/flux/schnell`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Key ${FAL_API_KEY}`,
      },
      body: JSON.stringify({
        prompt: prompt,
        image_size: 'landscape_16_9',
        num_inference_steps: 4,
        num_images: 1,
        enable_safety_checker: true,
      }),
    }
  );

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Image generation failed: ${errorText}`);
  }

  const data = await response.json();
  const imageUrl = data.images?.[0]?.url;

  if (!imageUrl) {
    throw new Error('No image URL in response');
  }

  // Download the image
  const imageResponse = await fetch(imageUrl);
  if (!imageResponse.ok) {
    throw new Error(`Failed to download generated image: ${imageResponse.statusText}`);
  }

  const imageBuffer = Buffer.from(await imageResponse.arrayBuffer());

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

  const results = await Promise.all(
    prompts.map(async (prompt, index) => {
      const outputPath = `${baseDir}/image_${index + 1}.png`;
      return generateImage(prompt, outputPath);
    })
  );

  return results;
}
