import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs/promises';
import * as path from 'path';

const execAsync = promisify(exec);

export interface VideoCompositionOptions {
  imagePaths: string[];
  audioPath: string;
  outputPath: string;
  transitionDuration?: number;  // seconds
}

export async function getAudioDuration(audioPath: string): Promise<number> {
  try {
    const { stdout } = await execAsync(
      `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${audioPath}"`
    );
    return parseFloat(stdout.trim()) || 30;
  } catch {
    // Default duration if ffprobe fails
    return 30;
  }
}

export async function composeVideo(options: VideoCompositionOptions): Promise<{ duration: number }> {
  const {
    imagePaths,
    audioPath,
    outputPath,
    transitionDuration = 0.5,
  } = options;

  // Ensure output directory exists
  await fs.mkdir(path.dirname(outputPath), { recursive: true });

  // Get audio duration
  const audioDuration = await getAudioDuration(audioPath);

  // Calculate display time for each image
  const imageCount = imagePaths.length;
  const totalTransitionTime = transitionDuration * (imageCount - 1);
  const imageDisplayTime = (audioDuration - totalTransitionTime) / imageCount;

  // Create a temporary file list for concat
  const tempDir = path.dirname(outputPath);
  const tempListPath = path.join(tempDir, 'filelist.txt');

  // Build complex filter for crossfade transitions
  // Each image needs to be scaled and padded to same size, then crossfaded
  const filterParts: string[] = [];
  const inputParts: string[] = [];

  // Add inputs for each image
  for (let i = 0; i < imagePaths.length; i++) {
    inputParts.push(`-loop 1 -t ${imageDisplayTime + (i < imagePaths.length - 1 ? transitionDuration : 0)} -i "${imagePaths[i]}"`);
  }

  // Build filter complex for smooth crossfade transitions
  // First, scale and pad all inputs
  for (let i = 0; i < imagePaths.length; i++) {
    filterParts.push(`[${i}:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v${i}]`);
  }

  // Apply crossfade transitions
  let lastOutput = 'v0';
  for (let i = 1; i < imagePaths.length; i++) {
    const offset = (imageDisplayTime * i) - (transitionDuration * (i - 1));
    const nextOutput = i === imagePaths.length - 1 ? 'vout' : `vt${i}`;
    filterParts.push(
      `[${lastOutput}][v${i}]xfade=transition=fade:duration=${transitionDuration}:offset=${offset.toFixed(2)}[${nextOutput}]`
    );
    lastOutput = nextOutput;
  }

  const filterComplex = filterParts.join('; ');

  // Build FFmpeg command
  const ffmpegCommand = [
    'ffmpeg -y',
    inputParts.join(' '),
    `-i "${audioPath}"`,
    `-filter_complex "${filterComplex}"`,
    '-map "[vout]"',
    `-map ${imagePaths.length}:a`,
    '-c:v libx264 -preset fast -crf 23',
    '-c:a aac -b:a 192k',
    '-shortest',
    `"${outputPath}"`,
  ].join(' ');

  try {
    await execAsync(ffmpegCommand, { maxBuffer: 50 * 1024 * 1024 });
  } catch (error: unknown) {
    const execError = error as { stderr?: string; message?: string };
    throw new Error(`FFmpeg error: ${execError.stderr || execError.message}`);
  }

  // Clean up temp file if exists
  try {
    await fs.unlink(tempListPath);
  } catch {
    // Ignore if file doesn't exist
  }

  return { duration: audioDuration };
}

export async function checkFFmpegInstalled(): Promise<boolean> {
  try {
    await execAsync('ffmpeg -version');
    return true;
  } catch {
    return false;
  }
}
