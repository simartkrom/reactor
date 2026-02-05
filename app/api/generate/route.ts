import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { generateScript, generateImagePrompts, generateTTS } from '@/lib/gemini';
import { generateImagesParallel } from '@/lib/imageGen';
import { composeVideo, checkFFmpegInstalled } from '@/lib/ffmpeg';

export const maxDuration = 300; // 5 minutes timeout

interface GenerateRequest {
  projectId: string;
  skipSteps?: string[]; // Steps to skip for retry
}

type Step = 'script' | 'images' | 'tts' | 'video';

async function updateProjectStep(projectId: string, step: string, status: string = 'generating', error?: string) {
  await prisma.videoProject.update({
    where: { id: projectId },
    data: {
      currentStep: step,
      status,
      error,
    },
  });
}

export async function POST(request: NextRequest) {
  try {
    const { projectId, skipSteps = [] }: GenerateRequest = await request.json();

    if (!projectId) {
      return NextResponse.json(
        { error: 'Project ID is required' },
        { status: 400 }
      );
    }

    // Check FFmpeg installation
    const ffmpegInstalled = await checkFFmpegInstalled();
    if (!ffmpegInstalled) {
      return NextResponse.json(
        { error: 'FFmpeg is not installed on the server' },
        { status: 500 }
      );
    }

    // Get project
    const project = await prisma.videoProject.findUnique({
      where: { id: projectId },
      include: {
        script: true,
        images: { orderBy: { order: 'asc' } },
        audio: true,
        video: true,
      },
    });

    if (!project) {
      return NextResponse.json(
        { error: 'Project not found' },
        { status: 404 }
      );
    }

    const shouldSkip = (step: Step) => skipSteps.includes(step);

    // Step 1: Generate Script
    let scriptContent = project.script?.content;
    if (!scriptContent && !shouldSkip('script')) {
      try {
        await updateProjectStep(projectId, 'script');
        scriptContent = await generateScript(project.topic);

        await prisma.script.create({
          data: {
            projectId,
            content: scriptContent,
          },
        });
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        await updateProjectStep(projectId, 'script', 'failed', `Script generation failed: ${errorMessage}`);
        return NextResponse.json(
          { error: `Script generation failed: ${errorMessage}`, step: 'script' },
          { status: 500 }
        );
      }
    } else if (project.script?.content) {
      scriptContent = project.script.content;
    }

    if (!scriptContent) {
      return NextResponse.json(
        { error: 'Script is required to continue', step: 'script' },
        { status: 400 }
      );
    }

    // Step 2: Generate Images (Parallel)
    let imagePaths = project.images.map(img => img.path);
    if (imagePaths.length < 4 && !shouldSkip('images')) {
      try {
        await updateProjectStep(projectId, 'images');

        // Generate prompts first
        const prompts = await generateImagePrompts(project.topic, 4);

        // Generate images in parallel
        const results = await generateImagesParallel(prompts, projectId);

        // Save to database
        await Promise.all(
          results.map((result, index) =>
            prisma.image.create({
              data: {
                projectId,
                prompt: result.prompt,
                path: result.path,
                order: index,
              },
            })
          )
        );

        imagePaths = results.map(r => r.path);
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        await updateProjectStep(projectId, 'images', 'failed', `Image generation failed: ${errorMessage}`);
        return NextResponse.json(
          { error: `Image generation failed: ${errorMessage}`, step: 'images' },
          { status: 500 }
        );
      }
    }

    if (imagePaths.length < 4) {
      return NextResponse.json(
        { error: 'At least 4 images are required to continue', step: 'images' },
        { status: 400 }
      );
    }

    // Step 3: Generate TTS Audio
    let audioPath = project.audio?.path;
    if (!audioPath && !shouldSkip('tts')) {
      try {
        await updateProjectStep(projectId, 'tts');

        const outputPath = `public/storage/audio/${projectId}/narration.wav`;
        const { duration } = await generateTTS(scriptContent, outputPath);

        await prisma.audio.create({
          data: {
            projectId,
            path: outputPath,
            duration,
          },
        });

        audioPath = outputPath;
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        await updateProjectStep(projectId, 'tts', 'failed', `TTS generation failed: ${errorMessage}`);
        return NextResponse.json(
          { error: `TTS generation failed: ${errorMessage}`, step: 'tts' },
          { status: 500 }
        );
      }
    }

    if (!audioPath) {
      return NextResponse.json(
        { error: 'Audio is required to continue', step: 'tts' },
        { status: 400 }
      );
    }

    // Step 4: Compose Video with FFmpeg
    let videoPath = project.video?.path;
    if (!videoPath && !shouldSkip('video')) {
      try {
        await updateProjectStep(projectId, 'video');

        const outputPath = `public/storage/videos/${projectId}/final.mp4`;
        const { duration } = await composeVideo({
          imagePaths,
          audioPath,
          outputPath,
          transitionDuration: 0.5,
        });

        await prisma.video.create({
          data: {
            projectId,
            path: outputPath,
            duration,
          },
        });

        videoPath = outputPath;
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        await updateProjectStep(projectId, 'video', 'failed', `Video composition failed: ${errorMessage}`);
        return NextResponse.json(
          { error: `Video composition failed: ${errorMessage}`, step: 'video' },
          { status: 500 }
        );
      }
    }

    // Mark as completed
    await updateProjectStep(projectId, 'completed', 'completed');

    // Fetch final project state
    const finalProject = await prisma.videoProject.findUnique({
      where: { id: projectId },
      include: {
        script: true,
        images: { orderBy: { order: 'asc' } },
        audio: true,
        video: true,
      },
    });

    return NextResponse.json(finalProject);
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json(
      { error: `Generation failed: ${errorMessage}` },
      { status: 500 }
    );
  }
}
