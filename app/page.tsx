'use client';

import { useState, useEffect, useCallback } from 'react';

interface Script {
  id: string;
  content: string;
}

interface ImageItem {
  id: string;
  prompt: string;
  path: string;
  order: number;
}

interface Audio {
  id: string;
  path: string;
  duration: number | null;
}

interface Video {
  id: string;
  path: string;
  duration: number | null;
}

interface VideoProject {
  id: string;
  topic: string;
  status: string;
  error: string | null;
  currentStep: string | null;
  script: Script | null;
  images: ImageItem[];
  audio: Audio | null;
  video: Video | null;
}

type StepStatus = 'pending' | 'active' | 'completed' | 'error';

interface Step {
  id: string;
  title: string;
  description: string;
  status: StepStatus;
}

const STEPS_CONFIG = [
  { id: 'script', title: '스크립트 생성', description: 'Gemini가 주제에 맞는 대본을 작성합니다' },
  { id: 'images', title: '이미지 생성', description: '4장의 관련 이미지를 병렬로 생성합니다' },
  { id: 'tts', title: '음성 합성', description: 'Gemini TTS로 대본을 읽습니다' },
  { id: 'video', title: '영상 합성', description: 'FFmpeg로 부드러운 전환 효과와 함께 영상을 만듭니다' },
];

export default function Home() {
  const [topic, setTopic] = useState('');
  const [project, setProject] = useState<VideoProject | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<{ message: string; step: string } | null>(null);
  const [steps, setSteps] = useState<Step[]>(
    STEPS_CONFIG.map(s => ({ ...s, status: 'pending' as StepStatus }))
  );

  const updateStepStatus = useCallback((stepId: string, status: StepStatus) => {
    setSteps(prev =>
      prev.map(s => (s.id === stepId ? { ...s, status } : s))
    );
  }, []);

  const resetSteps = useCallback(() => {
    setSteps(STEPS_CONFIG.map(s => ({ ...s, status: 'pending' as StepStatus })));
  }, []);

  const pollProject = useCallback(async (projectId: string) => {
    try {
      const response = await fetch(`/api/projects/${projectId}`);
      if (!response.ok) return;

      const data: VideoProject = await response.json();
      setProject(data);

      // Update step statuses based on project state
      const newSteps = [...steps];

      // Script step
      if (data.script) {
        newSteps[0].status = 'completed';
      } else if (data.currentStep === 'script') {
        newSteps[0].status = data.status === 'failed' ? 'error' : 'active';
      }

      // Images step
      if ((data.images?.length || 0) >= 4) {
        newSteps[1].status = 'completed';
      } else if (data.currentStep === 'images') {
        newSteps[1].status = data.status === 'failed' ? 'error' : 'active';
      }

      // TTS step
      if (data.audio) {
        newSteps[2].status = 'completed';
      } else if (data.currentStep === 'tts') {
        newSteps[2].status = data.status === 'failed' ? 'error' : 'active';
      }

      // Video step
      if (data.video) {
        newSteps[3].status = 'completed';
      } else if (data.currentStep === 'video') {
        newSteps[3].status = data.status === 'failed' ? 'error' : 'active';
      }

      setSteps(newSteps);
    } catch {
      // Ignore polling errors
    }
  }, [steps]);

  const handleGenerate = async (skipSteps: string[] = []) => {
    if (!topic.trim() && !project) return;

    setIsGenerating(true);
    setError(null);

    try {
      let projectId = project?.id;

      // Create project if not exists
      if (!projectId) {
        resetSteps();
        const createResponse = await fetch('/api/projects', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ topic: topic.trim() }),
        });

        if (!createResponse.ok) {
          throw new Error('프로젝트 생성에 실패했습니다');
        }

        const newProject = await createResponse.json();
        projectId = newProject.id;
        setProject(newProject);
      }

      // Start generation
      const generateResponse = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ projectId, skipSteps }),
      });

      // Poll for updates while generating
      const pollInterval = setInterval(() => pollProject(projectId!), 2000);

      const result = await generateResponse.json();

      clearInterval(pollInterval);

      if (!generateResponse.ok) {
        setError({ message: result.error, step: result.step || 'unknown' });

        // Update the failed step status
        if (result.step) {
          updateStepStatus(result.step, 'error');
        }

        // Fetch latest project state
        await pollProject(projectId!);
      } else {
        setProject(result);
        // Mark all steps as completed
        setSteps(STEPS_CONFIG.map(s => ({ ...s, status: 'completed' as StepStatus })));
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다';
      setError({ message: errorMessage, step: 'unknown' });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRetry = () => {
    if (!project) return;

    // Get completed steps to skip
    const skipSteps: string[] = [];
    if (project.script) skipSteps.push('script');
    if ((project.images?.length || 0) >= 4) skipSteps.push('images');
    if (project.audio) skipSteps.push('tts');
    if (project.video) skipSteps.push('video');

    handleGenerate(skipSteps);
  };

  const handleNewProject = () => {
    setProject(null);
    setError(null);
    setTopic('');
    resetSteps();
  };

  const getStepIcon = (status: StepStatus) => {
    switch (status) {
      case 'completed':
        return '✓';
      case 'active':
        return '⟳';
      case 'error':
        return '✕';
      default:
        return '○';
    }
  };

  const getImageUrl = (path: string) => {
    // Convert storage path to public URL
    return '/' + path.replace('public/', '');
  };

  return (
    <div className="container">
      <header className="header">
        <h1>AI Video Generator</h1>
        <p>주제를 입력하면 자동으로 AI 영상을 생성합니다</p>
      </header>

      {!project || project.status === 'pending' ? (
        <div className="input-section">
          <input
            type="text"
            placeholder="영상 주제를 입력하세요 (예: 우주의 신비, 고양이의 일상)"
            value={topic}
            onChange={e => setTopic(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleGenerate()}
            disabled={isGenerating}
          />
          <button
            className="btn btn-primary"
            onClick={() => handleGenerate()}
            disabled={!topic.trim() || isGenerating}
          >
            {isGenerating ? (
              <>
                <span className="spinner" />
                생성 중...
              </>
            ) : (
              '영상 생성'
            )}
          </button>
        </div>
      ) : (
        <div className="input-section">
          <input type="text" value={project.topic} disabled />
          <button className="btn btn-primary" onClick={handleNewProject}>
            새 영상 만들기
          </button>
        </div>
      )}

      <section className="progress-section">
        <h3 className="progress-title">생성 단계</h3>
        <div className="steps">
          {steps.map(step => (
            <div key={step.id} className={`step step-${step.status}`}>
              <div className="step-icon">{getStepIcon(step.status)}</div>
              <div className="step-content">
                <div className="step-title">{step.title}</div>
                <div className="step-description">{step.description}</div>
              </div>
            </div>
          ))}
        </div>

        {error && (
          <div className="error-box">
            <h4>오류 발생</h4>
            <p>{error.message}</p>
            <button className="btn btn-retry" onClick={handleRetry}>
              재시도 (완료된 단계 건너뛰기)
            </button>
          </div>
        )}
      </section>

      {project && (project.script || (project.images?.length || 0) > 0 || project.audio || project.video) && (
        <section className="result-section">
          <h3 className="result-title">결과</h3>

          {project.script && (
            <div className="script-box">
              <h4>스크립트</h4>
              <p>{project.script.content}</p>
            </div>
          )}

          {(project.images?.length || 0) > 0 && (
            <>
              <h4 style={{ marginBottom: '1rem' }}>생성된 이미지 ({project.images?.length || 0}장)</h4>
              <div className="images-grid">
                {(project.images || []).map((img, idx) => (
                  <div key={img.id} className="image-card">
                    <img src={getImageUrl(img.path)} alt={`Image ${idx + 1}`} />
                    <p>{img.prompt.substring(0, 100)}...</p>
                  </div>
                ))}
              </div>
            </>
          )}

          {project.video && (
            <div className="video-container">
              <video controls autoPlay>
                <source src={getImageUrl(project.video.path)} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
              <div className="video-info">
                <span>Duration: {project.video.duration?.toFixed(1)}s</span>
                <a href={getImageUrl(project.video.path)} download>
                  다운로드
                </a>
              </div>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
