import React, { useRef, useState } from 'react';

interface RecorderProps {
  onRecordingComplete: (blob: Blob) => void;
}

const Recorder: React.FC<RecorderProps> = ({ onRecordingComplete }) => {
  const [recording, setRecording] = useState(false);
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder.current = new MediaRecorder(stream);
    audioChunks.current = [];

    mediaRecorder.current.ondataavailable = (event) => {
      audioChunks.current.push(event.data);
    };

    mediaRecorder.current.onstop = () => {
      const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
      onRecordingComplete(audioBlob);
    };

    mediaRecorder.current.start();
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorder.current?.stop();
    setRecording(false);
  };

  return (
    <div className="flex items-center gap-4">
      {!recording ? (
        <button onClick={startRecording} className="bg-blue-500 text-white px-4 py-2 rounded">Start</button>
      ) : (
        <button onClick={stopRecording} className="bg-red-500 text-white px-4 py-2 rounded">Stop</button>
      )}
    </div>
  );
};

export default Recorder;

